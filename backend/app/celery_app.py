import logging
from celery import Celery
from celery.signals import after_setup_logger

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ---------------------------------------------------------------------------
# Celery application
# ---------------------------------------------------------------------------

celery_app = Celery(
    "valuai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=[
        "app.orchestrator.runner",  # main pipeline task (full async implementation)
        "app.tasks.valuation",      # re-export shim (used by upload router import)
    ],
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

celery_app.conf.update(
    # Serialisation
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    # Timezone
    timezone="Asia/Ho_Chi_Minh",
    enable_utc=True,
    # Result backend
    result_expires=86400,  # 24 h
    result_backend_transport_options={
        "master_name": "mymaster",
        "retry_policy": {
            "timeout": 5.0,
        },
    },
    # Task behaviour
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,  # one task at a time per worker (heavy AI calls)
    # Retries
    task_max_retries=3,
    task_default_retry_delay=60,  # 1 minute between retries
    # Soft / hard time limits (seconds)
    task_soft_time_limit=1800,   # 30 min → raises SoftTimeLimitExceeded
    task_time_limit=2100,        # 35 min → SIGKILL
    # Routing (single default queue for now)
    task_default_queue="valuai_default",
    task_queues={
        "valuai_default": {
            "exchange": "valuai_default",
            "routing_key": "valuai_default",
        },
    },
)


# ---------------------------------------------------------------------------
# Logging propagation
# ---------------------------------------------------------------------------


@after_setup_logger.connect
def setup_celery_logger(logger, *args, **kwargs):  # type: ignore[override]
    """Ensure Celery workers use the same log level as the app."""
    import logging as _logging

    _settings = get_settings()
    level = getattr(_logging, _settings.LOG_LEVEL.upper(), _logging.INFO)
    logger.setLevel(level)
