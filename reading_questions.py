from contextlib import suppress


def read_questions(filename):
    filepath = f"quiz_questions/{filename}.txt"
    with open(filepath, "r", encoding='KOI8-R') as file:
        quiz = file.read()

    questions_and_answers = {}
    quiz_content = quiz.split("\n\n")
    for content_index, content in enumerate(quiz_content):
        with suppress(ValueError):
            header, question_or_answer_content = content.split(':\n')
            if header.startswith("Вопрос"):
                _, answer = quiz_content[content_index + 1].split(":\n")
                questions_and_answers[question_or_answer_content] = answer

    return questions_and_answers
