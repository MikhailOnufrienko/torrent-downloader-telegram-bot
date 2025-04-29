from telegram import Bot

from app.config import config


class TGUploader:
    def __init__(self, bot: Bot = Bot(config.TELEGRAM_BOT_TOKEN, base_url="http://localhost:8081/")):
        self._bot = bot
        self._chat_id = config.TELEGRAM_REPO_CHAT_ID
    
    async def upload_file(self, file_path: str) -> str:
        with open(file_path, 'rb') as file:
            try:
                message = await self._bot.send_audio(chat_id=self._chat_id, audio=file, timeout)
            except Exception:
                print('Timeout')
        file_id = message.document.file_id
        file_info = self._bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{self._bot}/{file_info.file_path}"
        print(file_url)
        return file_url


tg_uploader = TGUploader()
