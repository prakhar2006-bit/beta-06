"""Scheme Navigator API entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.schemes import router
from app.api.routes.eligibility import router as eligibility_router
from app.api.routes.questionnaire import router as questionnaire_router
from app.api.routes.results import router as results_router
from app.core.config import cors_origins, load_environment
from app.core.errors import register_errors

VERSION = "0.1.0"

load_environment()

app = FastAPI(
    title="Scheme Navigator API",
    description="Multilingual Government Scheme Eligibility Assistant",
    version=VERSION,
    docs_url="/docs",
)
app.add_middleware(CORSMiddleware, allow_origins=cors_origins(),
                   allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["Accept", "Content-Type"])
register_errors(app)
app.include_router(router)
app.include_router(eligibility_router)
app.include_router(questionnaire_router)
app.include_router(results_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Report application liveness without checking external services."""
    return {"status": "ok", "service": "Scheme Navigator", "version": VERSION}
