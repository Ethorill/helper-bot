import os
import requests
import telegram
import time
import logging

from dotenv import load_dotenv

logging.basicConfig(level=logging.DEBUG)
load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'

bot = telegram.Bot(token=TELEGRAM_TOKEN)

statuses = ['rejected', 'approved']


def parse_homework_status(homework):
    homework_name = homework.get('homework_name')
    status_work = homework.get('status')
    if homework_name is None or status_work is None:
        logging.error('Не был получин один из параметров')
        return 'У вас проверили работу'

    homework_name = homework_name.split('.')[0]
    if status_work not in statuses:
        logging.error('Мы получили неверный ответ от Яндекса')
    if status_work == statuses[0]:
        verdict = 'К сожалению в работе нашлись ошибки.'
    if status_work == statuses[1]:
        verdict = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    if current_timestamp is None:
        current_timestamp = int(time.time())
    headers = {
        'Authorization': f'OAuth {PRACTICUM_TOKEN}',
    }
    params = {
        'from_date': current_timestamp
    }
    homework_statuses = requests.get(URL, params=params,
                                     headers=headers)
    try:
        return homework_statuses.json()
    except Exception as error:
        logging.info(f'Ошибка {error}')
        logging.error('Что то не так с API')


def send_message(message):
    return bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(new_homework.get('homeworks')[0]))
            current_timestamp = new_homework.get('current_date')
            time.sleep(1140)

        except Exception as e:
            logging.debug(f'Ошибка: {e}')
            logging.error(u'Бот упал :(')
            time.sleep(10)
            continue


if __name__ == '__main__':
    main()
