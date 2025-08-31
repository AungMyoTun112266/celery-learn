from celery import Celery
from .config import CELERY_CONFIG, BEAT_SCHEDULE

celery_app = Celery("Shinsa Application")
celery_app.config_from_object(CELERY_CONFIG)

celery_app.conf.beat_schedule = BEAT_SCHEDULE
celery_app.autodiscover_tasks(
    [
        "shinsa.celery_app.tasks.customer_tasks",
        "shinsa.celery_app.tasks.crawl_tasks",
        "shinsa.celery_app.tasks.analysis_tasks",
        "shinsa.celery_app.tasks.report_tasks",
        "shinsa.celery_app.tasks.beat_tasks",
    ]
)
