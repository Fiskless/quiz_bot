import os

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging

from dotenv import load_dotenv

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""

    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    chat_id = os.getenv("CHAT_ID")
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=chat_id,
                     text="Привет! Я бот для викторин",
                     reply_markup=reply_markup)


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(bot, update):
    """Echo the user message."""

    if update.message.text == "Новый вопрос":
        bot.send_message(chat_id=os.getenv("CHAT_ID"),
                         text="Здесь будет вопрос")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    chat_id = os.getenv("CHAT_ID")

    updater = Updater(bot_token)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(MessageHandler(Filters.text, echo))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
