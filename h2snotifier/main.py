import logging

from dotenv import dotenv_values

from db import create_table, sync_houses
from scrape import scrape, house_to_msg
from telegram import TelegramBot
import json

env = dotenv_values(".env")
TELEGRAM_API_KEY = env.get("TELEGRAM_API_KEY")
DEBUGGING_CHAT_ID = env.get("DEBUGGING_CHAT_ID")

debug_telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=DEBUGGING_CHAT_ID)


def read_config(config_path="config.json"):
    with open(config_path) as f:
        return json.load(f)


def main():
    create_table()
    config = read_config("config.json")
    for gp in config["telegram"]["groups"]:
        cities = gp["cities"]
        chat_id = gp["chat_id"]
        telegram = TelegramBot(apikey=TELEGRAM_API_KEY, chat_id=chat_id)
        houses_in_cities = scrape(cities=cities)
        for city_id, houses in houses_in_cities.items():
            new_houses = sync_houses(city_id=city_id, houses=houses)

            for h in new_houses:
                try:
                    if len(h['images']) > 0:
                        telegram.send_media_group(h['images'][:4], house_to_msg(h))
                    else:
                        telegram.send_simple_msg(house_to_msg(h))
                    logging.info(f"Sent telegram Notif for {h['url_key']}")
                except Exception as error:
                    debug_telegram.send_simple_msg(f"Sending notification failed! {h}")
                    debug_telegram.send_simple_msg(str(error))
                    logging.info(f"Sending notification failed! {h}")
                    logging.info(str(error))


if __name__ == "__main__":
    main()
