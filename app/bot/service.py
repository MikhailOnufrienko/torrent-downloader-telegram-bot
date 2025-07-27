import asyncio
import hashlib
import re
from datetime import datetime
from typing import BinaryIO

import bencodepy
from requests import HTTPError
from telegram import User as TGUser
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import BadRequest
from telegram.ext import CallbackContext
from loguru import logger

from app.torrent_client.qbittorrent import TorrentClient, torrent_client, with_relogin
from app.config import config
from app.entities.content.service import ContentService, content_service
from app.entities.torrent.service import TorrentService, torrent_service
from app.entities.user.service import (UserService, user_service, UserTorrentService,
                                       user_torrent_service, UserContentService, user_content_service)
from app.models import Content, Torrent, User
from app.common.messages import Messages, error_messages
from app.bot.structures import FileIDIndexPathSize
from app.bot.utils import shorten_path


class BotService:
    # SELECTED_SYMBOL = "✅"
    # PARTLY_SELECTED_SYMBOL = "☑️"
    # UNSELECTED_SYMBOL = "❌"

    def __init__(
        self,
        content_service: ContentService = content_service,
        torrent_client: TorrentClient = torrent_client,
        torrent_service: TorrentService = torrent_service,
        user_service: UserService = user_service,
        user_torrent_service: UserTorrentService = user_torrent_service,
        user_content_service: UserContentService = user_content_service,
    ):
        self._content_svc = content_service
        self._torrent_cli = torrent_client
        self._torrent_svc = torrent_service
        self._user_svc = user_service
        self._user_torrent_svc = user_torrent_service
        self._user_content_svc = user_content_service
        self.user_selections: dict[int, set] = dict()
    
    async def is_user_allowed_to_add_more_torrents(self, user_tg_id: int) -> dict:
        user = await self._user_svc.get_by_tg_id(user_tg_id)
        if not user:
            logger.error(f"[!] User with tg_id {user_tg_id} not found in DB.")
            return {"success": False, "error": True, "message": ""}
        user_torrents = await self._user_torrent_svc.fetch_torrents_by_user_id(user.id)
        active_torrents = [torrent for torrent in user_torrents if torrent.is_processing]
        active_torrents_amount = len(active_torrents)
        active_torrents_allowed = config.MAXIMUM_ACTIVE_TORRENTS
        if active_torrents_amount < active_torrents_allowed:
            return {"success": True, "error": False, "message": ""}
        return {"success": False, "error": False}

    async def save_user_if_not_exists(self, user: TGUser) -> User:
        return await self._user_svc.save_or_get_existing(user)

    @staticmethod
    def generate_hash_and_magnet_link_from_file(file: BinaryIO) -> tuple[str, str]:
        """Generate an info hash and a magnet link from the given torrent file."""
        torrent_data = bencodepy.decode(file.read())
        info = torrent_data[b"info"]
        info_hash = hashlib.sha1(bencodepy.encode(info)).hexdigest()
        magnet_link = f"magnet:?xt=urn:btih:{info_hash}"
        if b"announce-list" in torrent_data:
            for tier in torrent_data[b"announce-list"]:
                for tracker in tier:
                    magnet_link += f"&tr={tracker.decode()}"
        elif b"announce" in torrent_data:
            magnet_link += f'&tr={torrent_data[b"announce"].decode()}'
        return info_hash, magnet_link
    
    async def is_torrent_invalid(self, magnet_link: str, info_hash: str) -> dict:
        """Check if torrent meets the maximum size requirements.
        Return True if all torrent files exceed the maximum size.
        
        """
        maximum_size = config.MAXIMUM_TORRENTS_SIZE
        self._download_from_link(magnet_link)
        attempt = 0
        while attempt < 12:
            await asyncio.sleep(5)
            torrent_files = self._torrent_cli.get_torrent_files(info_hash)
            if torrent_files:
                break
            attempt += 1
        if not torrent_files:
            logger.info(f"[*] BOT SERVICE: Failed to get metadata of torrent {info_hash}")
            self._torrent_cli.delete_permanently(info_hash)
            return {"invalid": True, "metadata": False}
        invalid = all((file["size"] > maximum_size for file in torrent_files))
        if invalid:
            logger.info(f"[*] BOT SERVICE: The torrent {info_hash} is invalid")
            self._torrent_cli.delete_permanently(info_hash)
        return {"invalid": invalid, "metadata": True}

    @with_relogin
    def _download_from_link(self, magnet_link: str) -> None:
        self._torrent_cli.download_from_link(magnet_link, savepath=config.QBIT_SAVEPATH)

    async def save_torrent_and_contents(
        self, user_tg_id: int, magnet_link: str, info_hash: str = None
     ) -> tuple[Torrent, list[Content]] | None:
        if not info_hash:
            info_hash = self.extract_info_hash_from_magnet_link(magnet_link)
            if not info_hash:
                logger.error(f"No info hash generated from magnet_link {magnet_link}")
                return None
        user = await self._user_svc.get_by_tg_id(user_tg_id)
        if not user:
            return None
        torrent_info = await self.fetch_torrent_info(info_hash)
        torrent = {
            'user': user,
            'title': torrent_info['name'],
            'info_hash': info_hash,
            'magnet_link': magnet_link,
            'size': torrent_info['total_size'],
        }
        torrent = await self._torrent_svc.save_or_get_existing(torrent)
        await self._user_torrent_svc.save_association(user.id, torrent.id)
        torrent_files = self._get_torrent_files(info_hash)
        contents = await self._content_svc.save_many_if_not_exists(torrent_files, torrent.id)
        self._torrent_cli.delete_permanently(info_hash)
        return torrent, contents
    
    @with_relogin
    def _get_torrent_files(self, info_hash: str) -> dict:
        return self._torrent_cli.get_torrent_files(info_hash)

    async def fetch_torrent_info(self, info_hash: str) -> dict:
        existing_torrent = await self._torrent_svc.get_by_info_hash(info_hash)
        if existing_torrent:
            return {'name': existing_torrent.title, 'total_size': existing_torrent.size}
        return self._get_torrent(info_hash)
    
    @with_relogin
    def _get_torrent(self, info_hash: str) -> dict:
        return self._torrent_cli.get_torrent(info_hash)

    @staticmethod
    def extract_info_hash_from_magnet_link(magnet_link: str) -> str | None:
        pattern = r'magnet:\?xt=urn:btih:([a-fA-F0-9]{40}|[a-zA-Z0-9]{32})'
        match = re.search(pattern, magnet_link)
        if match:
            return match.group(1).lower()
        return None
 
    async def send_page_with_files(
        self, files: list[FileIDIndexPathSize], update: Update, context: CallbackContext, page: int, skip_edit: bool = False
    ) -> None:
        chat_id = update.effective_chat.id
        start_idx = page * config.FILES_PER_PAGE
        end_idx = start_idx + config.FILES_PER_PAGE
        page_items = [file.path for file in files[start_idx:end_idx]]
        keyboard = []
        torrent_id = context.user_data['torrent'].id
        for idx, item in enumerate(page_items):
            item_shortened = shorten_path(item, 50)
            selected = "✅" if item in self.user_selections.get(torrent_id, set()) else ""
            keyboard.append([
                InlineKeyboardButton(f"{selected} {item_shortened}", callback_data=f"toggle_{start_idx + idx}")
            ])
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️", callback_data=f"page_{page - 1}"))
        if end_idx < len(files):
            nav_buttons.append(InlineKeyboardButton("➡️", callback_data=f"page_{page + 1}"))
        if nav_buttons:
            keyboard.append(nav_buttons)
        keyboard.append([InlineKeyboardButton("Select all files", callback_data="select_all")])
        keyboard.append([InlineKeyboardButton("Unselect all files", callback_data="unselect_all")])
        keyboard.append([InlineKeyboardButton("✅ Ready", callback_data="done")])
        try:
            if update.callback_query and not skip_edit:
                await update.callback_query.edit_message_text(
                    text=Messages.select_files, reply_markup=InlineKeyboardMarkup(keyboard)
                )
            else:
                await context.bot.send_message(
                    chat_id=chat_id, text=Messages.select_files, reply_markup=InlineKeyboardMarkup(keyboard)
                )
        except BadRequest:
            pass

    async def save_and_download_user_choice(self, context: CallbackContext) -> None:
        user = await self._user_svc.get_by_tg_id(context._user_id)
        torrent = context.user_data['torrent']
        contents: list[FileIDIndexPathSize] = context.user_data['contents']
        content_ids = [content.id for content in contents if content.path in self.user_selections[torrent.id]]
        if content_ids:
            self._download_from_link(torrent.magnet_link)
            discarded_file_indexes = [  # The files the user doesn't want to download.
                content.index for content in contents if not content.path in self.user_selections[torrent.id]
            ]
            await asyncio.sleep(1)
            priority_set = await self._set_files_priority(discarded_file_indexes, torrent.hash)
            if not priority_set:
                logger.debug(f"[?] Failed to set priority for torrent {torrent.id}, user {user.id}")
            for content_id in content_ids:
                await self._user_content_svc.save_association(user.id, content_id)
            updated_torrent = await self._torrent_svc.update_torrent(
                {'is_task_sent': True, 'task_sent_at': datetime.now().replace(microsecond=0), 'is_processing': True},
                torrent.id
            )
            logger.debug(f'Torrent sent to download: id {torrent.id}.')
    
    async def _set_files_priority(self,discarded_file_indexes: list[int], torrent_hash: str) -> bool:
        max_retries = 30
        retry_delay = 2
        for attempt in range(max_retries):
            failed = False
            for idx in discarded_file_indexes:
                try:
                    self._set_file_priority(torrent_hash, idx)
                except HTTPError:
                    failed = True
                    break
            if not failed:
                break
            else:
                await asyncio.sleep(retry_delay)
        else:
            return False
        return True
    
    @with_relogin
    def _set_file_priority(self, torrent_hash: str, idx: int, priority: int = 0) -> None:
        return self._torrent_cli.set_file_priority(torrent_hash, idx, priority)

    async def set_user_unblocked(self, user_tg_id: int) -> dict:
        user = await self._user_svc.get_by_tg_id(user_tg_id)
        if not user:
            return {"success": False, "message": f"! ERROR ! No user found with tg ID {user_tg_id}."}
        user_updated = await self._user_svc.set_user_unblocked(user.id)
        if user_updated:
            return {"success": True, "message": f"* User {user.id} is unblocked."}
        return {"success": False, "message": f"! ERROR ! Failed to set user {user.id} unblocked."}

    async def is_selected_files_exceed_maximum_size(self, context: CallbackContext) -> bool:
        total_size = int()
        torrent = context.user_data['torrent']
        contents: list[FileIDIndexPathSize] = context.user_data['contents']
        selected_contents_sizes = [
            content.size for content in contents if content.path in self.user_selections[torrent.id]
        ]
        for file_size in selected_contents_sizes:
            total_size += file_size
        return total_size > config.MAXIMUM_TORRENTS_SIZE
    
    async def send_page_with_active_torrents(self, tg_user_id: int, update: Update, context: CallbackContext) -> None:
        user = await self._user_svc.get_by_tg_id(tg_user_id)
        chat_id = update.effective_chat.id
        if not user:
            logger.error(f"[!] User with tg_id {tg_user_id} not found in DB")
            await context.bot.send_message(chat_id=chat_id, text=error_messages["4"])
            return
        user_torrents = await self._user_torrent_svc.fetch_torrents_by_user_id(user.id)
        if not user_torrents:
            await context.bot.send_message(chat_id=chat_id, text=Messages.no_active_torrents)
            return
        at_least_one_active_torrent = False
        keyboard = []
        for torrent in user_torrents:
            if torrent.is_processing:
                at_least_one_active_torrent = True
                keyboard.append([InlineKeyboardButton(torrent.title, callback_data="nothing")])
                keyboard.append([InlineKeyboardButton(Messages.remove, callback_data=f"torrent_{torrent.id}")])
        if not at_least_one_active_torrent:
            await context.bot.send_message(chat_id=chat_id, text=Messages.no_active_torrents)
            return
        await context.bot.send_message(
            chat_id=chat_id, text=Messages.your_active_torrents, reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    async def delete_active_torrent(self, tg_user_id: int, torrent_id: int) -> None:
        user = await self._user_svc.get_by_tg_id(tg_user_id)
        await self._user_torrent_svc.delete_association(user.id, torrent_id)
        logger.info(f"[*] Removed user_torrent_associations of user {user.id}, torrent {torrent_id}")
        user_torrent_associations = await self._user_torrent_svc.count_user_torrent_associations(torrent_id)
        u_c_associations = await self._user_content_svc.find_associations_by_user_id(user.id)
        user_selected_contents_ids = [assoc["content_id"] for assoc in u_c_associations]
        await self._user_content_svc.delete_associations(user.id, user_selected_contents_ids)
        logger.info(f"[*] Removed user contents associations of user {user.id}")
        if user_torrent_associations == 0:
            await self._content_svc.delete_by_torrent_id(torrent_id)
            logger.info(f"[*] Removed contents of torrent {torrent_id}")
            torrent = await self._torrent_svc.get(torrent_id)
            if torrent:
                self._delete_permanently(torrent.hash)
                await self._torrent_svc.update_torrent({"is_processing": False}, torrent_id)
    
    @with_relogin
    def _delete_permanently(self, torrent_hash: str) -> None:
        return self._torrent_cli.delete_permanently(torrent_hash)


bot_service = BotService()
