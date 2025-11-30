"""
Application configuration and constants.
Centralizes configuration values following the Single Responsibility Principle.
"""
import os

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

# API Configuration
API_VERSION = "2.0.0"
APP_TITLE = "Notes App with Versioning"

# Server Configuration
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
LOG_LEVEL = "info"

# File paths (relative to project root)
TEMPLATES_DIR = "templates"
STATIC_DIR = "static"

# Logging configuration
ERROR_LOG_FILE = "error.log"
