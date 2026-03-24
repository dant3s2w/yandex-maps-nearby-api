from pydantic import BaseModel


class Coordinates(BaseModel):
    lat: float
    lon: float


class PlaceResponse(BaseModel):
    name: str
    address: str
    type: str  # тип объекта: улица, город, район и т.д.
    distance: float
    coordinates: Coordinates


class ErrorResponse(BaseModel):
    error: str
    details: str = None
