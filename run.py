"""
Simple runner script for the Notes App with Versioning
This script provides an easy way to start the application
"""

import uvicorn
import os
import sys
from app.config import DEFAULT_HOST, DEFAULT_PORT, LOG_LEVEL

def main():
    print("Starting Notes App with Versioning...")
    print("Features: CRUD operations, versioning, and modern UI")
    print(f"Access the app at: http://localhost:{DEFAULT_PORT}")
    print(f"API docs at: http://localhost:{DEFAULT_PORT}/docs")
    print("=" * 50)
    
    #Check if we're in the right directory
    if not os.path.exists("app/main.py"):
        print("Error: main.py not found. Please run from the project root directory.")
        sys.exit(1)
    # Start the application
    try:
        uvicorn.run(
            "app.main:app",
            host=DEFAULT_HOST,
            port=DEFAULT_PORT,
            reload=True,
            log_level=LOG_LEVEL
        )
    except KeyboardInterrupt:
        print("\nShutting down Notes App...")
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
