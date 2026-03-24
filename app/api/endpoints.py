import logging
from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.models.schemas import ErrorResponse, PlaceResponse
from app.services.yandex_maps import get_nearby_places

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/nearby",
    response_model=List[PlaceResponse],
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    summary="Поиск географических объектов",
    description="Возвращает список ближайших географических объектов "
                "(улиц, городов, районов, метро и т.д.)",
)
async def get_nearby_places_endpoint(
    lat: float = Query(..., description="Широта", examples=[55.7558]),
    lon: float = Query(..., description="Долгота", examples=[37.6173]),
    type: str = Query(
        "улица",
        description="Тип объекта: улица, город, район, метро, дом, достопримечательность",
    ),
    limit: int = Query(10, description="Количество результатов", ge=1, le=50),
):
    try:
        places = await get_nearby_places(lat, lon, type, limit)
        return places
    except ValueError as e:
        logger.error(f"Ошибка конфигурации: {e}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Ошибка конфигурации API", "details": str(e)},
        )
    except Exception as e:
        logger.error(f"Ошибка при запросе к Яндекс API: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Ошибка при запросе к Яндекс.Картам", "details": str(e)},
        )
