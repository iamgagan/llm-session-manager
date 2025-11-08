"""Main FastAPI application for Team Dashboard."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import structlog
from pathlib import Path

from .config import get_settings
from .routers import auth, sessions, teams, analytics, insights
from .routers import projects, memory
from .database import engine, Base
from .websocket import router as ws_router

# Configure logging
logger = structlog.get_logger()

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="LLM Session Manager API",
    description="Team Dashboard API for managing AI coding sessions",
    version="0.3.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    redirect_slashes=False  # Disable automatic trailing slash redirects
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    logger.info("Starting up API server")

    # Create tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")


@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown."""
    logger.info("Shutting down API server")


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(memory.router, prefix="/api/memory", tags=["Memory"])
app.include_router(teams.router, prefix="/api/teams", tags=["Teams"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(insights.router, prefix="/api/insights", tags=["Insights"])
app.include_router(ws_router, prefix="/ws", tags=["WebSocket"])


# Mount frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")

    @app.get("/")
    async def serve_frontend():
        """Serve frontend dashboard."""
        return FileResponse(str(frontend_path / "index.html"))
else:
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "LLM Session Manager API",
            "version": "0.3.0",
            "docs": "/api/docs",
            "dashboard": "/static/index.html",
            "status": "running"
        }


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.3.0"
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error("Unhandled exception", exc_info=exc, path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "path": str(request.url.path)
        }
    )
