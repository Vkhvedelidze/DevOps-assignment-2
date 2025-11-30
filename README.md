# Notes App with Versioning - DevOps Assignment 2

A modern, production-ready notes application built with Python FastAPI, featuring full CI/CD, containerization, monitoring, and comprehensive testing.

[![CI Pipeline](https://github.com/username/repo/workflows/CI%20Pipeline/badge.svg)](https://github.com/username/repo/actions)
[![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)](./htmlcov/index.html)

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Quick Start](#quick-start)
4. [Architecture & Codebase](#architecture--codebase)
5. [Deployment Guide](#deployment-guide)
6. [Monitoring](#monitoring)
7. [Project Report](#project-report)

---

## Project Overview

This project is a **Notes Application** built with **FastAPI**. It allows users to create, read, update, and delete notes. The application supports versioning of notes, meaning edits create new versions rather than overwriting the original note immediately. It also includes monitoring with Prometheus and is container-ready with Docker.

### Key Technologies
- **Framework**: FastAPI (High performance, async support, auto-docs)
- **Database**: SQLAlchemy ORM with SQLite (Dev) and PostgreSQL (Prod)
- **Validation**: Pydantic v2
- **Frontend**: Bootstrap 5, Vanilla JS
- **DevOps**: Docker, GitHub Actions, Prometheus, Azure

---

## Features

### Core Functionality
- **CRUD Operations**: Create, read, update, and delete notes
- **Version Control**: Full version history with restore capability
- **Search**: Real-time filtering by title or content
- **Modern UI**: Bootstrap 5-based responsive interface

### DevOps Enhancements
- **86% Test Coverage**: Comprehensive unit and integration tests
- **CI/CD Pipeline**: Automated testing, linting, and deployment
- **Containerization**: Optimized Docker image with security best practices
- **Monitoring**: Prometheus metrics for requests, latency, and errors
- **Health Checks**: Enhanced endpoint with uptime and version info

---

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```
Access at `http://localhost:8000`

### Using Docker
```bash
# Build and run
docker build -t notes-app .
docker run -p 8000:8000 notes-app
```

### Testing
```bash
# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-report=html
```
**Current Coverage**: 86% (exceeds 70% requirement ✓)

---

## Architecture & Codebase

### Project Structure
The project follows a modular structure to ensure separation of concerns:

```
├── app/
│   ├── config.py         # Centralized configuration (SRP)
│   ├── database.py       # Database setup & connection
│   ├── models.py         # SQLAlchemy ORM models
│   ├── schemas.py        # Pydantic data schemas (DTOs)
│   ├── crud.py           # Database operations (CRUD)
│   ├── routes.py         # API endpoints
│   ├── main.py           # FastAPI application entry
│   └── monitoring.py     # Prometheus metrics middleware
├── tests/
│   ├── conftest.py       # Test fixtures
│   └── test_app.py       # Integration/Unit tests
├── static/               # Frontend assets (JS, CSS)
├── templates/            # HTML templates
├── .github/workflows/    # CI/CD pipelines
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
├── run.py                # Local runner script
└── README.md             # This file
```

### File Descriptions

#### Root Directory
- **`run.py`**: Entry point script to start the application locally using `uvicorn`.
- **`Dockerfile`**: Multi-stage build definition for creating the application container.
- **`prometheus.yml`**: Configuration for Prometheus monitoring to scrape the `/metrics` endpoint.

#### `app/` Directory
- **`app/config.py`**: Centralizes all configuration (env vars, constants) following 12-Factor App principles.
- **`app/database.py`**: Handles database connection. Automatically switches between SQLite (local) and PostgreSQL (cloud) based on `DATABASE_URL`.
- **`app/models.py`**: Defines the database schema (Tables: `notes`, `note_versions`).
- **`app/schemas.py`**: Defines Pydantic models for request/response validation.
- **`app/crud.py`**: Contains the logic for interacting with the database.
- **`app/routes.py`**: Defines the API endpoints and connects them to CRUD operations.
- **`app/monitoring.py`**: Custom middleware to track request metrics (latency, count, errors).

---

## Deployment Guide

This application is designed to be deployed to **Azure Web Apps for Containers** using **GitHub Actions**.

### Prerequisites
1. **Azure Account**: Create a Web App for Containers.
2. **Docker Hub Account**: Create a repository named `notes-app`.

### Step 1: Azure Configuration
1. Create a **Resource Group** and **Azure Container Registry (ACR)** (optional, or use Docker Hub).
2. Create an **Azure Database for PostgreSQL** (Flexible Server).
   - **Important**: Allow public access from any Azure service in Networking settings.
3. Create a **Web App for Containers**.
   - **Image Source**: Docker Hub (or ACR).
   - **Startup Command**: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (usually auto-detected).

### Step 2: Environment Variables
Configure the following in Azure Web App -> Settings -> Configuration:

- **`DATABASE_URL`**: Connection string for your PostgreSQL database.
  - Format: `postgresql://username:YOUR_PASSWORD@hostname:5432/dbname`
  - **Note**: Replace `YOUR_PASSWORD` with your actual database password.

### Step 3: GitHub Secrets
Go to your repository Settings -> Secrets and variables -> Actions, and add:

| Secret Name | Description |
|-------------|-------------|
| `DOCKERHUB_USERNAME` | Your Docker Hub username |
| `DOCKERHUB_TOKEN` | Docker Hub Access Token |
| `AZURE_WEBAPP_NAME` | The name of your Azure Web App |
| `AZURE_WEBAPP_PUBLISH_PROFILE` | The publish profile XML from Azure Portal |

### Step 4: CI/CD Pipeline
The pipeline (`.github/workflows/cd.yml`) triggers on push to `main`:
1. Runs tests and linting.
2. Builds the Docker image.
3. Pushes to Docker Hub.
4. Deploys to Azure Web App.

---

## Monitoring

### Endpoints
- **Health Check**: `GET /health`
  - Returns status, uptime, and version.
- **Metrics**: `GET /metrics`
  - Exposes Prometheus metrics: `http_requests_total`, `http_request_duration_seconds`, `http_errors_total`.

### Local Dashboard
Run Prometheus locally to visualize metrics:
```bash
docker run -p 9090:9090 -v ./prometheus.yml:/etc/prometheus/prometheus.yml prom/prometheus
```

---

## Project Report

### Achievements
- **Code Quality**: Refactored to adhere to SOLID principles. Implemented `app/config.py` for SRP.
- **Testing**: Achieved **86% code coverage**, exceeding the 70% requirement.
- **CI/CD**: Implemented a robust pipeline with matrix testing (Python 3.10-3.12), linting (flake8, black), and automated deployment.
- **Security**: Docker image runs as a non-root user. Secrets are managed via GitHub Secrets.

### Improvements Made
1. **Configuration Management**: Moved all hardcoded values to `app/config.py`.
2. **Error Handling**: Replaced file-based logging with structured logging.
3. **Dependency Updates**: Upgraded Pydantic to v2 and SQLAlchemy to latest stable versions.

### Future Improvements
- **Short-term**: Add integration tests for version restore edge cases.
- **Long-term**: Implement distributed tracing (OpenTelemetry) and blue-green deployments.

---

## License
Educational project for DevOps course.
