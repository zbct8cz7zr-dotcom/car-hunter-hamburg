"""
Endpoint pour déclencher un cycle de scraping depuis le frontend
(bouton "Actualiser" par exemple). Le déclenchement automatique périodique
(APScheduler) sera branché à l'étape "Notifications", avec la même fonction
run_scrape en arrière-plan.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.scraper_service import run_scrape

router = APIRouter()


@router.post("/run")
def trigger_scrape(db: Session = Depends(get_db)):
    result = run_scrape(db)
    return {
        "new_listings": result.new_listings,
        "updated_prices": result.updated_prices,
        "deactivated": result.deactivated,
        "blocked_sources": result.blocked_sources,
    }
