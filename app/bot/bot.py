from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from app.bot.messages import Messages
from app.bot.service import BotService, bot_service
from app.config import config


class Bot:
    def __init__(
        self,
        bot_service: BotService = bot_service,
    ):
        self._bot_svc = bot_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user = update.message.from_user
        await self._bot_svc.save_user_if_not_exists(user)
        keyboard = [[InlineKeyboardButton("Start", callback_data="start_pressed")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(Messages.hello, reply_markup=reply_markup)

    async def button(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(Messages.invitation)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        message = update.message
        if message.text and message.text.lower().startswith('magnet'):
            magnet_link = message.text
            info_hash = None
            await update.message.reply_text(Messages.link_received)
        elif message.document:
            file = message.document
            await update.message.reply_text(Messages.file_received)
            info_hash, magnet_link = self._bot_svc.generate_hash_and_magnet_link_from_file(file)
        else:
            await update.message.reply_text(Messages.invitation_after_error)
            return
        await self._bot_svc.save_torrent_and_contents(update.message.from_user['id'], magnet_link, info_hash)
        # if torrent:
        #     torrent_files_hierarchy = await self._bot_svc.construct_torrent_files_hierarchy(info_hash)
        #     config.logger.debug(torrent_files_hierarchy)


def main():
    bot_instance = Bot()
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", bot_instance.start))
    application.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, bot_instance.handle_message))
    application.add_handler(CallbackQueryHandler(bot_instance.button))
    application.run_polling()

if __name__ == "__main__":
    main()
