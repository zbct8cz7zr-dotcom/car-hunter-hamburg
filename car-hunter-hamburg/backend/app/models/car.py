"""
Modèle Car : une annonce de voiture d'occasion telle que trouvée
par le scraper, enrichie par le score IA.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class Car(Base):
    __tablename__ = "cars"

    id = Column(Integer, primary_key=True, index=True)

    # Identité de l'annonce source
    source = Column(String, nullable=False)          # "mobile.de", "autoscout24", ...
    source_id = Column(String, unique=True, index=True, nullable=False)
    url = Column(String, nullable=False)

    # Caractéristiques du véhicule
    brand = Column(String, index=True, nullable=False)
    model = Column(String, index=True, nullable=False)
    year = Column(Integer)
    price = Column(Integer, nullable=False)
    mileage_km = Column(Integer, nullable=False)
    fuel_type = Column(String)        # "essence", "hybride", ...
    transmission = Column(String)     # "manuelle", "automatique"
    power_kw = Column(Integer, nullable=True)
    owners_count = Column(Integer, nullable=True)
    consumption_l_100km = Column(Float, nullable=True)

    # Localisation
    location = Column(String)
    distance_from_hamburg_km = Column(Float, nullable=True)

    # Contenu brut
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)

    # Scoring IA
    score = Column(Integer, nullable=True)             # note /100
    score_breakdown = Column(Text, nullable=True)       # JSON sérialisé du détail
    ai_analysis = Column(Text, nullable=True)           # points forts/faibles, JSON

    # Suivi
    is_active = Column(Boolean, default=True)           # False = annonce retirée
    date_added = Column(DateTime, default=datetime.utcnow)
    date_last_seen = Column(DateTime, default=datetime.utcnow)

    price_history = relationship("PriceHistory", back_populates="car")
