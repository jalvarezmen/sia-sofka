"""Logging configuration for the application."""

import logging
import sys
from pathlib import Path
import os

# Create logger
logger = logging.getLogger("sia_sofka")

# Get debug setting safely (avoid circular imports)
def _get_debug_setting() -> bool:
    """Get debug setting safely."""
    try:
        # Try to get from environment first (faster, no import needed)
        debug_env = os.getenv("DEBUG", "").lower()
        if debug_env in ("true", "1", "yes"):
            return True
        # Fallback to settings if available
        from app.core.config import settings
        return getattr(settings, "debug", False)
    except Exception:
        return False

# Prevent duplicate handlers
if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    debug_mode = _get_debug_setting()
    console_handler.setLevel(logging.INFO if not debug_mode else logging.DEBUG)
    logger.setLevel(logging.INFO if not debug_mode else logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (only if logs directory exists or can be created)
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        from logging.handlers import RotatingFileHandler
        file_handler = RotatingFileHandler(
            log_dir / "app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (PermissionError, OSError, Exception):
        # If we can't create log files, just use console
        pass

# Export logger for use in other modules
__all__ = ["logger"]

