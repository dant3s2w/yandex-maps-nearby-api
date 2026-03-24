from fastapi import FastAPI

from app.api.endpoints import router

app = FastAPI(
    title="Yandex Maps Nearby API",
    description="REST API для поиска ближайших объектов через Яндекс.Карты",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1", tags=["places"])


@app.get("/")
async def root():
    return {
        "message": "Yandex Maps Nearby API",
        "docs": "/docs",
        "redoc": "/redoc",
    }
