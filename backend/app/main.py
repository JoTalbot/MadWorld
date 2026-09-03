"""FastAPI application entrypoint."""
from __future__ import annotations
import logging
from uuid import uuid4
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.contract_routes import router as contract_router
from app.api.crafting_routes import router as crafting_router
from app.api.damage_routes import router as damage_router
from app.api.economy_loop_routes import router as economy_loop_router
from app.api.economy_routes import router as economy_router
from app.api.expedition_routes import router as expedition_router
from app.api.gathering_routes import router as gathering_router
from app.api.market_routes import router as market_router
from app.api.market_cancel_routes import router as market_cancel_router
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
from app.api.phase9_warfare_routes import router as phase9_warfare_router
from app.api.phase9_warfare_extra_routes import router as phase9_warfare_extra_router
from app.api.phase10_finance_routes import router as phase10_finance_router
from app.api.repair_routes import router as repair_router
from app.api.routes import router as api_v1_router
from app.api.session_routes import router as session_router
from app.api.settlement_routes import router as settlement_router
from app.api.travel_routes import router as travel_router
from app.application.errors import ConcurrencyConflict, IdempotencyConflict, NotFound
from app.domain.primitives import DomainError
from app.security import AbuseScorer, ReplayGuard, SlidingWindowRateLimiter
logger=logging.getLogger("madworld.api")
app=FastAPI(title="MadWorld API",version="0.1.0")
for router in (api_v1_router,session_router,market_router,market_cancel_router,gathering_router,crafting_router,repair_router,damage_router,contract_router,expedition_router,settlement_router,economy_router,economy_loop_router,phase3_router,phase4_router,phase4_alliance_router,phase4_alliance_extra_router,phase4_wallet_router,phase4_asset_router,phase4_asset_provenance_router,phase4_completion_router,phase5_territory_router,phase6_world_router,phase7_economy_router,phase8_faction_router,phase9_warfare_router,phase9_warfare_extra_router,phase10_finance_router):
    app.include_router(router)
app.include_router(travel_router)
_rate_limiter=SlidingWindowRateLimiter(limit=120,window_seconds=60)
_replay_guard=ReplayGuard(ttl_seconds=300,max_entries=10000)
_abuse_scorer=AbuseScorer(decay_seconds=300,threshold=100)
@app.middleware("http")
async def request_id_middleware(request:Request,call_next):
    request_id=request.headers.get("X-Request-ID") or str(uuid4()); request.state.request_id=request_id
    client=(request.client.host if request.client else "unknown")
    decision=_rate_limiter.check(client)
    if not decision.allowed:
        _abuse_scorer.add(client,5)
        response=_error_response(request,429,"RATE_LIMITED","request rate limit exceeded",{"retry_after":decision.retry_after})
        response.headers["Retry-After"]=str(decision.retry_after); response.headers["X-RateLimit-Remaining"]="0"; response.headers["X-Request-ID"]=request_id; return response
    if request.method in {"POST","PUT","PATCH","DELETE"} and request.url.path.startswith("/api/v1/"):
        replay_id=request.headers.get("X-Request-ID")
        if replay_id and not _replay_guard.check_and_remember(f"{request.method}:{request.url.path}:{client}:{replay_id}"):
            _abuse_scorer.add(client,20)
            response=_error_response(request,409,"REPLAY_DETECTED","duplicate request identifier for mutation")
            response.headers["X-Request-ID"]=request_id; return response
    if request.method=="POST" and request.url.path.startswith("/api/v1/vehicles/") and request.url.path.endswith("/repair"):
        response=JSONResponse(status_code=410,content={"code":"LEGACY_API_GONE","message":"The direct vehicle repair endpoint has been retired. Use POST /api/v1/vehicles/{vehicle_id}/repair-job with inventory_id and amount.","request_id":request_id,"details":{"replacement":"/api/v1/vehicles/{vehicle_id}/repair-job","migration":"vehicle-repair-v2"}},headers={"Deprecation":"true","Sunset":"Wed, 30 Sep 2026 00:00:00 GMT","X-MadWorld-Migration":"vehicle-repair-v2"}); response.headers["X-Request-ID"]=request_id; return response
    response=await call_next(request); response.headers["X-Request-ID"]=request_id; response.headers["X-Content-Type-Options"]="nosniff"; response.headers["X-Frame-Options"]="DENY"; response.headers["Referrer-Policy"]="no-referrer"; response.headers["X-RateLimit-Remaining"]=str(decision.remaining)
    if response.status_code in {401,403,409,429}: _abuse_scorer.add(client,1 if response.status_code in {401,403} else 2)
    return response
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
def ready():
    """Real readiness probe: verifies PostgreSQL connectivity and that the
    authoritative schema has been migrated (schema_migrations present)."""
    from sqlalchemy import text
    from app.infrastructure.db import create_engine_from_env
    engine = create_engine_from_env()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            migrations = conn.execute(text("SELECT COUNT(*) FROM schema_migrations")).scalar()
        return {"status":"ok","service":"madworld-api","database":"ok","migrations_applied":int(migrations)}
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(status_code=503,content={"status":"degraded","service":"madworld-api","database":"error","error":str(exc)[:200]})
    finally:
        engine.dispose()
@app.get("/api/v1/world")
def world()->dict:
    return {"season":1,"tick":0,"regions":[{"id":"dust_basin","name":"Dust Basin","security":"lawless"},{"id":"iron_ruins","name":"Iron Ruins","security":"contested"},{"id":"salt_coast","name":"Salt Coast","security":"frontier"}]}
