import html
import logging
import os
import random

import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

from create_parser import create_parser
from logs_handler import CustomLogsHandler
from reading_questions import read_questions
from connect_to_db import connect_to_db


logger = logging.getLogger('vk_logger')


def handle_give_up(event, vk_api):
    correct_answer = REDIS_CONNECTION.get(event.user_id).decode('utf-8')
    text = f'Вот тебе правильный ответ: {correct_answer} Чтобы продолжить, нажми "Новый вопрос"'
    add_buttons(event, vk_api, text)

    REDIS_CONNECTION.delete(event.user_id)


def handle_solution_attempt(event, vk_api):
    correct_answer = REDIS_CONNECTION.get(event.user_id)
    if event.text.encode('utf-8') == correct_answer:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
        add_buttons(event, vk_api, message)
        REDIS_CONNECTION.delete(event.user_id)

    else:
        message = 'Неправильно… Попробуешь ещё раз?'
        add_buttons(event, vk_api, message)


def handle_new_question_request(event, vk_api):
    question = REDIS_CONNECTION.randomkey().decode('utf-8')
    answer = REDIS_CONNECTION.get(question)
    REDIS_CONNECTION.set(event.user_id, answer)
    add_buttons(event, vk_api, question)

    return question


def add_buttons(event, vk_api, message):
    keyboard = VkKeyboard(one_time=True)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.POSITIVE)

    keyboard.add_line()
    keyboard.add_button('Мой счет', color=VkKeyboardColor.SECONDARY)

    vk_api.messages.send(
        user_id=event.user_id,
        message=message,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1, 1000)
    )


def cancel(event, vk_api):
    vk_api.messages.send(
        user_id=event.user_id,
        message="Спасибо за участие!",
        random_id=random.randint(1, 1000)
    )


def main():
    load_dotenv()

    parser = create_parser()
    args = parser.parse_args()

    questions_and_answers = read_questions(args.file_path)

    for question, answer in questions_and_answers.items():
        REDIS_CONNECTION.set(question, answer)

    for value in REDIS_CONNECTION.keys():
        print(value.decode('utf-8'))

    vk_group_token = os.getenv("VK_GROUP_TOKEN")
    vk_user_id = os.getenv("VK_USER_ID")

    vk_session = vk.VkApi(token=vk_group_token)

    logger.setLevel(logging.WARNING)
    logger.addHandler(CustomLogsHandler(vk_user_id, None, vk_group_token))

    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    question_q = []
    answer = 0
    for event in longpoll.listen():

        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "/start":
                message = 'Добро пожаловать в викторину! Нажмите "Новый вопрос" для начала викторины!'
                add_buttons(event, vk_api, message)
            if event.text == "Новый вопрос":
                question = handle_new_question_request(event, vk_api)
                question_quot = html.escape(question)
                question_q.append(question_quot)
            if event.text == "Сдаться":
                handle_give_up(event, vk_api)
            if event.text == "/cancel":
                cancel(event, vk_api)
            if answer:
                handle_solution_attempt(event, vk_api)
                answer = 0
        if event.type == VkEventType.MESSAGE_NEW\
                and event.from_me \
                and question_q\
                and event.text == question_q[0]:
            answer = 1
            question_q.remove(question_q[0])


if __name__ == "__main__":
    REDIS_CONNECTION = connect_to_db()
    main()
