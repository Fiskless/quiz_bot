import html
import logging
import os
import random

import vk_api as vk
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.longpoll import VkLongPoll, VkEventType
from dotenv import load_dotenv

from logs_handler import CustomLogsHandler
from reading_questions import read_questions
from tg_bot import connect_to_db


logger = logging.getLogger('vk_logger')


def handle_give_up(event, vk_api):
    correct_answer = redis_connection.get(
        redis_connection.get(event.user_id)).decode('utf-8')
    text = f'Вот тебе правильный ответ: {correct_answer} Чтобы продолжить, нажми "Новый вопрос"'
    add_button(event, vk_api, text)

    redis_connection.delete(event.user_id)


def handle_solution_attempt(event, vk_api):
    user_answer = event.text
    correct_answer = redis_connection.get(redis_connection.get(event.user_id))
    if user_answer.encode('utf-8') == correct_answer:
        message = 'Правильно! Поздравляю! Для следующего вопроса нажми "Новый вопрос"'
        add_button(event, vk_api, message)
        redis_connection.delete(event.user_id)

    else:
        message = 'Неправильно… Попробуешь ещё раз?'
        add_button(event, vk_api, message)


def handle_new_question_request(event, vk_api):
    question = redis_connection.randomkey().decode('utf-8')
    redis_connection.set(event.user_id, question)
    add_button(event, vk_api, question)

    return question


def add_button(event, vk_api, message):
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

    questions_and_answers = read_questions('3f15')

    global redis_connection
    redis_connection = connect_to_db()
    for question, answer in questions_and_answers.items():
        redis_connection.set(question, answer)

    vk_group_token = os.getenv("VK_GROUP_TOKEN")
    vk_user_id = os.getenv("VK_USER_ID")

    vk_session = vk.VkApi(token=vk_group_token)

    logger.setLevel(logging.WARNING)
    logger.addHandler(CustomLogsHandler(vk_user_id, None, vk_group_token))

    vk_api = vk_session.get_api()

    longpoll = VkLongPoll(vk_session)
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            if event.text == "/start":
                message = 'Добро пожаловать в викторину! Нажмите "Новый вопрос" для начала викторины!'
                add_button(event, vk_api, message)
            if event.text == "Новый вопрос":
                question = handle_new_question_request(event, vk_api)
                question_quot = html.escape(question)
                print(question_quot)
            if event.text == "Сдаться":
                handle_give_up(event, vk_api)
            if event.text == "/cancel":
                cancel(event, vk_api)
        # if event.type == VkEventType.MESSAGE_NEW and event.from_me:
        #     print(event.text)
        #     print(event.text==question_quot)
        #     if event.text == question_quot:
        #         print('close')
        #     #     handle_solution_attempt(event, vk_api)


if __name__ == "__main__":
    main()
