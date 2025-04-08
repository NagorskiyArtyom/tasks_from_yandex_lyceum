import sys
from io import BytesIO
import requests
from PIL import Image
import math

# Получаем адрес из аргументов командной строки
toponym_to_find = " ".join(sys.argv[1:])

# Геокодирование исходного адреса
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

# Координаты исходного адреса
address_coords = toponym["Point"]["pos"]
address_longitude, address_latitude = address_coords.split(" ")
address_ll = f"{address_longitude},{address_latitude}"

# Поиск ближайшей аптеки
search_api_server = "https://search-maps.yandex.ru/v1/"
search_params = {
    "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
    "text": "аптека",
    "lang": "ru_RU",
    "ll": address_ll,
    "type": "biz",
    "results": 1  # Ищем только ближайшую
}

response = requests.get(search_api_server, params=search_params)
if not response:
    print("Ошибка поиска аптеки")
    sys.exit(1)

json_response = response.json()
organization = json_response["features"][0]
org_name = organization["properties"]["CompanyMetaData"]["name"]
org_address = organization["properties"]["CompanyMetaData"]["address"]
org_hours = organization["properties"]["CompanyMetaData"].get("Hours", {}).get("text", "Время работы не указано")

# Координаты аптеки
pharmacy_point = organization["geometry"]["coordinates"]
pharmacy_ll = f"{pharmacy_point[0]},{pharmacy_point[1]}"

# Расчёт расстояния


def calculate_distance(lon1, lat1, lon2, lat2):
    # Приблизительный расчёт расстояния в метрах
    dx = abs(float(lon1) - float(lon2))
    dy = abs(float(lat1) - float(lat2))
    return round(math.sqrt(dx*dx + dy*dy), 1)


distance = calculate_distance(address_longitude, address_latitude, pharmacy_point[0], pharmacy_point[1])

# Формирование сниппета
snippet = f"""
Найденная аптека:
Название: {org_name}
Адрес: {org_address}
Время работы: {org_hours}
Расстояние от заданного адреса: {distance} м
"""
print(snippet)

# Построение карты
# Автоматическое позиционирование карты по двум точкам


def get_map_spn(coords1, coords2):
    lon1, lat1 = map(float, coords1.split(','))
    lon2, lat2 = map(float, coords2.split(','))
    delta_lon = abs(lon1 - lon2) * 1.5
    delta_lat = abs(lat1 - lat2) * 1.5
    return f"{delta_lon},{delta_lat}"


map_params = {
    "ll": f"{(float(address_longitude) + float(pharmacy_point[0]))/2},"
          f"{(float(address_latitude) + float(pharmacy_point[1]))/2}",
    "spn": get_map_spn(address_ll, pharmacy_ll),
    "l": "map",
    "pt": f"{address_ll},pm2rdl~{pharmacy_ll},pm2gnl",  # Разные метки
    "apikey": "086592db-32f2-4350-a2a1-a73ad6bae0a0"
}

map_api_server = "https://static-maps.yandex.ru/1.x"
response = requests.get(map_api_server, params=map_params)

# Отображение карты
Image.open(BytesIO(response.content)).show()
