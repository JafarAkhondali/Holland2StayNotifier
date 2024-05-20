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
                    media.append(dict(type="photo", media=f"attach://{name}"))
                except Exception as e:
                    logging.error(f"Error processing image: {img}, Error: {e}")
                    debug_telegram.send_simple_msg(f"Error processing image: {img}")
                    debug_telegram.send_simple_msg(str(e))
                    continue
        if media:
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
        else:
            return None

    def send_simple_msg(self, msg):
        room_desc_encoded = quote(msg.encode("utf8"))
        url = f"https://api.telegram.org/bot{self.apikey}/sendMessage?chat_id={self.chat_id}&text={room_desc_encoded}"
        return requests.get(url)