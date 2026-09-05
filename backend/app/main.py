"""FastAPI application entrypoint."""
from __future__ import annotations

import logging
import os
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse

from app.api.contract_routes import router as contract_router
from app.api.crafting_routes import router as crafting_router
from app.api.damage_routes import router as damage_router
from app.api.economy_loop_routes import router as economy_loop_router
from app.api.economy_routes import router as economy_router
from app.api.expedition_routes import router as expedition_router
from app.api.gathering_routes import router as gathering_router
from app.api.market_cancel_routes import router as market_cancel_router
from app.api.market_routes import router as market_router
from app.api.phase3_routes import router as phase3_router
from app.api.phase4_alliance_extra_routes import router as phase4_alliance_extra_router
from app.api.phase4_alliance_routes import router as phase4_alliance_router
from app.api.phase4_asset_provenance_routes import router as phase4_asset_provenance_router
from app.api.phase4_asset_routes import router as phase4_asset_router
from app.api.phase4_completion_routes import router as phase4_completion_router
from app.api.phase4_routes import router as phase4_router
from app.api.phase4_wallet_routes import router as phase4_wallet_router
from app.api.phase5_territory_routes import router as phase5_territory_router
from app.api.phase6_world_routes import router as phase6_world_router
from app.api.phase7_economy_routes import router as phase7_economy_router
from app.api.phase8_faction_routes import router as phase8_faction_router
from app.api.phase9_warfare_extra_routes import router as phase9_warfare_extra_router
from app.api.phase9_warfare_routes import router as phase9_warfare_router
from app.api.phase10_finance_routes import router as phase10_finance_router
from app.api.repair_routes import router as repair_router
from app.api.routes import router as api_v1_router
from app.api.session_routes import router as session_router
from app.api.settlement_routes import router as settlement_router
from app.api.travel_routes import router as travel_router
from app.application.errors import ConcurrencyConflict, IdempotencyConflict, NotFound
from app.domain.primitives import DomainError
from app.infrastructure.abuse_controls import build_abuse_controls
from app.infrastructure.client_identity import identify
from app.infrastructure.metrics import ABUSE_EVENTS, HTTP_LATENCY, HTTP_REQUESTS, REGISTRY, gauge_line

logger=logging.getLogger("madworld.api")
app=FastAPI(title="MadWorld API",version="0.1.0")
for router in (api_v1_router,session_router,market_router,market_cancel_router,gathering_router,crafting_router,repair_router,damage_router,contract_router,expedition_router,settlement_router,economy_router,economy_loop_router,phase3_router,phase4_router,phase4_alliance_router,phase4_alliance_extra_router,phase4_wallet_router,phase4_asset_router,phase4_asset_provenance_router,phase4_completion_router,phase5_territory_router,phase6_world_router,phase7_economy_router,phase8_faction_router,phase9_warfare_router,phase9_warfare_extra_router,phase10_finance_router):
    app.include_router(router)
app.include_router(travel_router)
def _abuse_backend()->str:
    # Shared (PostgreSQL) controls whenever a database is configured so multi-replica
    # deployments enforce one policy; explicit override via MADWORLD_ABUSE_CONTROL_BACKEND.
    return os.getenv("MADWORLD_ABUSE_CONTROL_BACKEND") or ("postgres" if os.getenv("MADWORLD_DATABASE_URL") else "memory")
def _engine_factory():
    from app.api.dependencies import get_engine
    return get_engine()
_rate_limiter,_replay_guard,_abuse_scorer=build_abuse_controls(_abuse_backend(),_engine_factory,rate_limit=int(os.getenv("MADWORLD_RATE_LIMIT","120")),rate_window_seconds=60,replay_ttl_seconds=300,score_decay_seconds=300,score_threshold=100)
logger.info("abuse controls backend=%s",_abuse_backend())
@app.middleware("http")
async def request_id_middleware(request:Request,call_next):
    started=perf_counter()
    request_id=request.headers.get("X-Request-ID") or str(uuid4()); request.state.request_id=request_id
    identity=identify(request.client.host if request.client else None,request.headers.get("X-Forwarded-For"),request.headers.get("Authorization"))
    request.state.client_ip=identity.network; client=identity.network
    # Two independent budgets: per network origin and per session. Either one exhausted -> 429.
    decision=None
    for key in identity.keys:
        decision=_rate_limiter.check(key)
        if not decision.allowed:
            _abuse_scorer.add(client,5); ABUSE_EVENTS.inc("rate_limited")
            response=_error_response(request,429,"RATE_LIMITED","request rate limit exceeded",{"retry_after":decision.retry_after,"scope":key.split(":",1)[0]})
            response.headers["Retry-After"]=str(decision.retry_after); response.headers["X-RateLimit-Remaining"]="0"; response.headers["X-Request-ID"]=request_id
            _observe(request,429,started); return response
    if request.method in {"POST","PUT","PATCH","DELETE"} and request.url.path.startswith("/api/v1/"):
        replay_id=request.headers.get("X-Request-ID")
        if replay_id and not _replay_guard.check_and_remember(f"{request.method}:{request.url.path}:{client}:{replay_id}"):
            _abuse_scorer.add(client,20); ABUSE_EVENTS.inc("replay_detected")
            response=_error_response(request,409,"REPLAY_DETECTED","duplicate request identifier for mutation")
            response.headers["X-Request-ID"]=request_id; _observe(request,409,started); return response
    if request.method=="POST" and request.url.path.startswith("/api/v1/vehicles/") and request.url.path.endswith("/repair"):
        response=JSONResponse(status_code=410,content={"code":"LEGACY_API_GONE","message":"The direct vehicle repair endpoint has been retired. Use POST /api/v1/vehicles/{vehicle_id}/repair-job with inventory_id and amount.","request_id":request_id,"details":{"replacement":"/api/v1/vehicles/{vehicle_id}/repair-job","migration":"vehicle-repair-v2"}},headers={"Deprecation":"true","Sunset":"Wed, 30 Sep 2026 00:00:00 GMT","X-MadWorld-Migration":"vehicle-repair-v2"}); response.headers["X-Request-ID"]=request_id; _observe(request,410,started); return response
    response=await call_next(request); response.headers["X-Request-ID"]=request_id; response.headers["X-Content-Type-Options"]="nosniff"; response.headers["X-Frame-Options"]="DENY"; response.headers["Referrer-Policy"]="no-referrer"; response.headers["X-RateLimit-Remaining"]=str(decision.remaining if decision else _rate_limiter.limit)
    if response.status_code in {401,403,409,429}: _abuse_scorer.add(client,1 if response.status_code in {401,403} else 2); ABUSE_EVENTS.inc(f"http_{response.status_code}")
    _observe(request,response.status_code,started)
    return response
def _observe(request:Request,status_code:int,started:float)->None:
    route=request.scope.get("route"); path=getattr(route,"path",None) or ("/api/v1/<unmatched>" if request.url.path.startswith("/api/v1/") else request.url.path)
    HTTP_REQUESTS.inc(request.method,path,f"{status_code//100}xx"); HTTP_LATENCY.observe(perf_counter()-started)
def _error_response(request:Request,status_code:int,code:str,message:str,details:dict|None=None)->JSONResponse:
    return JSONResponse(status_code=status_code,content={"code":code,"message":message,"request_id":request.state.request_id,"details":details})
@app.exception_handler(NotFound)
async def not_found_handler(request:Request,exc:NotFound)->JSONResponse:return _error_response(request,404,"NOT_FOUND",str(exc))
@app.exception_handler(ConcurrencyConflict)
async def concurrency_handler(request:Request,exc:ConcurrencyConflict)->JSONResponse:return _error_response(request,409,"CONCURRENCY_CONFLICT",str(exc))
@app.exception_handler(IdempotencyConflict)
async def idempotency_handler(request:Request,exc:IdempotencyConflict)->JSONResponse:return _error_response(request,409,"IDEMPOTENCY_CONFLICT",str(exc))
@app.exception_handler(DomainError)
async def domain_error_handler(request:Request,exc:DomainError)->JSONResponse:return _error_response(request,400,"DOMAIN_ERROR",str(exc))
@app.exception_handler(PermissionError)
async def permission_handler(request:Request,exc:PermissionError)->JSONResponse:return _error_response(request,403,"FORBIDDEN",str(exc))
@app.exception_handler(ValueError)
async def value_error_handler(request:Request,exc:ValueError)->JSONResponse:return _error_response(request,400,"INVALID_ARGUMENT",str(exc))
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request:Request,exc:RequestValidationError)->JSONResponse:return _error_response(request,422,"VALIDATION_ERROR","request validation failed",{"errors":exc.errors()})
@app.get("/health")
def health()->dict[str,str]:return {"status":"ok","service":"madworld-api"}

@app.get("/health/ready")
def ready(max_tick_lag_seconds:int=int(os.getenv("MADWORLD_READY_MAX_TICK_LAG_SECONDS","900"))):
    """Readiness probe: PostgreSQL reachable, schema migrated, and the authoritative
    world tick has advanced recently (world worker alive). Tick lag beyond the
    threshold is reported as degraded but does NOT fail readiness, because API
    reads/writes remain correct while the world worker is being recovered."""
    from sqlalchemy import text

    from app.api.dependencies import get_engine
    from app.infrastructure.readiness import evaluate_readiness
    try:
        with get_engine().connect() as conn:
            report=evaluate_readiness(lambda q,p=None: conn.execute(text(q),p or {}),max_tick_lag_seconds=max_tick_lag_seconds)
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=503,content={"status":"unavailable","service":"madworld-api","database":"error","error":str(exc)[:200]})
    return JSONResponse(status_code=200,content={"service":"madworld-api",**report})
@app.get("/api/v1/world")
def world()->dict:
    """Authoritative world summary read from PostgreSQL (season/tick/regions).
    Falls back to the static seed regions with authoritative=false when no database is configured."""
    from sqlalchemy import text

    from app.api.dependencies import get_engine
    static={"season":1,"tick":0,"authoritative":False,"regions":[{"id":"dust_basin","name":"Dust Basin","security":"lawless"},{"id":"iron_ruins","name":"Iron Ruins","security":"contested"},{"id":"salt_coast","name":"Salt Coast","security":"frontier"}]}
    if not os.getenv("MADWORLD_DATABASE_URL"): return static
    try:
        with get_engine().connect() as conn:
            sim=conn.execute(text("SELECT season, tick FROM world_simulation_state WHERE id = 1")).mappings().first()
            regions=conn.execute(text("SELECT id, name, security FROM world_regions ORDER BY id")).mappings().all()
    except Exception:  # noqa: BLE001
        logger.exception("world summary unavailable; serving static seed"); return static
    return {"season":int(sim["season"]) if sim else 1,"tick":int(sim["tick"]) if sim else 0,"authoritative":sim is not None,"regions":[{"id":r["id"],"name":r["name"],"security":r["security"]} for r in regions] or static["regions"]}
@app.get("/metrics",response_class=PlainTextResponse,include_in_schema=False)
def metrics()->PlainTextResponse:
    return PlainTextResponse(REGISTRY.render(),media_type="text/plain; version=0.0.4; charset=utf-8")
def _shared_state_gauges():
    if not os.getenv("MADWORLD_DATABASE_URL"): return
    from sqlalchemy import text

    from app.api.dependencies import get_engine
    with get_engine().connect() as conn:
        row=conn.execute(text("SELECT tick, EXTRACT(EPOCH FROM (now() - last_tick_at)) AS lag FROM world_simulation_state WHERE id = 1")).mappings().first()
        if row: yield gauge_line("madworld_world_tick",float(row["tick"])); yield gauge_line("madworld_world_tick_lag_seconds",float(row["lag"]))
        for table in ("abuse_control_hits","abuse_control_replays","abuse_control_scores"):
            yield gauge_line("madworld_abuse_control_rows",float(conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar_one()),table=table)
REGISTRY.gauge_source(_shared_state_gauges)
