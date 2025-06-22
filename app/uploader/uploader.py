import os
import re
import zipfile

from pyrogram.client import Client
from pyrogram.errors.exceptions.bad_request_400 import PeerIdInvalid
from telegram import Bot

from app.config import config
from app.models import Content


class Uploader:
    def __init__(self, bot: Bot = Bot(config.TELEGRAM_BOT_TOKEN)):
        self._bot = bot
        self._chat_id = config.TELEGRAM_REPO_CHAT_ID
        self._tg_api_id = config.TELEGRAM_API_ID
        self._tg_api_hash = config.TELEGRAM_API_HASH
        self._known_user_ids: set[int] = set()
    
    async def __call__(self, user_tg_id: int, contents: list[Content], torrent_title: str) -> dict:
        is_peer_known = await self._is_peer_known(user_tg_id)
        if not is_peer_known:
            return {"success": False, "error_code": "1"}
        if len(contents) > 1:
            file_to_send = self._make_archive(contents, torrent_title)
        else:
            file_to_send = contents[0].save_path
        if not file_to_send:
            print("No file to send! {file_to_send}")
            return {"success": False, "error_code": "2"}
        result = await self._send_file_to_user(file_to_send, user_tg_id)
        self._delete_file(file_to_send) if len(contents) > 1 else None
        return result
    
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
                            print(f"! Uploader Error !: Attempt to upload file {file_path} failed: return message is None!")
                            return {"success": False, "error_code": "2"}
                    return {"success": True}
                except PeerIdInvalid:
                    return {"success": False, "error_code": "1"}
        except FileNotFoundError:
            print(f"! Uploader Error !: File {file_path} not found!")
            return {"success": False, "error_code": "3"}
    
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
