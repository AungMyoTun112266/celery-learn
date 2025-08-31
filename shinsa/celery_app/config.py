import os
from dotenv import load_dotenv
from kombu import Exchange, Queue

load_dotenv()
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Exchanges
default_exchange = Exchange("default", type="direct")
io_exchange = Exchange("io_intensive", type="direct")
cpu_exchange = Exchange("cpu_intensive", type="direct")
orchestration_exchange = Exchange("orchestration", type="direct")
# Task routing configuration
CELERY_TASK_ROUTES = {
    # Coordination tasks (fast, lightweight)
    "find_customer_links": {"queue": "coordination"},
    "process_customer_workflow": {"queue": "coordination"},
    "generate_customer_report": {"queue": "coordination"},
    "batch_generate_report": {"queue": "coordination"},
    # I/O intensive tasks
    "crawl_link": {"queue": "io_intensive"},
    "fetch_page_content": {"queue": "io_intensive"},
    # CPU intensive tasks
    "analyze_content": {"queue": "cpu_intensive"},
    "extract_keywords": {"queue": "cpu_intensive"},
}

# Queue definitions
CELERY_TASK_QUEUES = (
    Queue(
        "coordination",
        exchange=orchestration_exchange,
        routing_key="coordination",
        queue_arguments={"x-max-priority": 10},
    ),
    Queue(
        "io_intensive",
        exchange=io_exchange,
        routing_key="io_intensive",
        queue_arguments={"x-max-priority": 5},
    ),
    Queue(
        "cpu_intensive",
        exchange=cpu_exchange,
        routing_key="cpu_intensive",
        queue_arguments={"x-max-priority": 5},
    ),
    # Queue(
    #     "default",
    #     exchange=default_exchange,
    #     routing_key="default",
    # ),
)
CELERY_CONFIG = {
    "broker_url": CELERY_BROKER_URL,
    "result_backend": CELERY_RESULT_BACKEND,
    "task_serializer": "json",
    "accept_content": ["json"],
    "result_serializer": "json",
    "timezone": "UTC",
    "enable_utc": True,
    "task_track_started": True,
    "task_time_limit": 600,  # 10 minutes
    "task_soft_time_limit": 540,  # 9 minutes
    "worker_prefetch_multiplier": 4,
    "task_acks_late": True,
    "worker_disable_rate_limits": True,
    "task_routes": CELERY_TASK_ROUTES,
    # "task_default_queue": "default",
    "task_queues": CELERY_TASK_QUEUES,
    "worker_send_task_events": True,
    "task_send_sent_event": True,
}

# Worker configurations
WORKER_CONFIGS = {
    "coordination": {
        "concurrency": 4,
        "prefetch_multiplier": 10,
        "queues": ["coordination"],
    },
    "io_intensive": {
        "concurrency": 20,
        "prefetch_multiplier": 4,
        "queues": ["io_intensive"],
    },
    "cpu_intensive": {
        "concurrency": 0,  # Auto-detect CPU cores
        "prefetch_multiplier": 1,
        "queues": ["cpu_intensive"],
    },
}
