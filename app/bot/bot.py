from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler,
                          ContextTypes, MessageHandler, filters)

from app.bot.messages import Messages
from app.bot.service import bot_service
from app.config import config


class Bot:
    def __init__(self, bot_service=bot_service):
        self._bot_svc = bot_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
            await update.message.reply_text(Messages.link_received)
            resp = await self._bot_svc.process_magnet_link(magnet_link)
        elif message.document:
            file = message.document
            await update.message.reply_text(Messages.file_received)
            info_hash, magnet_link = bot_service.generate_hash_and_magnet_link_from_file(file)
            resp = await self._bot_svc.process_magnet_link(magnet_link, info_hash)

        else:
            await update.message.reply_text(Messages.invitation_after_error)


def main():
    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", Bot.start))
    application.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, Bot.handle_message))
    application.add_handler(CallbackQueryHandler(Bot.button))
    application.run_polling()

if __name__ == "__main__":
    main()
