import os
import requests
import random
import json
from urllib.parse import quote

from io import BytesIO
from PIL import Image
import logging


class TelegramBot:
    def __init__(self, apikey, chat_id):
        self.apikey = apikey
        self.chat_id = chat_id

    def send_media_group(self, images, caption=None, reply_to_message_id=None):
        send_media_group = f"https://api.telegram.org/bot{self.apikey}/sendMediaGroup"
        files = {}
        media = []
        for i, img in enumerate(images):
            with BytesIO() as output:
                try:
                    img = Image.open(requests.get(img, stream=True).raw)
                    img.save(output, format="PNG")
                    output.seek(0)
                    name = f"photo-{random.random()}-{i}.png"
                    files[name] = output.read()
                    img.save(name)
                    # a list of InputMediaPhoto. attach refers to the name of the file in the files dict
                    media.append(dict(type="photo", media=f"attach://{name}"))
                except Exception as e:
                    pass
        media[0]["caption"] = caption
        resp = requests.post(
            send_media_group,
            data={
                "media": json.dumps(media),
                "chat_id": self.chat_id,
                "reply_to_message_id": reply_to_message_id,
            },
            files=files,
        )
        for img in files.keys():
            os.remove(img)
        return resp

    def send_simple_msg(self, msg):
        room_desc_encoded = quote(msg.encode("utf8"))
        url = f"https://api.telegram.org/bot{self.apikey}/sendMessage?chat_id={self.chat_id}&text={room_desc_encoded}"
        return requests.get(url)

    def send_notification(self, data):
        message = {data.get("message")}

        image_links = []
        for pic in data["pictures"]:
            image_links.append(pic["uri"])
        self.send_media_group(image_links, message)
        room_desc_encoded = quote(data["description"].encode("utf8"))
        url = f"https://api.telegram.org/bot{self.apikey}/sendMessage?chat_id={self.chat_id}&text={room_desc_encoded}"
        requests.get(url).json()

        self.send_location(data["lat"], data["long"])

    def send_location(self, latitude, longitude):
        url = f"https://api.telegram.org/bot{self.apikey}/sendLocation"
        data = {"chat_id": self.chat_id, "latitude": latitude, "longitude": longitude}
        requests.post(url, data=data)
