"""
Endpoint pour insérer les annonces de démonstration sans avoir besoin d'un
accès shell au serveur (utile sur Render en particulier, où le plan
gratuit ne donne pas de terminal). Pratique pour vérifier que tout le
pipeline frontend <-> backend fonctionne, indépendamment de la fiabilité
du scraping en direct.
"""
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.car import Car
from app.services.scoring import score_all_active_cars

router = APIRouter()

DEMO_CARS = [
    dict(source="demo", source_id="demo-1", url="https://example.com/1",
         brand="Toyota", model="Auris Hybrid", year=2018, price=9300, mileage_km=78000,
         fuel_type="hybride", transmission="automatique", location="Bergedorf",
         distance_from_hamburg_km=14),
    dict(source="demo", source_id="demo-2", url="https://example.com/2",
         brand="Honda", model="Jazz", year=2017, price=7900, mileage_km=91000,
         fuel_type="essence", transmission="manuelle", location="Wandsbek",
         distance_from_hamburg_km=9),
    dict(source="demo", source_id="demo-3", url="https://example.com/3",
         brand="Skoda", model="Fabia Combi", year=2016, price=6400, mileage_km=132000,
         fuel_type="essence", transmission="manuelle", location="Harburg",
         distance_from_hamburg_km=19),
    dict(source="demo", source_id="demo-4", url="https://example.com/4",
         brand="Hyundai", model="i30", year=2015, price=5200, mileage_km=148000,
         fuel_type="essence", transmission="manuelle", location="Norderstedt",
         distance_from_hamburg_km=21),
    dict(source="demo", source_id="demo-5", url="https://example.com/5",
         brand="Volkswagen", model="Golf Variant", year=2017, price=11200, mileage_km=88000,
         fuel_type="diesel", transmission="automatique", location="Altona",
         distance_from_hamburg_km=6),
]


@router.post("/demo")
def seed_demo(db: Session = Depends(get_db)):
    added = 0
    for data in DEMO_CARS:
        exists = db.query(Car).filter(Car.source_id == data["source_id"]).first()
        if exists:
            continue
        db.add(Car(**data, is_active=True, date_added=datetime.utcnow(), date_last_seen=datetime.utcnow()))
        added += 1
    db.commit()

    scored = score_all_active_cars(db)
    return {"added": added, "scored": scored}
