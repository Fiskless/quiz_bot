# -*- coding: utf-8 -*-

import logging
import os


import telegram
from dotenv import load_dotenv
from telegram.ext import (CommandHandler, ConversationHandler, Filters,
                          MessageHandler, RegexHandler, Updater)

from logs_handler import CustomLogsHandler
from reading_questions import read_questions
from connect_to_db import connect_to_db
from create_parser import create_parser


logger = logging.getLogger('tg_logger')

QUESTION, ANSWER = range(2)


def start(bot, update):
    """Send a message when the command /start is issued."""

    custom_keyboard = [['Новый вопрос', 'Сдаться'], ['Мой счет']]
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.effective_user['id'],
                     text="Привет! Я бот для викторин",
                     reply_markup=reply_markup)

    return QUESTION


def handle_give_up(bot, update):
    correct_answer = REDIS_CONNECTION.get(update.effective_user['id']).decode('utf-8')
    text = f'Вот тебе правильный ответ: {correct_answer} Чтобы продолжить, нажми "Новый вопрос"'
    bot.send_message(chat_id=update.effective_user['id'],
                     text=text)
    REDIS_CONNECTION.delete(update.effective_user['id'])


def handle_solution_attempt(bot, update):
    user_answer = update.message.text
    correct_answer = REDIS_CONNECTION.get(update.effective_user['id'])
    if user_answer.encode('utf-8') == correct_answer:
        bot.send_message(chat_id=update.effective_user['id'],
                        text='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
        REDIS_CONNECTION.delete(update.effective_user['id'])
        return QUESTION
    elif user_answer == "Сдаться":
        handle_give_up(bot, update)
        return QUESTION
    else:
        bot.send_message(chat_id=update.effective_user['id'],
                         text='Неправильно… Попробуешь ещё раз?')
        return ANSWER


def handle_new_question_request(bot, update):
    question = REDIS_CONNECTION.randomkey().decode('utf-8')
    answer = REDIS_CONNECTION.get(question)
    REDIS_CONNECTION.set(update.effective_user['id'], answer)
    bot.send_message(chat_id=update.effective_user['id'],
                     text=question)
    return ANSWER


def cancel(bot, update):
    update.message.reply_text('Команда завершения бота викторины')

    return ConversationHandler.END


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def main():
    """Start the bot."""
    load_dotenv()

    parser = create_parser()
    args = parser.parse_args()

    questions_and_answers = read_questions(args.file_path)

    for question, answer in questions_and_answers.items():
        REDIS_CONNECTION.set(question, answer)

    # for key in REDIS_CONNECTION.keys():
    #     REDIS_CONNECTION.delete(key)
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    updater = Updater(bot_token)

    logger.setLevel(logging.WARNING)
    logger.addHandler(CustomLogsHandler(chat_id, bot_token))

    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            QUESTION: [
                RegexHandler('^(Новый вопрос)$', handle_new_question_request)],
            ANSWER: [MessageHandler(Filters.text, handle_solution_attempt)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    REDIS_CONNECTION = connect_to_db()
    main()
