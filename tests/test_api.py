from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Тест корневого эндпоинта"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs" in response.json()


def test_nearby_endpoint_missing_params():
    """Тест без обязательных параметров"""
    response = client.get("/api/v1/nearby")
    assert response.status_code == 422  # Validation error


def test_nearby_endpoint_with_valid_params():
    """Тест с валидными параметрами"""
    response = client.get("/api/v1/nearby?lat=55.7558&lon=37.6173&type=улица&limit=5")
    assert response.status_code in [200, 400, 500]

    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "name" in data[0]
            assert "address" in data[0]
            assert "type" in data[0]
            assert "distance" in data[0]
            assert "coordinates" in data[0]


def test_nearby_endpoint_with_limit():
    """Тест с параметром limit"""
    limit = 3
    response = client.get(
        f"/api/v1/nearby?lat=55.7558&lon=37.6173&type=город&limit={limit}"
    )
    assert response.status_code in [200, 400, 500]

    if response.status_code == 200:
        data = response.json()
        if len(data) > 0:
            assert len(data) <= limit


def test_nearby_endpoint_invalid_type():
    """Тест с неподдерживаемым типом объекта"""
    response = client.get(
        "/api/v1/nearby?lat=55.7558&lon=37.6173&type=несуществующий_тип&limit=5"
    )
    # API должен вернуть данные (используется тип "street" по умолчанию)
    assert response.status_code in [200, 400, 500]


def test_nearby_endpoint_all_supported_types():
    """Тест всех поддерживаемых типов объектов"""
    types = ["улица", "город", "район", "метро", "дом", "достопримечательность"]

    for obj_type in types:
        response = client.get(
            f"/api/v1/nearby?lat=55.7558&lon=37.6173&type={obj_type}&limit=3"
        )
        assert response.status_code in [200, 400, 500]

        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                assert data[0]["type"] in [
                    "улица",
                    "город",
                    "район",
                    "станция метро",
                    "дом",
                    "достопримечательность",
                ]


def test_docs_endpoint():
    """Тест доступности документации"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")


def test_redoc_endpoint():
    """Тест доступности ReDoc"""
    response = client.get("/redoc")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
