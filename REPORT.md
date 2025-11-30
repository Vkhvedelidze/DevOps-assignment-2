# DevOps Assignment 2 - Implementation Report

**Student:** Vako Khvedelidze  
**Project:** Notes Application with versioning and Full DevOps Pipeline  

---

## Executive Summary

This report documents the improvements made to the Notes Application from Assignment 1, focusing on code quality, automated testing, CI/CD automation, containerization, and monitoring. All assignment requirements have been met or exceeded, with **86% code coverage** (exceeding the 70% requirement) and a fully functional CI/CD pipeline integrated with GitHub Actions.

---

## 1. Code Quality and Refactoring (25%)

### 1.1 Code Smells Eliminated

**Problem Identified:**
- Hardcoded configuration values scattered across multiple files
- Poor separation of concerns
- Duplicate configuration patterns
- Magic numbers and strings

**Solutions Implemented:**

#### Created `app/config.py` - Centralized Configuration
```python
# All configuration in one place following Single Responsibility Principle
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")
API_VERSION = "2.0.0"
APP_TITLE = "Notes App with Versioning"
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
```

**Files Refactored:**
- `app/database.py` → uses `config.DATABASE_URL`
- `app/main.py` → uses `config.APP_TITLE`, `config.API_VERSION`
- `run.py` → uses `config.DEFAULT_HOST`, `config.DEFAULT_PORT`

**Benefits:**
- ✅ Easier to modify configuration
- ✅ Environment-specific settings via environment variables
- ✅ No hardcoded values in business logic

### 1.2 SOLID Principles Applied

**Single Responsibility Principle (SRP):**
- `config.py` → Configuration management only
-  `crud.py` → Database operations only
- `routes.py` → API endpoint definitions only
- `monitoring.py` → Metrics collection only

**Dependency Inversion Principle (DIP):**
- Database dependency injection using FastAPI's `Depends(get_db)`
- Testable architecture with in-memory database for tests

---

## 2. Testing and Coverage (20%)

### 2.1 Test Infrastructure

**Framework:** pytest with pytest-cov  
**Test Isolation:** In-memory SQLite database per test function  
**Coverage Target:** 70% **→ Achieved: 86%**

### 2.2 Test Suite Coverage

```
Name                    Stmts   Miss  Cover   Missing Lines
-------------------------------------------------------------
app/config.py              11      0   100%
app/crud.py                92     30    67%   45, 61-70, 79, 92-101
app/database.py            13      1    92%   
app/main.py                17      2    88%   
app/models.py              26      0   100%
app/monitoring.py          30      5    83%   
app/routes.py              45      4    91%   
app/schemas.py             26      0   100%
-------------------------------------------------------------
TOTAL                     260     42    86%
```

### 2.3 Comprehensive Test Cases

**9 Integration/Unit Tests:**
1. `test_health_check` - Enhanced health endpoint with uptime and version
2. `test_metrics_endpoint` - Prometheus metrics exposure
3. `test_create_note` - Note creation with validation
4. `test_get_notes` - Note retrieval
5. `test_search_notes` - Search functionality
6. `test_get_specific_note` - Single note retrieval
7. `test_update_note` - Note updates with versioning
8. `test_delete_note` - Note deletion
9. `test_version_history_and_restore` - Full versioning workflow

---
## 3. Continuous Integration (CI) (20%)

### 3.1 CI Pipeline Configuration

**File:** `.github/workflows/ci.yml`

**Pipeline Stages:**

#### Stage 1: Testing (Matrix Strategy)
- **Python Versions:** 3.10, 3.11, 3.12
- **Coverage Enforcement:** Pipeline fails if coverage < 70%
- **Caching:** pip dependencies for faster builds
- **Reporting:** Codecov integration

#### Stage 2: Linting
- **Black:** Code formatting verification
- **isort:** Import order checking (with `--profile black` for compatibility)
- **flake8:** PEP 8 compliance (max-line-length: 120)

#### Stage 3: Build
- **Docker Build:** Validates Dockerfile
- **Container Test:** Starts container and verifies `/health` endpoint
- **Dependencies:** Only runs if tests and linting pass

### 3.2 Failure Conditions

The pipeline fails if:
-  Tests fail
-  Coverage below 70%
-  Code formatting violations (black/isort)
-  Linting errors (flake8)
-  Docker build fails
-  Health check fails

---

## 4. Deployment and Containerization (20%)

### 4.1 Dockerfile Optimizations

**Security Best Practices:**
```dockerfile
# Non-root user for security
RUN useradd -m -u 1000 appuser
USER appuser
```

**Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

**Layer Caching:**
```dockerfile
# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Copy application code last (changes more frequently)
COPY app ./app
```

### 4.2 Continuous Deployment (CD)

**File:** `.github/workflows/cd.yml`

**Deployment Flow:**
1. **Trigger:** Push to `main` branch only
2. **Docker Hub:** Build and push tagged images (`:latest`, `:commit-sha`)
3. **Azure Deployment:** Automatic deployment to Azure Web App
4. **Secrets Management:** Secure credential management via GitHub Secrets

**Required Secrets:**
- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `AZURE_WEBAPP_NAME`
- `AZURE_WEBAPP_PUBLISH_PROFILE`

### 4.3 Database Configuration

**Database:** SQLite (`notes.db`)
- **Local Development:** SQLite file-based database
- **Production:** SQLite with persistent volume mounting in containers
- **Flexibility:** Code supports PostgreSQL via `DATABASE_URL` environment variable if needed for future scaling

**Benefits of SQLite for this project:**
- ✅ Zero configuration required
- ✅ Perfect for development and testing
- ✅ Portable (single file database)
- ✅ Sufficient for assignment requirements

---

## 5. Monitoring and Health Checks (15%)

### 5.1 Health Endpoint

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "UP",
  "uptime_seconds": 3600,
  "version": "2.0.0"
}
```

**Purpose:**
- Container orchestrators can check application health
- Load balancers can route traffic only to healthy instances
- Monitoring systems can track availability

### 5.2 Prometheus Metrics

**File:** `app/monitoring.py` - Custom middleware

**Metrics Exposed:**

1. **`http_requests_total` (Counter)**
   - Labels: method, endpoint, status
   - Tracks all HTTP requests

2. **`http_request_duration_seconds` (Histogram)**
   - Labels: method, endpoint
   - Measures request latency (for performance analysis)

3. **`http_requests_in_progress` (Gauge)**
   - Real-time concurrent request count

4. **`http_errors_total` (Counter)**
   - Labels: method, endpoint, status
   - Tracks 4xx and 5xx errors

**Metrics Endpoint:** `GET /metrics` (Prometheus format)

### 5.3 Prometheus Setup

**Configuration File:** `prometheus.yml`

```yaml
scrape_configs:
  - job_name: 'notes-app'
    static_configs:
      - targets: ['localhost:8000']
```

**Sample Queries:**
- Request rate: `rate(http_requests_total[5m])`
- Error rate: `rate(http_errors_total[5m])`
- Latency p95: `histogram_quantile(0.95, http_request_duration_seconds)`

---

## 6. Documentation

### 6.1 README.md

Comprehensive documentation including:
- Project overview and features
- Quick start guide (local and Docker)
- Testing instructions with coverage commands
- Deployment guide for Azure
- API documentation
- Architecture and file structure
- Monitoring setup instructions

## Summary of Achievements

| Component | Requirement | Achievement |
|-----------|-------------|-------------|
| **Code Coverage** | 70% |   **86%** |
| **Refactoring** | Remove smells, SOLID |  Config module, SRP compliance |
| **CI Pipeline** | Tests, coverage, build |  Multi-version testing, linting |
| **CD Pipeline** | Deployment automation |  Docker Hub + Azure integration |
| **Health Check** | `/health` endpoint |  Status, uptime, version |
| **Metrics** | Request count, latency, errors | 4 metric types with Prometheus |
| **Containerization** | Docker | Optimized, secure, health checks |
| **Documentation** | README, tests docs | Comprehensive guides |

---
