"""
Schémas Pydantic : forme des données échangées par l'API.
Séparés des modèles SQLAlchemy pour ne jamais exposer la structure
de la base de données telle quelle (bonne pratique de sécurité/évolutivité).
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CarBase(BaseModel):
    brand: str
    model: str
    year: Optional[int] = None
    price: int
    mileage_km: int
    fuel_type: Optional[str] = None
    transmission: Optional[str] = None
    location: Optional[str] = None
    distance_from_hamburg_km: Optional[float] = None
    url: str


class CarOut(CarBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source: str
    power_kw: Optional[int] = None
    owners_count: Optional[int] = None
    consumption_l_100km: Optional[float] = None
    image_url: Optional[str] = None
    score: Optional[int] = None
    ai_analysis: Optional[str] = None
    is_active: bool
    date_added: datetime
    date_last_seen: datetime


class CarListResponse(BaseModel):
    total: int
    items: list[CarOut]
