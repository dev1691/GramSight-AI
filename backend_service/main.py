import os
import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend_service.database import engine, Base
from backend_service.routers.weather import router as weather_router
from backend_service.routers.market import router as market_router
from backend_service.routers.analytics import router as analytics_router
from backend_service.routers.orchestrator import router as orchestrator_router
from backend_service.routers.risk import router as risk_router
from backend_service.routers.ai import router as ai_router
from backend_service.routers.auth import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('backend')


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup tasks here. Avoid global blocking calls at import time.
    # Create tables in a thread to avoid blocking the event loop.
    try:
        await asyncio.to_thread(Base.metadata.create_all, bind=engine)
    except Exception:
        logger.exception('Could not create DB tables at startup')
    # TODO: integrate RDS Proxy and Secrets Manager for production credentials
    yield
    # Place any shutdown cleanup here


app = FastAPI(title='GramSight Backend', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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


@app.get('/health')
async def health():
    return {'status': 'ok'}


# AWS Lambda compatibility using Mangum. When running in Lambda, the handler
# variable can be used by the Lambda runtime. For containerized uvicorn runs
# this has no effect.
try:
    from mangum import Mangum

    handler = Mangum(app)
except Exception:
    handler = None
