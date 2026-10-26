"""RQ Background Worker Tasks"""
import logging

logger = logging.getLogger(__name__)


def background_health_task() -> str:
    """Sample task to verify RQ worker execution."""
    logger.info("ArthMitra background worker health check executed successfully.")
    return "ok"
