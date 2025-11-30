import time

from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .config import API_VERSION, APP_TITLE, STATIC_DIR
from .database import Base, engine
from .monitoring import MonitoringMiddleware
from .routes import router

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
    return {"status": "UP", "uptime_seconds": uptime, "version": API_VERSION}


# Prometheus metrics
# Note: FastAPI doesn't natively support WSGI middleware for metrics on the same port easily without uvicorn's help
# or a separate endpoint.
# But we can use prometheus-fastapi-instrumentator or just a simple endpoint if we want to keep it simple.
# The user asked for a /metrics endpoint using prometheus_client.
# A simple way is to expose the registry.
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
