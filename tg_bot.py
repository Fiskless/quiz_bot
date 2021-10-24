# -*- coding: utf-8 -*-

import os

import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, \
    ConversationHandler, RegexHandler
import logging
import redis

from dotenv import load_dotenv
from reading_questions import read_questions

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

CHOOSING, ANSWER = range(2)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""

    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.effective_user['id'],
                     text="Привет! Я бот для викторин",
                     reply_markup=reply_markup)

    return CHOOSING


def handle_give_up(bot, update):
    correct_answer = redis_connection.get(
        redis_connection.get(update.effective_user['id'])).decode('utf-8')
    text = f'Вот тебе правильный ответ: {correct_answer} Чтобы продолжить, нажми "Новый вопрос"'
    bot.send_message(chat_id=update.effective_user['id'],
                     text=text)
    redis_connection.delete(update.effective_user['id'])
    return CHOOSING


def handle_solution_attempt(bot, update):
    user_answer = update.message.text
    correct_answer = redis_connection.get(redis_connection.get(update.effective_user['id']))
    if user_answer.encode('utf-8') == correct_answer:
        bot.send_message(chat_id=update.effective_user['id'],
                        text='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
        redis_connection.delete(update.effective_user['id'])
    else:
        bot.send_message(chat_id=update.effective_user['id'],
                         text='Неправильно… Попробуешь ещё раз?')
    return CHOOSING


def handle_new_question_request(bot, update):
    question = redis_connection.randomkey().decode('utf-8')
    redis_connection.set(update.effective_user['id'], question)
    bot.send_message(chat_id=update.effective_user['id'],
                     text=question)
    return ANSWER


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def cancel(bot, update):
    user = update.message.from_user
    logger.info("User %s canceled the quiz.", user.first_name)
    update.message.reply_text('Команда завершения бота викторины')

    return ConversationHandler.END


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main():
    """Start the bot."""
    load_dotenv()

    questions_and_answers = read_questions('3f15')
    redis_host = os.getenv("REDIS_HOST")
    redis_port = os.getenv("REDIS_PORT")
    redis_password = os.getenv("REDIS_PASSWORD")

    global redis_connection
    redis_connection = redis.Redis(host=redis_host,
                                   port=redis_port,
                                   password=redis_password)
    for question, answer in questions_and_answers.items():
        redis_connection.set(question, answer)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    updater = Updater(bot_token)

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            CHOOSING: [
                RegexHandler('^(Новый вопрос)$',
                             handle_new_question_request),
                RegexHandler('^(Сдаться)$',
                             handle_give_up)],
            ANSWER: [MessageHandler(Filters.text, handle_solution_attempt)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(conv_handler)

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
