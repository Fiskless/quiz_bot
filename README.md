# Викторина

Данный проект состоит из двух ботов. Данные боты позволяют пользователю пройти викторину. Один бот выполнен в телеграмме(@fiskless_quiz_bot), другой во [ВКонтакте](https://vk.com/im?sel=-208206433) 
Данный проект запущен на сервере [Heroku](https://id.heroku.com/login)

## Запуск

Для запуска скрипта у вас уже должен быть установлен Python 3.

- Скачайте код
- Установите зависимости командой
    ```sh
    pip install -r requirements.txt
    ```
- Запуск бота в ВК производится командой: 
    ```sh
    python3 vk_bot.py
    ```
- Запуск бота в телеграмме производится командой: 
    ```sh
    python3 tg_bot.py
    ```

## Переменные окружения

Часть настроек проекта берётся из переменных окружения. 
Чтобы их определить, создайте файл `.env` рядом с `main.py` 
и запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Используются следующие переменные окружения: 
- `TELEGRAM_BOT_TOKEN` - токен, созданного вами Telegram-бота для оповещений о проверке работ. Чтобы его получить, необходимо написать Отцу ботов в Telegram(@BotFather). 
Отец ботов попросит ввести два имени. Первое — как он будет отображаться в списке контактов, можно написать на русском. Второе — имя, по которому бота можно будет найти в поиске. Должно быть английском и заканчиваться на bot (например, notification_bot)
- `VK_GROUP_TOKEN` - это ваш персональный токен созданной вами группы ВКонтакте.  Для его получения зайдите в вашу группу ВК -> вкладка Управление в правой части страницы -> Настройки -> Работа с API -> Создать ключ.
- `REDIS_HOST` - адрес базы данных Redis, для его получения необходимо создать [базу данных](https://redis.com/)
- `REDIS_PORT` - порт вашей базы даннах
- `REDIS_PASSWORD` - пароль для подключения к базе данных
- `CHAT_ID` - для его получения необходимо написать в Telegram специальному боту: @userinfobot
- `VK_USER_ID` - ваш id во ВКонтакте. Нужен для того, чтобы в случае ошибки бот вам написал.


## Функционал проекта

Пример работы бота в телеграмм:

![Image alt](https://github.com/Fiskless/quiz_bot/blob/master/demo%20bots/tg_bot_demo.gif)

Пример работы бота в ВК:

![Image alt](https://github.com/Fiskless/quiz_bot/blob/master/demo%20bots/vk_bot_demo.gif)

### Возможности скрипта reading_questions

В данном скрипте прописана функция, которая считывает данные для викторины и 
преобразует их в подходящий для дальнейшего использования вид. Все файлы с 
вопросами для викторины, находятся [здесь](https://dvmn.org/media/modules_dist/quiz-questions.zip).
В данном случае, функция создает словарь, в котором ключ - это текст вопроса, а значение - ответ
на вопрос. Далее эти данные помещаются в базу данных [redis](https://redis.com/).


## Инструкция по запуску на сервере

- Зарегистрироваться на [Heroku](https://id.heroku.com/login) и создать приложение
- Привязать аккаунт Github к аккаунту Heroku на вкладке Deploy. Потом найдите свой репозиторий с помощью поиска и подключите его к Heroku.
- Отредактировать файл Procfile в репозитории, чтобы он был следующего вида:
  ```sh
      bot-vk: python3 название_бота_вконтакте.py
      bot-tg: python3 название_бота_телеграмм.py
  ```
- На вкладке Settings вашего приложения в графе Config Vars добавить переменные окружения из вашего ранее созданного .env файла.
- Установите себе консольный клиент [Heroku LCI](https://devcenter.heroku.com/articles/heroku-cli#download-and-install). Он покажет, есть ли какие-либо ошибки, мешающие запуску скрипта на сервере
- На вкладке Deploy вашего приложения в графе Manual Deploy нажмите Deploy Branch. 
- Наслаждайтесь работой скрипта. В случае каких-либо ошибок загляните в Heroku LCI.


## Цели проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).