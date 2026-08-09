"""
Insère quelques annonces d'exemple pour tester l'API avant que le scraper
(étape 3) ne soit branché.

Usage : depuis backend/, avec le venv activé :
    python -m app.seed_demo_data
"""
from datetime import datetime

from app.core.database import Base, engine, SessionLocal
from app.models.car import Car

DEMO_CARS = [
    dict(source="demo", source_id="demo-1", url="https://example.com/1",
         brand="Toyota", model="Auris Hybrid", year=2018, price=9300, mileage_km=78000,
         fuel_type="hybride", transmission="automatique", location="Bergedorf",
         distance_from_hamburg_km=14, score=94),
    dict(source="demo", source_id="demo-2", url="https://example.com/2",
         brand="Honda", model="Jazz", year=2017, price=7900, mileage_km=91000,
         fuel_type="essence", transmission="manuelle", location="Wandsbek",
         distance_from_hamburg_km=9, score=88),
    dict(source="demo", source_id="demo-3", url="https://example.com/3",
         brand="Skoda", model="Fabia Combi", year=2016, price=6400, mileage_km=132000,
         fuel_type="essence", transmission="manuelle", location="Harburg",
         distance_from_hamburg_km=19, score=76),
    dict(source="demo", source_id="demo-4", url="https://example.com/4",
         brand="Hyundai", model="i30", year=2015, price=5200, mileage_km=148000,
         fuel_type="essence", transmission="manuelle", location="Norderstedt",
         distance_from_hamburg_km=21, score=61),
    dict(source="demo", source_id="demo-5", url="https://example.com/5",
         brand="Volkswagen", model="Golf Variant", year=2017, price=11200, mileage_km=88000,
         fuel_type="diesel", transmission="automatique", location="Altona",
         distance_from_hamburg_km=6, score=82),
]


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        added = 0
        for data in DEMO_CARS:
            exists = db.query(Car).filter(Car.source_id == data["source_id"]).first()
            if exists:
                continue
            db.add(Car(**data, date_added=datetime.utcnow(), date_last_seen=datetime.utcnow()))
            added += 1
        db.commit()
        print(f"{added} annonce(s) de démonstration ajoutée(s).")
    finally:
        db.close()


if __name__ == "__main__":
    run()
