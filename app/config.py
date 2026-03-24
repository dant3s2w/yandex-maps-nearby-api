import os

from dotenv import load_dotenv

load_dotenv()

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "your_api_key_here")
YANDEX_GEOCODER_URL = "https://geocode-maps.yandex.ru/1.x/"
