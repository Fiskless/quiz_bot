import logging
import random
import telegram
import vk_api as vk


class CustomLogsHandler(logging.Handler):
    def __init__(self, chat_id, tg_token=None, vk_token=None):
        super().__init__()
        self.chat_id = chat_id
        self.bot = None
        self.vk_api = None

        if tg_token:
            self.bot = telegram.Bot(token=tg_token)
        if vk_token:
            self.vk_api = vk.VkApi(token=vk_token)

    def emit(self, record):
        log_entry = self.format(record)

        if self.bot:
            self.bot.send_message(
                chat_id=self.chat_id,
                text=log_entry
            )
        if self.vk_api:
            self.vk_api.messages.send(
                user_id=self.chat_id,
                message=log_entry,
                random_id=random.randint(1, 1000)
            )