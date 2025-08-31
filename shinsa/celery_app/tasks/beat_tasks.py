import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, name="say_hello_task")
def say_hello(self, name="Aung"):
    logger.info(f"👋 Hello {name}")
    return f"Hello {name}"


@shared_task(name="cleanup_task")
def cleanup():
    logger.info("🧹 Cleaning up old customer data...")
    return "cleanup done"
