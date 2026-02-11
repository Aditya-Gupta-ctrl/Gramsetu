"""
Shared logging configuration for all services
Provides structured JSON logging with context
"""
import logging
import sys
from loguru import logger
from shared.config import get_settings

settings = get_settings()


def setup_logging(service_name: str):
    """
    Configure loguru for the service
    
    Args:
        service_name: Name of the service (voice, agent, document, orchestrator)
    """
    # Remove default handler
    logger.remove()
    
    # Determine format based on config
    if settings.log_format == "json":
        log_format = (
            '{"time": "{time:YYYY-MM-DD HH:mm:ss.SSS}", '
            '"level": "{level}", '
            '"service": "' + service_name + '", '
            '"message": "{message}", '
            '"extra": {extra}}'
        )
    else:
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>" + service_name + "</cyan> | "
            "<level>{message}</level>"
        )
    
    # Add console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=(settings.log_format != "json"),
    )
    
    # Add file handler
    logger.add(
        f"logs/{service_name}.log",
        format=log_format,
        level=settings.log_level,
        rotation="100 MB",
        retention="7 days",
        compression="zip",
    )
    
    logger.info(f"{service_name} logging initialized", level=settings.log_level)
    
    return logger
