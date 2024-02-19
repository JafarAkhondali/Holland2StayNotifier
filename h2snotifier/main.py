import logging

from dotenv import dotenv_values

from db import create_table, sync_houses
from scrape import scrape, house_to_msg
from telegram import TelegramBot
import json

env = dotenv_values(".env")
TELEGRAM_API_KEY = env.get('TELEGRAM_API_KEY')


def read_config(config_path='config.json'):
    with open(config_path) as f:
        return json.load(f)


def main():
    create_table()
    config = read_config('config.json')
    for gp in config['telegram']['groups']:
        cities = gp['cities']
        chat_id = gp['chat_id']
        telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=chat_id)
        houses_in_cities = scrape(cities=cities)
        for city_id, houses in houses_in_cities.items():
            new_houses = sync_houses(city_id=city_id, houses=houses)

            for h in new_houses:
                telegram.send_simple_msg(house_to_msg(h))
                logging.info(f"Sent telegram Notif for {h['url_key']}")


if __name__ == "__main__":
    main()
