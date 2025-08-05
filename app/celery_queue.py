from celery import Celery

from app.config import config
from app.tasks.schedule import ScheduledTasks


celery_app = Celery("worker", broker=config.amqp_dsn, include=["app.tasks.tasks", "app.tasks.upload_task"])

celery_app.conf.worker_pool_restarts = True
celery_app.conf.broker_connection_retry_on_startup = True
celery_app.conf.broker_heartbeat = 0

celery_app.conf.beat_schedule = {
    **ScheduledTasks.watchdog_tasks,
}
