import os
import shutil

from loguru import logger

from app.bot.bot import bot_instance
from app.torrent_client.qbittorrent import TorrentClient, torrent_client
from app.entities.torrent.service import TorrentService, torrent_service
from app.entities.content.service import ContentService, content_service
from app.entities.user.service import (
    UserContentService, UserService, UserTorrentService,
    user_content_service, user_service, user_torrent_service
)
from app.config import config
from app.tasks.tasks import upload_downloaded_contents


class Watchdog:
    def __init__(
        self,
        torrent_client: TorrentClient = torrent_client,
        torrent_service: TorrentService = torrent_service,
        content_service: ContentService = content_service,
        user_content_service: UserContentService = user_content_service,
        user_service: UserService = user_service,
        user_torrent_service: UserTorrentService = user_torrent_service,
    ):
        self._torrent_cli = torrent_client
        self._torrent_svc = torrent_service
        self._content_svc = content_service
        self._user_content_svc = user_content_service
        self._user_svc = user_service
        self._user_torrent_svc = user_torrent_service
        self._savepath = config.HOST_SAVEPATH

    async def __call__(self):
        torrents_to_watch = await self._torrent_svc.get_many({'is_processing': True})
        for torrent in torrents_to_watch:
            user_torrent_associations = await self._user_torrent_svc.find_associations_by_torrent_id(torrent.id)
            contents = await self._content_svc.get_by_torrent_id(torrent.id)
            torrent_files = self._torrent_cli.get_torrent_files(torrent.hash)
            if not torrent_files:
                continue
            for assoc in user_torrent_associations:
                user_id = assoc["user_id"]
                user = await self._user_svc.get(user_id)
                if user.is_blocked:
                    if not user.is_unblocking_message_sent:  # type: ignore
                        await bot_instance.send_message_to_get_acquainted(user.tg_id)
                        user = await self._user_svc.set_user_is_unblocking_message_sent(user.id)
                        logger.debug(f"Sent unblocking message to user {user_id}")
                        continue
                    if user.is_unblocking_message_sent:
                        continue
                user_content_associations = await self._user_content_svc.find_associations_by_user_id(user_id)
                user_selected_contents_ids = [assoc["content_id"] for assoc in user_content_associations]
                user_selected_contents = [content for content in contents if content.id in user_selected_contents_ids]
                ready_files_counter = int()
                ready_contents = []
                for file in torrent_files:
                    if file['progress'] >= 1:
                        content_ = [
                            content for content in contents if content in user_selected_contents and content.index == file['index']
                        ]
                        if not content_:
                            continue
                        content = content_[0]
                        ready_content = content
                        if not all((content.save_path, content.ready)):
                            file_path = f'{self._savepath}/{file["name"]}'
                            ready_content = await self._content_svc.update(
                                {'save_path': file_path, 'ready': True}, torrent.id, file['index']
                            )
                        ready_contents.append(ready_content)
                        logger.debug(f'Content downloaded: id {ready_content.id}, save_path {ready_content.save_path}')
                        ready_files_counter += 1
                if not ready_files_counter == len(ready_contents):
                    continue
                upload_downloaded_contents.delay(user, ready_contents, torrent)

    async def _delete_contents_from_db(self, torrent_id: int) -> int:
        rows_deleted = await self._content_svc.delete_by_torrent_id(torrent_id)
        return rows_deleted

    async def _delete_contents_from_disk(self, file_paths: list[str]) -> None:
        if not file_paths:
            return
        abs_paths = [os.path.abspath(p) for p in file_paths if p]
        if len(abs_paths) == 1:
            os.remove(file_paths[0])
            return
        common_root = os.path.commonpath(abs_paths)
        if not os.path.isdir(common_root):
            return
        shutil.rmtree(common_root)


watch_for_downloads = Watchdog()
