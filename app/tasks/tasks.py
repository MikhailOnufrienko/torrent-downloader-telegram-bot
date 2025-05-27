import asyncio

from app.celery_queue import celery_app
from app.tasks.service import watch_for_downloads


@celery_app.task
def watch_for_downloads_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(watch_for_downloads())
