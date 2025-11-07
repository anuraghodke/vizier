"""
FastAPI main application entry point for Vizier animation generation.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
from pathlib import Path

from app.routers import generation

# Create FastAPI app
app = FastAPI(
    title="Vizier API",
    description="AI-Assisted 2D Animation Inbetweening Tool",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Vite dev server
        "http://localhost:5173",  # Alternative Vite port
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(generation.router, prefix="/api", tags=["generation"])

# Create directories if they don't exist
UPLOADS_DIR = Path("uploads")
OUTPUTS_DIR = Path("outputs")
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# Mount static file serving for generated frames
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/")
async def root():
    """Root endpoint - API info"""
    return {
        "name": "Vizier API",
        "version": "0.1.0",
        "description": "AI-Assisted 2D Animation Inbetweening Tool",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "vizier-backend",
        "uploads_dir": str(UPLOADS_DIR.exists()),
        "outputs_dir": str(OUTPUTS_DIR.exists())
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc)
        }
    )
