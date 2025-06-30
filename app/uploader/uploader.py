import os
import re
import zipfile

from loguru import logger
from pyrogram.client import Client
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid

from app.bot.bot import bot_instance
from app.config import config
from app.models import Content, Torrent, User
from app.entities.user.service import user_service, UserService
from app.entities.torrent.service import torrent_service, TorrentService


class Uploader:
    def __init__(self, user_service: UserService = user_service, torrent_service: TorrentService = torrent_service):
        self._tg_api_id = config.TELEGRAM_API_ID
        self._tg_api_hash = config.TELEGRAM_API_HASH
        self._torrent_svc = torrent_service
        self._user_svc = user_service
        self._known_user_ids: set[int] = set()
    
    async def __call__(self, user: User, contents: list[Content], torrent: Torrent) -> None:
        is_peer_known = await self._is_peer_known(user.tg_id)
        if not is_peer_known:
            if not user.is_blocked:
                await self._user_svc.set_user_blocked(user.id)
                logger.debug(f"Sent unblocking message to user {user.id}")
            await bot_instance.send_message_to_get_acquainted(user.tg_id)
            return
        try:
            if len(contents) > 1:
                file_to_send = self._make_archive(contents, torrent.title)
            else:
                file_to_send = contents[0].save_path
            if not file_to_send:
                logger.error("[!] No file to send! {file_to_send}")
                return
        except IndexError:
            logger.error("[!] IndexError! No file to send! {file_to_send}")
            return
        result = await self._send_file_to_user(file_to_send, user.tg_id)
        if not result["success"]:
            if result["error_code"] == 1:
                if not user.is_blocked:
                    await self._user_svc.set_user_blocked(user.id)
                    logger.debug(f"Sent unblocking message to user {user.id}")
                    await bot_instance.send_message_to_get_acquainted(user.tg_id)
                    return
            if result["error_code"] == 2:
                logger.error(f"[!] Uploader Error! Attempt to upload file {file_to_send} failed: return message is None!")
                return
            if result["error_code"] == 3:
                logger.error(f"! Uploader Error !: File {file_to_send} not found!")
                return
        # TODO: Think how to update torrent if it is used by another user at the time.
        torrent_updated = await self._torrent_svc.update_torrent({"is_task_done": True}, torrent.id)
        if not torrent_updated:
            logger.error(f"! Torrent Update Error !: Torrent {torrent.id} was not set is_task_done=True")
        if len(contents) > 1:
            self._delete_file(file_to_send)
    
    def _make_archive(self, contents: list[Content], torrent_title: str) -> str | None:
        file_paths = [content.save_path for content in contents]
        zip_filename = f"{torrent_title}.zip" if not torrent_title.lower().endswith('.zip') else torrent_title
        zip_filename = self._sanitize_filename(zip_filename)
        base_dir = config.HOST_SAVEPATH
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file_path in file_paths:
                if not file_path:
                    print("No file path!")
                    return
                full_path = os.path.abspath(file_path)
                arcname = os.path.relpath(full_path, base_dir)
                zipf.write(full_path, arcname=arcname)
        return os.path.abspath(zip_filename)

    async def _send_file_to_user(self, file_path: str, user_id: int) -> dict:
        try:
            with open(file_path, "rb") as file:
                try:
                    async with Client("uploader", api_id=self._tg_api_id, api_hash=self._tg_api_hash) as app:
                        message = await app.send_document(
                            chat_id=user_id,
                            document=file,
                            file_name=os.path.basename(file_path),
                        )
                        if not message:
                            return {"success": False, "error": True, "error_code": "2"}
                    return {"success": True, "error": False}
                except PeerIdInvalid:
                    return {"success": False, "error": True, "error_code": "1"}
        except FileNotFoundError:
            return {"success": False, "error": True, "error_code": "3"}
    
    async def _is_peer_known(self, user_id: int) -> bool:
        if user_id not in self._known_user_ids:
            await self._load_known_peers()
        return user_id in self._known_user_ids  # type: ignore

    async def _load_known_peers(self) -> None:
        """Загрузить список известных пользователей (peer'ов)"""
        async with Client("uploader", api_id=self._tg_api_id, api_hash=self._tg_api_hash) as app:
            # Сохраняем только ID пользователей из личных чатов
            async for dialog in app.get_dialogs():
                if dialog.chat.type.value == "private":
                    self._known_user_ids.add(dialog.chat.id)
                if not self._known_user_ids:
                    self._known_user_ids = {1}  # на случай, если нет личных чатов
    
    @staticmethod
    def _sanitize_filename(name: str) -> str:
        return re.sub(r'[\\/:"*?<>|]+', "_", name)
    
    @staticmethod
    def _delete_file(file_path: str) -> None:
        os.remove(file_path)


uploader = Uploader()
