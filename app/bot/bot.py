from io import BytesIO

from loguru import logger
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters, ApplicationBuilder)
from telegram.request import HTTPXRequest

from app.common.messages import Messages, error_messages
from app.bot.service import BotService, bot_service
from app.config import config
from app.bot.structures import FileIDIndexPath


class CustomHTTPXRequest(HTTPXRequest):
    def __init__(self, base_url: str, **kwargs):
        # Инициализация родительского класса с аргументами
        super().__init__(**kwargs)
        self.base_url = base_url

    # Переопределение метода build_url
    def build_url(self, endpoint: str) -> str:
        return f"{self.base_url}/{endpoint.lstrip('/')}"


custom_base_url = config.BOT_URL.unicode_string()
request = CustomHTTPXRequest(base_url=custom_base_url)
application = ApplicationBuilder().token(config.TELEGRAM_BOT_TOKEN).request(request).build()


class MainBot:
    def __init__(
        self,
        bot_service: BotService = bot_service,
        bot = application.bot,
    ):
        self._bot_svc = bot_service
        self._bot = bot

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        keyboard = [[InlineKeyboardButton("Start", callback_data="start_pressed")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(Messages.hello, reply_markup=reply_markup)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(Messages.invitation)
        tg_user = update.effective_user
        await self._bot_svc.save_user_if_not_exists(tg_user)

    async def handle_torrent(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message
        if message.text and message.text.lower().startswith('magnet'):
            magnet_link = message.text
            info_hash = None
            await update.message.reply_text(Messages.link_received)
        elif message.document:
            await update.message.reply_text(Messages.file_received)
            file = await message.document.get_file()
            byte_array = await file.download_as_bytearray()
            byte_stream = BytesIO(byte_array)
            info_hash, magnet_link = self._bot_svc.generate_hash_and_magnet_link_from_file(byte_stream)
        else:
            await update.message.reply_text(Messages.invitation_after_error)
            return
        result = await self._bot_svc.save_torrent_and_contents(
            update.message.from_user['id'], magnet_link, info_hash
        )
        if not result:
            return
        torrent, contents = result[0], result[1]
        context.user_data['torrent'] = torrent  # Here the torrent is linked to the user.
        files_id_index_path = [
            FileIDIndexPath(id=content.id, index=content.index, path=content.file_name) for content in contents
        ]
        context.user_data['contents'] = files_id_index_path  # Here all contents of the torrent are linked to the user.
        self._bot_svc.user_selections[torrent.id] = set()  # This set will store the contents the user will choose.
        await self._bot_svc.send_page_with_files(files_id_index_path, update, context, page=0)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        data = query.data
        if data == "message_sent":
            result = await self._bot_svc.set_user_unblocked(update)
            if not result["success"]:
                logger.error(result["message"])
                await query.message.reply_text("Ой! Что-то пошло не так...")
                return
            await query.message.reply_text("Спасибо! Сообщение принято.")
            return
        contents = context.user_data['contents']
        torrent_id = context.user_data['torrent'].id
        if data.startswith("toggle_"):
            # File selection.
            item_idx = int(data.split("_")[1])
            item = contents[item_idx].path
            # Update user's choice.
            if item in self._bot_svc.user_selections[torrent_id]:
                self._bot_svc.user_selections[torrent_id].remove(item)
            else:
                self._bot_svc.user_selections[torrent_id].add(item)
            await self._bot_svc.send_page_with_files(contents, update, context, page=item_idx // config.FILES_PER_PAGE)
        elif data.startswith("page_"):
            # Switching between pages.
            page = int(data.split("_")[1])
            await self._bot_svc.send_page_with_files(contents, update, context, page=page)
        elif data == 'select_all':
            self._bot_svc.user_selections[torrent_id] = {file.path for file in contents}
            await self._bot_svc.send_page_with_files(contents, update, context, page=0)
        elif data == 'done':
            # Selection is done.
            selected_items = self._bot_svc.user_selections.get(torrent_id, set())
            if len(selected_items) == len(contents):
                await query.edit_message_text(text=Messages.all_files_selected)
            elif not selected_items:
                await query.edit_message_text(text=Messages.no_file_selected)
            else:
                text = f'{len(selected_items)} {Messages.files_selected}'
                await query.edit_message_text(text=text)
            await self._bot_svc.save_and_download_user_choice(context)
    
    async def send_message_to_get_acquainted(self, user_tg_id: int) -> None:
        message = error_messages["1"]
        keyboard = [[InlineKeyboardButton(Messages.have_sent_message_to_helper, callback_data="message_sent")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._bot.send_message(
            chat_id=user_tg_id,
            text=message,
            reply_markup=reply_markup,
        )


bot_instance = MainBot()

def main():
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, bot_instance.handle_torrent))
    application.add_handler(CallbackQueryHandler(bot_instance.handle_callback, pattern=r'^(toggle_\d+|page_\d+|select_all|done|message_sent)$'))
    application.add_handler(CallbackQueryHandler(bot_instance.button, pattern=r'^start_pressed$'))
    application.run_polling()

if __name__ == "__main__":
    main()
