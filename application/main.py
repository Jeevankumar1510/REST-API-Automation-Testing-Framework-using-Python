"""
FastAPI application entry point.
Initializes routes, middleware, exception handling, and health endpoints.
"""

import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from application.routes.auth import router as auth_router
from application.routes.users import router as users_router

app = FastAPI(
    title="REST API Automation Testing Target Service",
    description="Industry-standard sample REST API backend designed for automated testing with Pytest and Requests.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
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


# Include modular routers
app.include_router(auth_router)
app.include_router(users_router)


@app.get(
    "/",
    status_code=status.HTTP_200_OK,
    tags=["Root"],
    summary="API Root",
    description="Service information and links to interactive API documentation."
)
def root():
    return {
        "service": "REST API Automation Testing Framework - Target Service",
        "version": "1.0.0",
        "status": "online",
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

