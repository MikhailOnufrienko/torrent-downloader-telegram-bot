import asyncio

from app.celery_queue import celery_app
from app.models import Content
from app.uploader.uploader import uploader
from app.watchdog.watchdog import watch_for_downloads


@celery_app.task
def watch_for_downloads_task() -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(watch_for_downloads())


@celery_app.task
def upload_downloaded_contents(user_tg_id: int, contents: list[Content], torrent_title: str) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(uploader(user_tg_id, contents,torrent_title))
