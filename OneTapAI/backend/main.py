"""
Main entry point for ZIEL-MAS Backend
"""

import uvicorn
import asyncio
import os
from loguru import logger
from backend.api.main import app
from config.settings import settings


def main():
    """Run the FastAPI application"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"API: http://{settings.API_HOST}:{settings.API_PORT}")
    logger.info(f"Docs: http://{settings.API_HOST}:{settings.API_PORT}/docs")

    uvicorn.run(
        "backend.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()
