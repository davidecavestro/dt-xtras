from loguru import logger
import sys
import os

# Remove default logger
logger.remove()

# Configure logger based on environment
is_development = os.getenv("NODE_ENV") == "development" or not os.getenv("NODE_ENV")

if is_development:
    # Development configuration - colorful and detailed
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="DEBUG",
        colorize=True
    )
else:
    # Production configuration - structured JSON
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO",
        colorize=False
    )

# Add file logging for production
if not is_development:
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="INFO"
    )
    
    logger.add(
        "logs/error.log",
        rotation="10 MB",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}",
        level="ERROR"
    )

# Create module-specific loggers
def get_logger(name: str):
    """Get a logger with module name"""
    return logger.bind(name=name)

# Export the configured logger
__all__ = ["logger", "get_logger"]
