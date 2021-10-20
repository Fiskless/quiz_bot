# -*- coding: koi8-r -*-
from contextlib import suppress


def main():
    with open("quiz_questions/3f15.txt", "r", encoding='KOI8-R') as file:
        quiz = file.read()

    questions_and_answers = {}
    quiz_content = quiz.split("\n\n")
    for content_index, content in enumerate(quiz_content):
        with suppress(ValueError):
            header, lining = content.split(':')
            if header.startswith("Вопрос"):
                # print(header)
                _, answer = quiz_content[content_index+1].split(":")
                questions_and_answers[lining] = answer

    print(type(questions_and_answers))


if __name__ == '__main__':
    main()
