"""
Endpoint /api/history — alimente la page "Historique" du frontend :
baisses de prix récentes et annonces devenues inactives (retirées par
le vendeur).
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.car import Car
from app.models.price_history import PriceHistory
from app.schemas.price_history import PriceHistoryEntry
from app.schemas.car import CarOut

router = APIRouter()


@router.get("/price-drops", response_model=list[PriceHistoryEntry])
def price_drops(db: Session = Depends(get_db), limit: int = Query(30, le=100)):
    rows = (
        db.query(PriceHistory, Car.brand, Car.model)
        .join(Car, Car.id == PriceHistory.car_id)
        .order_by(PriceHistory.date.desc())
        .limit(limit)
        .all()
    )
    return [
        PriceHistoryEntry(
            id=ph.id, car_id=ph.car_id, old_price=ph.old_price, new_price=ph.new_price,
            date=ph.date, car_brand=brand, car_model=model,
        )
        for ph, brand, model in rows
    ]


@router.get("/removed", response_model=list[CarOut])
def recently_removed(db: Session = Depends(get_db), limit: int = Query(30, le=100)):
    """Annonces retirées récemment (probablement vendues ou dépubliées)."""
    return (
        db.query(Car)
        .filter(Car.is_active.is_(False))
        .order_by(Car.date_last_seen.desc())
        .limit(limit)
        .all()
    )
