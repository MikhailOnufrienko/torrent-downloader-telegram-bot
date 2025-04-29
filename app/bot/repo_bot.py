# from telegram import Bot

# from app.config import config


# class RepoChat:
#     def __init__(self, bot: type[Bot] = Bot):
#         self._chat_id = config.TELEGRAM_REPO_CHAT_ID
    
#     async def upload_file(self, file_path: str) -> str:
#         with open(file_path, 'rb') as file:
#             # TODO: bots can't send messages to bots
#             message = await self._bot.send_document(chat_id=self._chat_id, document=file)
#         file_id = message.document.file_id
#         file_info = self._bot.get_file(file_id)
#         # file_url = f"https://api.telegram.org/file/bot{config.TELEGRAM_REPO_BOT_TOKEN}/{file_info.file_path}"
#         return file_id
    

# repo_bot = RepoBot()
