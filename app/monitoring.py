"""
Enhanced monitoring middleware for the Notes App.
Provides metrics for request count, latency, and errors.
"""
import time
from prometheus_client import Counter, Histogram, Gauge
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

# Metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

REQUEST_IN_PROGRESS = Gauge(
    'http_requests_in_progress',
    'Number of HTTP requests in progress'
)

ERROR_COUNT = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status']
)

class MonitoringMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        REQUEST_IN_PROGRESS.inc()
        
        method = request.method
        endpoint = request.url.path
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Record metrics
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            
            if status_code >= 400:
                ERROR_COUNT.labels(method=method, endpoint=endpoint, status=status_code).inc()
            
            return response
        
        except Exception as e:
            # Record error
            ERROR_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()
            raise
        
        finally:
            # Record latency
            duration = time.time() - start_time
            REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
            REQUEST_IN_PROGRESS.dec()
