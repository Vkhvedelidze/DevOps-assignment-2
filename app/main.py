from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from .routes import router
from .database import engine, Base
from .config import APP_TITLE, API_VERSION, STATIC_DIR
from .monitoring import MonitoringMiddleware
import time

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title=APP_TITLE, version=API_VERSION)

# Add monitoring middleware
app.add_middleware(MonitoringMiddleware)

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Include API routes
app.include_router(router)

# Store app start time for health check
app.state.start_time = time.time()

# Enhanced health check endpoint
@app.get("/health")
async def health_check():
    uptime = int(time.time() - app.state.start_time)
    return {
        "status": "UP",
        "uptime_seconds": uptime,
        "version": API_VERSION
    }

# Prometheus metrics
# Note: FastAPI doesn't natively support WSGI middleware for metrics on the same port easily without uvicorn's help or a separate endpoint.
# But we can use prometheus-fastapi-instrumentator or just a simple endpoint if we want to keep it simple.
# The user asked for a /metrics endpoint using prometheus_client.
# A simple way is to expose the registry.

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
