from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, clients, intakes, predictions, analyses, feedback, dashboard


@asynccontextmanager
async def lifespan(application: FastAPI):
    # Create tables on startup
    from app.database import engine, Base
    from app.models import (  # noqa: F401 — ensure all models are imported
        user, client, program, feature, intake_brief,
        prediction, analysis, feedback as fb_model, audit_log,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


def create_app() -> FastAPI:
    application = FastAPI(
        title="Prediction Tracker API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth.router, prefix="/api")
    application.include_router(clients.router, prefix="/api")
    application.include_router(intakes.router, prefix="/api")
    application.include_router(predictions.router, prefix="/api")
    application.include_router(analyses.router, prefix="/api")
    application.include_router(feedback.router, prefix="/api")
    application.include_router(dashboard.router, prefix="/api")

    @application.get("/api/health")
    async def health():
        return {"status": "ok"}

    return application


app = create_app()
