#!/usr/bin/env python3
"""
Startup script for the Successful CEOs UI system.
This script initializes the database, migrates data, and starts the API server.
"""

import os
import sys
import subprocess
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Project root directory
ROOT_DIR = Path(__file__).parent

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import pydantic
        logger.info("Core dependencies are installed")
        return True
    except ImportError as e:
        logger.error(f"Missing dependencies: {e}")
        logger.info("Please run: pip install -r requirements.txt")
        return False

def initialize_database():
    """Initialize the database and migrate data from JSON"""
    logger.info("Initializing database...")
    
    # Check if database file exists
    db_path = ROOT_DIR / "data" / "ceos.db"
    if db_path.exists():
        logger.info(f"Database already exists at {db_path}")
        user_input = input("Do you want to recreate the database? (y/N): ")
        if user_input.lower() != 'y':
            logger.info("Skipping database initialization")
            return True
        else:
            try:
                os.remove(db_path)
                logger.info("Existing database removed")
            except Exception as e:
                logger.error(f"Error removing database: {e}")
                return False
    
    # Initialize database schema
    try:
        from app.db.connection import init_db
        init_db()
        logger.info("Database schema initialized")
    except Exception as e:
        logger.error(f"Error initializing database schema: {e}")
        return False
    
    # Check for sample repository.json
    repo_path = ROOT_DIR / "data" / "sample_repository.json"
    if not repo_path.exists():
        repo_path = ROOT_DIR / "data" / "repository.json"
        if not repo_path.exists():
            logger.warning("No repository.json found. Database will be empty.")
            return True
    
    # Run migration script
    try:
        logger.info(f"Migrating data from {repo_path}...")
        
        # Add project root to Python path
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT_DIR)
        
        # Run migration script
        result = subprocess.run(
            [sys.executable, "-m", "app.tools.migrate_to_db", str(repo_path)],
            env=env,
            check=True
        )
        
        if result.returncode == 0:
            logger.info("Database migration completed successfully")
            return True
        else:
            logger.error("Database migration failed")
            return False
    except Exception as e:
        logger.error(f"Error running migration: {e}")
        return False

def start_api_server():
    """Start the FastAPI server"""
    logger.info("Starting API server...")
    
    try:
        # Add project root to Python path
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT_DIR)
        
        # Start the API server
        api_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.api.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
            env=env
        )
        
        logger.info("API server started on http://localhost:8000")
        return api_process
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        return None

def main():
    """Main entry point"""
    logger.info("Starting Successful CEOs UI system...")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Initialize database
    if not initialize_database():
        return 1
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        return 1
    
    # Print instructions
    print("\n" + "="*80)
    print("Successful CEOs UI System")
    print("="*80)
    print("\nAPI server is running at: http://localhost:8000")
    print("\nAPI Documentation: http://localhost:8000/docs")
    print("\nTo start the frontend (in a separate terminal):")
    print("  cd frontend")
    print("  npm install")
    print("  npm run dev")
    print("\nPress Ctrl+C to stop the server")
    print("="*80 + "\n")
    
    try:
        # Keep the script running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        if api_process:
            api_process.terminate()
            api_process.wait()
        logger.info("Server stopped")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())