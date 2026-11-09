"""
FastAPI application entry point.
Initializes core REST endpoints, platform management services, SQLite ORM models,
static asset hosting, and modular routers using modern FastAPI lifespan context.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import time
from typing import Optional
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from application.routes.auth import router as auth_router
from application.routes.users import router as users_router
from platform_core.database import Base, SessionLocal, engine
from platform_core.routes.dashboard_routes import router as platform_dashboard_router
from platform_core.routes.execution_routes import router as platform_execution_router
from platform_core.routes.github_routes import router as platform_github_router
from platform_core.routes.pipeline_routes import router as platform_pipeline_router
from platform_core.routes.projects_routes import router as platform_projects_router
from platform_core.services.project_service import ProjectService


def get_index_html_path() -> Optional[Path]:
    """Finds index.html across standard, relative, and serverless directory layouts."""
    candidates = [
        Path(__file__).resolve().parent / "static" / "index.html",
        Path(__file__).resolve().parent.parent / "api" / "static" / "index.html",
        Path("application/static/index.html"),
        Path("api/static/index.html")
    ]
    for c in candidates:
        if c.exists():
            return c
    return None


STATIC_DIR = Path(__file__).resolve().parent / "static"
if not (STATIC_DIR / "index.html").exists():
    alt = Path(__file__).resolve().parent.parent / "api" / "static"
    if (alt / "index.html").exists():
        STATIC_DIR = alt

try:
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
except Exception:
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern lifespan handler: initializes SQLite database and seeds default projects."""
    try:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as db:
            ProjectService.seed_default_projects_if_empty(db)
    except Exception as e:
        print(f"Startup initialization notice: {e}")
    yield


app = FastAPI(
    title="Intelligent API Automation & 3D CI/CD Management Platform",
    description="Enterprise-grade REST API test automation and CI/CD platform with interactive 3D pipeline visualization.",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Enable CORS for cross-origin test calls if needed
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Measure server processing time and add custom response header."""
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = (time.perf_counter() - start_time) * 1000  # in milliseconds
    response.headers["X-Process-Time-Ms"] = f"{process_time:.2f}"
    return response


# Include Target Microservice Routers (Backward Compatible)
app.include_router(auth_router)
app.include_router(users_router)

# Include Upgraded Platform Routers (Modules 1 - 7)
app.include_router(platform_projects_router)
app.include_router(platform_execution_router)
app.include_router(platform_pipeline_router)
app.include_router(platform_github_router)
app.include_router(platform_dashboard_router)

# Mount Static Assets safely with check_dir=False
app.mount("/static", StaticFiles(directory=str(STATIC_DIR), check_dir=False), name="static")


@app.get(
    "/platform",
    tags=["Platform UI"],
    summary="Web UI Platform",
    include_in_schema=False
)
def platform_ui():
    """Serves the Intelligent API Automation & 3D CI/CD Web Platform."""
    index_file = get_index_html_path()
    if index_file and index_file.exists():
        return FileResponse(str(index_file), media_type="text/html")
    return HTMLResponse("<h1>Antigravity API Platform</h1><p>Platform running in serverless mode.</p>")


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Root"],
    summary="API Root",
    description="Service information, platform UI link, and API documentation."
)
def root(request: Request):
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        index_file = get_index_html_path()
        if index_file and index_file.exists():
            return FileResponse(str(index_file), media_type="text/html")

    return {
        "service": "Intelligent API Automation & CI/CD Platform",
        "version": "2.0.0",
        "status": "online",
        "platform_ui": "/platform",
        "documentation": "/docs"
    }


@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health"],
    summary="Health Check",
    description="Returns the operational health status of the application."
)
def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "user-management-api"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("application.main:app", host="127.0.0.1", port=8000, reload=True)
