"""FastAPI application entrypoint."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.damage_routes import router as damage_router
from app.api.gathering_routes import router as gathering_router
from app.api.market_routes import router as market_router
from app.api.crafting_routes import router as crafting_router
from app.api.repair_routes import router as repair_router
from app.api.routes import router as api_v1_router
from app.api.session_routes import router as session_router
from app.application.errors import ConcurrencyConflict, IdempotencyConflict, NotFound
from app.domain.primitives import DomainError

app = FastAPI(title="MadWorld API", version="0.1.0")
app.include_router(api_v1_router)
app.include_router(session_router)
app.include_router(market_router)
app.include_router(gathering_router)
app.include_router(crafting_router)
app.include_router(repair_router)
app.include_router(damage_router)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def _error_response(request: Request, status_code: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"code": code, "message": message, "request_id": request.state.request_id, "details": details})


@app.exception_handler(NotFound)
async def not_found_handler(request: Request, exc: NotFound) -> JSONResponse: return _error_response(request, 404, "NOT_FOUND", str(exc))
@app.exception_handler(ConcurrencyConflict)
async def concurrency_handler(request: Request, exc: ConcurrencyConflict) -> JSONResponse: return _error_response(request, 409, "CONCURRENCY_CONFLICT", str(exc))
@app.exception_handler(IdempotencyConflict)
async def idempotency_handler(request: Request, exc: IdempotencyConflict) -> JSONResponse: return _error_response(request, 409, "IDEMPOTENCY_CONFLICT", str(exc))
@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse: return _error_response(request, 400, "DOMAIN_ERROR", str(exc))
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse: return _error_response(request, 400, "INVALID_ARGUMENT", str(exc))
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse: return _error_response(request, 422, "VALIDATION_ERROR", "request validation failed", {"errors": exc.errors()})


@app.get("/health")
def health() -> dict[str, str]: return {"status": "ok", "service": "madworld-api"}


@app.get("/api/v1/world")
def world() -> dict: return {"season": 1, "tick": 0, "regions": [{"id": "dust_basin", "name": "Dust Basin", "security": "lawless"}, {"id": "iron_ruins", "name": "Iron Ruins", "security": "contested"}, {"id": "salt_coast", "name": "Salt Coast", "security": "frontier"}]}
