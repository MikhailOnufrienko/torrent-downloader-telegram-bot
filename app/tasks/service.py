import asyncio

from loguru import logger


from app.client.qbittorrent import TorrentClient, torrent_client
from app.entities.torrent.service import TorrentService, torrent_service
from app.entities.content.service import ContentService, content_service
from app.models import Content, Torrent
from app.config import config
from app.tasks.uploader import TGUploader, tg_uploader


class Watchdog:
    def __init__(
        self,
        torrent_client: TorrentClient = torrent_client,
        torrent_service: TorrentService = torrent_service,
        content_service: ContentService = content_service,
        telegram_uploader: TGUploader = tg_uploader,
    ):
        self._torrent_cli = torrent_client
        self._torrent_svc = torrent_service
        self._content_svc = content_service
        self._savepath = config.HOST_SAVEPATH
        self._tg_uploader = telegram_uploader
    
    async def __call__(self):
        torrents_to_watch = await self._torrent_svc.get_many({'is_processing': True})
        for torrent in torrents_to_watch:
            # torrent_info = self._torrent_cli.get_torrent(torrent.hash)
            # total_size = torrent_info["total_size"]
            # total_downloaded = torrent_info["total_downloaded"]
            # if total_size != -1 and total_downloaded >= total_size:
            # torrent_updated = await self._torrent_svc.update_torrent({'is_processing': False}, torrent.id)
            contents = await self._content_svc.get_by_torrent_id(torrent.id)
            torrent_files = self._torrent_cli.get_torrent_files(torrent.hash)
            for file in torrent_files:
                if file['progress'] >= 1:
                    content = [content for content in contents if content.index == file['index']][0]
                    if not content.ready:
                        file_path = f'{self._savepath}/{file["name"]}'
                        content_updated = await self._content_svc.update(
                            {'ready': True, 'save_path': file_path}, torrent.id, file['index']
                        )
                        logger.debug(f'Content downloaded: id {content_updated.id}, save_path {content_updated.save_path}')
                        content_url = await self._tg_uploader.upload_file(file_path)
                    # print(content_url)
                #  Создать архив с контентом
                #  Отправить архив пользователю


watch_for_downloads = Watchdog()

if __name__ == '__main__':
    asyncio.run(watch_for_downloads())
