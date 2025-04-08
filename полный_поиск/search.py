import sys
from io import BytesIO
import requests
from PIL import Image
from map_utils import calculate_spn

# Получаем адрес из аргументов командной строки
toponym_to_find = " ".join(sys.argv[1:])

# Запрос к геокодеру
geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
geocoder_params = {
    "apikey": "b2703248-6397-49b6-af1e-d95ab5a1f4b5",
    "geocode": toponym_to_find,
    "format": "json"
}

response = requests.get(geocoder_api_server, params=geocoder_params)
if not response:
    print("Ошибка выполнения запроса к геокодеру")
    sys.exit(1)

json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]

# Получаем координаты центра топонима
toponym_coordinates = toponym["Point"]["pos"]
toponym_longitude, toponym_lattitude = toponym_coordinates.split(" ")

# Вычисляем spn с помощью функции из map_utils.py
spn = calculate_spn(toponym)

# Параметры для запроса к StaticMapsAPI
map_params = {
    "ll": ",".join([toponym_longitude, toponym_lattitude]),
    "spn": spn,
    "l": "map",
    "pt": f"{toponym_longitude},{toponym_lattitude},pm2rdm",  # Добавляем точку
    "apikey": "086592db-32f2-4350-a2a1-a73ad6bae0a0"
}

map_api_server = "https://static-maps.yandex.ru/1.x"
response = requests.get(map_api_server, params=map_params)

# Отображаем картинку
Image.open(BytesIO(response.content)).show()
