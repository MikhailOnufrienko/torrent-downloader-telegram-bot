import asyncio

from app.celery_queue import celery_app
from app.uploader.uploader import uploader


@celery_app.task
def upload_downloaded_contents(user_id: int, contents: list[int], torrent_id: int) -> None:
    loop = asyncio.get_event_loop()
    loop.run_until_complete(uploader(user_id, contents,torrent_id))
