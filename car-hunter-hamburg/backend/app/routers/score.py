"""
Endpoint pour recalculer les scores manuellement — utile après avoir
modifié BRAND_RELIABILITY, ou pour re-scorer les annonces de démo sans
relancer tout le scraping.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.scoring import score_all_active_cars

router = APIRouter()


@router.post("/run")
def trigger_scoring(db: Session = Depends(get_db)):
    updated = score_all_active_cars(db)
    return {"status": "ok", "cars_scored": updated}
