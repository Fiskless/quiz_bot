import argparse


def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'file_path',
        help='Укажите путь к файлу с вопросами и ответами к викторине',
        nargs='?',
        default='quiz_questions/3f15.txt',
        type=str
    )

    return parser
