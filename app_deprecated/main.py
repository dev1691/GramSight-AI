from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings

# Routers
from .modules.auth.routes import router as auth_router
from .modules.farmer.routes import router as farmer_router
from .modules.admin.routes import router as admin_router

settings = get_settings()

def create_app() -> FastAPI:
    app = FastAPI(title="GramSight AI Backend")

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(farmer_router, prefix="/farmer", tags=["farmer"])
    app.include_router(admin_router, prefix="/admin", tags=["admin"])

    # Health
    @app.get("/health", tags=["health"])
    async def health():
        return {"status": "ok"}

    return app


app = create_app()
