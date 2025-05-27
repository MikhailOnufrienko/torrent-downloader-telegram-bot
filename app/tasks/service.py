import asyncio

from loguru import logger


from app.client.qbittorrent import TorrentClient, torrent_client
from app.entities.torrent.service import TorrentService, torrent_service
from app.entities.content.service import ContentService, content_service
from app.entities.user.service import UserContentService, UserTorrentService, user_content_service, user_torrent_service
from app.models import Content, Torrent
from app.config import config
from app.tasks.uploader import TGUploader, tg_uploader


class Watchdog:
    def __init__(
        self,
        torrent_client: TorrentClient = torrent_client,
        torrent_service: TorrentService = torrent_service,
        content_service: ContentService = content_service,
        user_content_service: UserContentService = user_content_service,
        user_torrent_service: UserTorrentService = user_torrent_service,
        telegram_uploader: TGUploader = tg_uploader,
    ):
        self._torrent_cli = torrent_client
        self._torrent_svc = torrent_service
        self._content_svc = content_service
        self._user_content_svc = user_content_service
        self._user_torrent_svc = user_torrent_service
        self._savepath = config.HOST_SAVEPATH
        self._tg_uploader = telegram_uploader
    
    async def __call__(self):
        torrents_to_watch = await self._torrent_svc.get_many({'is_processing': True})
        for torrent in torrents_to_watch:
            user_torrent_associations = await self._user_torrent_svc.find_associations_by_torrent_id(torrent.id)
            contents = await self._content_svc.get_by_torrent_id(torrent.id)
            torrent_files = self._torrent_cli.get_torrent_files(torrent.hash)
            for assoc in user_torrent_associations:
                user_id = assoc["user_id"]
                user_content_associations = await self._user_content_svc.find_associations_by_user_id(user_id)
                user_selected_contents_ids = [assoc["content_id"] for assoc in user_content_associations]
                for file in torrent_files:
                    if file['progress'] >= 1:
                        content = [
                            content for content in contents if content.id in user_selected_contents_ids and content.index == file['index']
                        ][0]
                        if not content.ready:
                            file_path = f'{self._savepath}/{file["name"]}'
                            content_updated = await self._content_svc.update(
                                {'ready': True, 'save_path': file_path}, torrent.id, file['index']
                            )
                            logger.debug(f'Content downloaded: id {content_updated.id}, save_path {content_updated.save_path}')
                            # content_url = await self._tg_uploader.upload_file(file_path)
                            # if not content_url:
                            #     print("No content URL.")
                            #     return
                            # print("Content URL: ", content_url)
                            #  Создать архив с контентом
                            #  Отправить архив пользователю
                if await self._is_contents_ready(user_selected_contents_ids):
                    # Собрать скачанные файлы, сделать архив и отправить пользователю.
                    # Затем проставить content._is_deleted.
                    # Проработать случай, если на закачку вновь идёт тот же контент: надо проставить is_ready=False, is_deleted=False
                    # Как-то проверить, не качает ли сейчас данный торрент кто-то другой. Если нет, проставляем у торрента is_processing=False
                    # и удаляем его из клиента и физически его файлы с диска.
                    pass

    async def _is_contents_ready(self, contents_ids: list[int]) -> bool:
        for content_id in contents_ids:
            content = await self._content_svc.get(content_id)
            if not content:
                continue  # TODO: think how to deal with this case.
            if not content.ready:
                return False
        return True


watch_for_downloads = Watchdog()
asyncio.run(watch_for_downloads())
