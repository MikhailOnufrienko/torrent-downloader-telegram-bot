from app.downloader.service import downloader_service


class BotService:
    def __init__(self, downloader_svc=downloader_service):
        self._downl_svc = downloader_service



bot_service = BotService()
