import httpx

from app.config import YANDEX_API_KEY, YANDEX_GEOCODER_URL

# Типы объектов для Geocoder API
OBJECT_TYPES = {
    "улица": "street",
    "город": "locality",
    "район": "district",
    "метро": "metro",
    "достопримечательность": "house",
    "дом": "house",
    "адрес": "house",
}


async def get_nearby_places(
    lat: float, lon: float, place_type: str = "улица", limit: int = 10
):
    """
    Поиск географических объектов (улиц, городов, районов и т.д.)
    через Яндекс.Геокодер API
    """
    if not YANDEX_API_KEY or YANDEX_API_KEY == "your_api_key_here":
        raise ValueError(
            "YANDEX_API_KEY не настроен."
            "Получите ключ на https://developer.tech.yandex.ru/"
        )

    # Преобразуем тип объекта для API
    kind = OBJECT_TYPES.get(place_type.lower(), "street")

    # Формируем запрос к Geocoder API
    params = {
        "apikey": YANDEX_API_KEY,
        "geocode": f"{lon},{lat}",
        "kind": kind,
        "format": "json",
        "results": limit,
        "lang": "ru_RU",
    }

    # Для некоторых типов добавляем область поиска
    if kind in ["street", "house"]:
        # Для улиц и домов увеличиваем область поиска до 20 км
        params["spn"] = "0.2,0.2"
        params["rspn"] = "0"  # не ограничивать строго
    else:
        # Для городов, районов, метро - стандартная область
        params["spn"] = "0.05,0.05"
        params["rspn"] = "1"

    async with httpx.AsyncClient() as client:
        response = await client.get(YANDEX_GEOCODER_URL, params=params)
        response.raise_for_status()
        data = response.json()

    places = []
    features = (
        data.get("response", {}).get("GeoObjectCollection", {}).get("featureMember", [])
    )

    for feature in features:
        geo_object = feature.get("GeoObject", {})
        meta_data = geo_object.get("metaDataProperty", {}).get("GeocoderMetaData", {})
        coords = geo_object.get("Point", {}).get("pos", "").split()

        # Определяем тип объекта на основе kind из ответа
        kind_info = meta_data.get("kind", "unknown")
        object_type = {
            "street": "улица",
            "locality": "город",
            "district": "район",
            "metro": "станция метро",
            "house": "дом",
            "province": "область",
            "country": "страна",
        }.get(kind_info, kind_info)

        # Фильтруем: для запроса "улица" показываем только улицы
        if place_type.lower() == "улица" and kind_info != "street":
            continue
        if place_type.lower() == "дом" and kind_info != "house":
            continue
        if place_type.lower() == "город" and kind_info != "locality":
            continue
        if place_type.lower() == "район" and kind_info != "district":
            continue
        if place_type.lower() == "метро" and kind_info != "metro":
            continue

        if coords and len(coords) == 2:
            # Вычисляем примерное расстояние (в метрах)
            from math import atan2, cos, radians, sin, sqrt

            lat1, lon1 = lat, lon
            lat2, lon2 = float(coords[1]), float(coords[0])

            R = 6371000  # радиус Земли в метрах
            φ1, φ2 = radians(lat1), radians(lat2)
            Δφ = radians(lat2 - lat1)
            Δλ = radians(lon2 - lon1)

            a = sin(Δφ / 2) ** 2 + cos(φ1) * cos(φ2) * sin(Δλ / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = round(R * c, 1)

            places.append(
                {
                    "name": geo_object.get("name", "Неизвестно"),
                    "address": geo_object.get("description", "Адрес не указан"),
                    "type": object_type,
                    "distance": distance,
                    "coordinates": {
                        "lat": float(coords[1]),
                        "lon": float(coords[0]),
                    },
                }
            )

    # Сортируем по расстоянию
    places.sort(key=lambda x: x["distance"])

    return places
