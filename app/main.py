from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, clients, intakes, predictions, analyses, feedback, dashboard


def create_app() -> FastAPI:
    application = FastAPI(
        title="Prediction Tracker API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
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
