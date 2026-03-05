import os
import uuid as _uuid
import logging
import asyncio
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from backend_service.config import ALLOWED_ORIGINS
from backend_service.database import engine, Base
from backend_service.routers.weather import router as weather_router
from backend_service.routers.market import router as market_router
from backend_service.routers.analytics import router as analytics_router
from backend_service.routers.orchestrator import router as orchestrator_router
from backend_service.routers.risk import router as risk_router
from backend_service.routers.ai import router as ai_router
from backend_service.routers.auth import router as auth_router
from backend_service.routers.farmer import router as farmer_router
from backend_service.routers.demo import router as demo_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s [%(name)s] %(message)s',
)
logger = logging.getLogger('backend')


# --------------- Middleware: Request-ID + timing ---------------
class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get('X-Request-ID', str(_uuid.uuid4()))
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers['X-Request-ID'] = request_id
        logger.info(
            "method=%s path=%s status=%s duration_ms=%.1f request_id=%s",
            request.method, request.url.path, response.status_code, elapsed_ms, request_id,
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await asyncio.to_thread(Base.metadata.create_all, bind=engine)
    except Exception:
        logger.exception('Could not create DB tables at startup')
    yield


app = FastAPI(title='GramSight Backend', lifespan=lifespan)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(weather_router)
app.include_router(market_router)
app.include_router(analytics_router)
app.include_router(orchestrator_router)
app.include_router(risk_router)
app.include_router(ai_router)
app.include_router(auth_router)
app.include_router(farmer_router)
app.include_router(demo_router)


@app.get('/health')
async def health():
    """Deep health check: verifies DB and Redis connectivity."""
    checks = {'db': 'ok', 'redis': 'ok'}
    try:
        from sqlalchemy import text
        await asyncio.to_thread(lambda: engine.connect().execute(text('SELECT 1')))
    except Exception as exc:
        checks['db'] = str(exc)
    try:
        from backend_service.cache import _get_sync
        _get_sync().ping()
    except Exception as exc:
        checks['redis'] = str(exc)

    ok = checks['db'] == 'ok' and checks['redis'] == 'ok'
    return {'status': 'ok' if ok else 'degraded', 'checks': checks}


# AWS Lambda compatibility using Mangum. When running in Lambda, the handler
# variable can be used by the Lambda runtime. For containerized uvicorn runs
# this has no effect.
try:
    from mangum import Mangum

    handler = Mangum(app)
except Exception:
    handler = None
