"""
=============================================================
  AI X-Ray Fracture Analysis Platform — FastAPI Entry Point
=============================================================
Starts the server, mounts static directories, loads models at
startup, and includes all API routes.
"""

import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# ── make sure project root is on sys.path ──────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from api.routes import router as api_router
from ml.model_loader import ModelLoader
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ── create required directories ────────────────────────────
for folder in ("models", "uploads", "outputs"):
    os.makedirs(os.path.join(BASE_DIR, folder), exist_ok=True)


# ── lifespan: pre-load heavy models once ───────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load ML models into memory before accepting requests."""
    logger.info("🚀  Starting model pre-load …")
    try:
        loader = ModelLoader.get_instance()
        loader.load_all()
        logger.info("✅  All models loaded successfully")
    except Exception as exc:
        logger.warning(f"⚠️  Model pre-load issue (non-fatal): {exc}")
    yield
    logger.info("🛑  Shutting down …")


# ── FastAPI application ────────────────────────────────────
app = FastAPI(
    title="AI X-Ray Fracture Analysis Platform",
    description="Upload X-ray images or reports to receive AI-powered "
                "fracture detection with annotated visuals and structured "
                "medical insights.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS (allow React dev server) ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── serve annotated output images as static files ──────────
app.mount(
    "/outputs",
    StaticFiles(directory=os.path.join(BASE_DIR, "outputs")),
    name="outputs",
)
app.mount(
    "/uploads",
    StaticFiles(directory=os.path.join(BASE_DIR, "uploads")),
    name="uploads",
)

# ── include API routes ─────────────────────────────────────
app.include_router(api_router, prefix="/api")


# ── root health-check ─────────────────────────────────────
@app.get("/")
async def root():
    return {
        "status": "running",
        "service": "AI X-Ray Fracture Analysis Platform",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )