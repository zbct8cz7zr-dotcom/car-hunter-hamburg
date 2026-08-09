from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PriceHistoryEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    car_id: int
    old_price: int
    new_price: int
    date: datetime
    # Enrichis manuellement dans le router (pas des colonnes de PriceHistory)
    car_brand: str
    car_model: str
