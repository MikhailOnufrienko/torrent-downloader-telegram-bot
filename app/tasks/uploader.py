from pyrogram.client import Client
from telegram import Bot

from app.config import config


class TGUploader:
    # def __init__(self, bot: Bot = Bot(config.TELEGRAM_BOT_TOKEN, base_url=config.TELEGRAM_BOT_URL)):
    def __init__(self, bot: Bot = Bot(config.TELEGRAM_BOT_TOKEN)):
        self._bot = bot
        self._chat_id = config.TELEGRAM_REPO_CHAT_ID
        self._tg_api_id = config.TELEGRAM_API_ID
        self._tg_api_hash = config.TELEGRAM_API_HASH

    async def upload_file(self, file_path: str) -> str | None:
        try:
            async with Client("contents_uploader", api_id=self._tg_api_id, api_hash=self._tg_api_hash) as app:
                # async for dialog in app.get_dialogs():
                #     print(dialog.chat.id, dialog.chat.title, dialog.chat.username)
                message = await app.send_document(
                    chat_id=self._chat_id,
                    document=file_path,
                )
                if not message:
                    print(f"! TGUploader Error !: Attempt to upload file {file_path} failed: return message is None!")
                    return
        except FileNotFoundError:
            print(f"! TGUploader Error !: File {file_path} not found!")
            return
        file_id = message.document.file_id
        file_path = await app.download_media(file_id)
        file_url = f"https://api.telegram.org/file/bot{config.TELEGRAM_BOT_TOKEN}/{file_path}"
        print(file_url)
        return file_url


tg_uploader = TGUploader()

if __name__ == "__main__":
    import asyncio
    asyncio.run(tg_uploader.upload_file("/home/mikhail/Downloads/code_1.95.2-1730981514_amd64.deb"))
