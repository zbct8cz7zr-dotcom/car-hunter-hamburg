"""
Endpoints /api/settings — les critères de recherche (le panneau "Critères"
côté frontend). Un seul enregistrement UserSettings pour l'instant
(un utilisateur unique) : on le crée avec des valeurs par défaut au
premier appel s'il n'existe pas encore.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import get_settings
from app.models.user_settings import UserSettings
from app.schemas.user_settings import UserSettingsOut, UserSettingsUpdate

router = APIRouter()


def _get_or_create(db: Session) -> UserSettings:
    settings = db.query(UserSettings).first()
    if settings is None:
        defaults = get_settings()
        settings = UserSettings(
            budget_max=defaults.default_budget_max,
            km_max=defaults.default_km_max,
            radius_km=defaults.default_radius_km,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


@router.get("", response_model=UserSettingsOut)
def read_settings(db: Session = Depends(get_db)):
    return _get_or_create(db)


@router.patch("", response_model=UserSettingsOut)
def update_settings(payload: UserSettingsUpdate, db: Session = Depends(get_db)):
    settings = _get_or_create(db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(settings, field, value)
    db.commit()
    db.refresh(settings)
    return settings
