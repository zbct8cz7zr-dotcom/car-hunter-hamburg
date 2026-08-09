"""
Endpoints /api/cars — consultation des annonces.
La création/mise à jour des annonces se fera depuis le scraper (étape 3),
pas via ces endpoints publics : on garde ici uniquement la lecture et les
actions utilisateur (masquer une annonce, etc.).
"""
from typing import Optional, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.car import Car
from app.schemas.car import CarOut, CarListResponse

router = APIRouter()

SortField = Literal["score", "price", "mileage_km", "date_added"]


@router.get("", response_model=CarListResponse)
def list_cars(
    db: Session = Depends(get_db),
    budget_max: Optional[int] = Query(None, description="Prix maximum en €"),
    km_max: Optional[int] = Query(None, description="Kilométrage maximum"),
    radius_km: Optional[float] = Query(None, description="Distance max depuis Hambourg"),
    fuel_types: Optional[str] = Query(None, description="CSV, ex: essence,hybride"),
    brands: Optional[str] = Query(None, description="CSV, ex: toyota,honda"),
    min_score: Optional[int] = Query(None, ge=0, le=100),
    sort: SortField = "score",
    order: Literal["asc", "desc"] = "desc",
    active_only: bool = True,
    limit: int = Query(50, le=200),
    offset: int = 0,
):
    """
    Liste des annonces, filtrée et triée.
    C'est cet endpoint que le frontend appellera pour peupler le Dashboard
    et la page Annonces, avec les critères choisis dans UserSettings.
    """
    q = db.query(Car)

    if active_only:
        q = q.filter(Car.is_active.is_(True))
    if budget_max is not None:
        q = q.filter(Car.price <= budget_max)
    if km_max is not None:
        q = q.filter(Car.mileage_km <= km_max)
    if radius_km is not None:
        q = q.filter(Car.distance_from_hamburg_km <= radius_km)
    if min_score is not None:
        q = q.filter(Car.score >= min_score)
    if fuel_types:
        wanted = [f.strip().lower() for f in fuel_types.split(",") if f.strip()]
        if wanted:
            q = q.filter(Car.fuel_type.ilike(f"%{wanted[0]}%")) if len(wanted) == 1 else q.filter(
                Car.fuel_type.in_(wanted)
            )
    if brands:
        wanted = [b.strip().lower() for b in brands.split(",") if b.strip()]
        if wanted:
            q = q.filter(Car.brand.ilike(f"%{wanted[0]}%")) if len(wanted) == 1 else q.filter(
                Car.brand.in_(wanted)
            )

    total = q.count()

    sort_col = getattr(Car, sort)
    q = q.order_by(sort_col.desc() if order == "desc" else sort_col.asc())
    items = q.offset(offset).limit(limit).all()

    return CarListResponse(total=total, items=items)


@router.get("/{car_id}", response_model=CarOut)
def get_car(car_id: int, db: Session = Depends(get_db)):
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    return car


@router.delete("/{car_id}")
def hide_car(car_id: int, db: Session = Depends(get_db)):
    """Masque une annonce (suppression logique, jamais de suppression réelle
    pour garder l'historique des prix cohérent)."""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(status_code=404, detail="Annonce introuvable")
    car.is_active = False
    db.commit()
    return {"status": "ok", "id": car_id, "is_active": False}
