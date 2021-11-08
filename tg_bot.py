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
from functools import partial


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


def handle_give_up(bot, update, db_connection):

    correct_answer = db_connection.get(f"tg-{update.effective_user['id']}").decode('utf-8')
    text = f'Вот тебе правильный ответ: {correct_answer} Чтобы продолжить, нажми "Новый вопрос"'
    bot.send_message(chat_id=update.effective_user['id'],
                     text=text)
    db_connection.delete(update.effective_user['id'])


def handle_solution_attempt(db_connection, bot, update):

    user_answer = update.message.text
    correct_answer = db_connection.get(f"tg-{update.effective_user['id']}")
    if user_answer.encode('utf-8') == correct_answer:
        bot.send_message(chat_id=update.effective_user['id'],
                        text='Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"')
        db_connection.delete(update.effective_user['id'])
        return QUESTION
    elif user_answer == "Сдаться":
        handle_give_up(bot, update, db_connection)
        return QUESTION
    else:
        bot.send_message(chat_id=update.effective_user['id'],
                         text='Неправильно… Попробуешь ещё раз?')
        return ANSWER


def handle_new_question_request(db_connection, bot, update):

    question = db_connection.randomkey().decode('utf-8')
    answer = db_connection.get(question)
    db_connection.set(f"tg-{update.effective_user['id']}", answer)
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

    redis_connection = connect_to_db()

    for question, answer in questions_and_answers.items():
        redis_connection.set(question, answer)

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")

    updater = Updater(bot_token)

    logger.setLevel(logging.WARNING)
    logger.addHandler(CustomLogsHandler(chat_id, bot_token))

    dp = updater.dispatcher

    handle_question_request_with_db = partial(handle_new_question_request,
                                              redis_connection)
    handle_solution_attempt_with_db = partial(handle_solution_attempt,
                                              redis_connection)

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],

        states={
            QUESTION: [
                RegexHandler('^(Новый вопрос)$',
                             handle_question_request_with_db)],
            ANSWER: [MessageHandler(Filters.text,
                                    handle_solution_attempt_with_db)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(conv_handler)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
