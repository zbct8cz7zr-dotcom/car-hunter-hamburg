"""
Orchestre l'ensemble des scrapers : lance chaque source, normalise les
résultats, et met à jour la base (nouvelles annonces, prix changés,
annonces disparues → marquées inactives).

Une source bloquée (ScraperBlockedError) n'interrompt pas les autres :
elle est simplement journalisée, pour que tu sois prévenu sans perdre les
résultats des sources qui fonctionnent encore.
"""
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.car import Car
from app.models.price_history import PriceHistory
from app.models.user_settings import UserSettings
from app.scrapers import AVAILABLE_SCRAPERS, SearchCriteria, ScraperBlockedError, RawListing
from app.services.scoring import score_all_active_cars


@dataclass
class ScrapeRunResult:
    new_listings: int = 0
    updated_prices: int = 0
    deactivated: int = 0
    blocked_sources: list[str] = None

    def __post_init__(self):
        if self.blocked_sources is None:
            self.blocked_sources = []


def _criteria_from_settings(settings: UserSettings) -> SearchCriteria:
    return SearchCriteria(
        budget_max=settings.budget_max,
        km_max=settings.km_max,
        radius_km=settings.radius_km,
        fuel_types=[f.strip() for f in settings.fuel_types.split(",") if f.strip()],
        brands=[b.strip() for b in settings.favorite_brands.split(",") if b.strip()],
    )


def _upsert_listing(db: Session, listing: RawListing) -> tuple[bool, bool]:
    """Insère l'annonce si nouvelle, ou met à jour le prix si elle existe déjà.
    Retourne (is_new, price_changed)."""
    existing = db.query(Car).filter(Car.source_id == listing.source_id).first()

    if existing is None:
        db.add(
            Car(
                source=listing.source,
                source_id=listing.source_id,
                url=listing.url,
                brand=listing.brand,
                model=listing.model,
                year=listing.year,
                price=listing.price,
                mileage_km=listing.mileage_km,
                fuel_type=listing.fuel_type,
                transmission=listing.transmission,
                location=listing.location,
                power_kw=listing.power_kw,
                owners_count=listing.owners_count,
                consumption_l_100km=listing.consumption_l_100km,
                image_url=listing.image_url,
                description=listing.description,
                is_active=True,
                date_added=datetime.utcnow(),
                date_last_seen=datetime.utcnow(),
            )
        )
        return True, False

    existing.date_last_seen = datetime.utcnow()
    existing.is_active = True
    price_changed = existing.price != listing.price
    if price_changed:
        db.add(PriceHistory(car_id=existing.id, old_price=existing.price, new_price=listing.price))
        existing.price = listing.price

    return False, price_changed


def run_scrape(db: Session) -> ScrapeRunResult:
    settings = db.query(UserSettings).first()
    if settings is None:
        raise RuntimeError("Aucun UserSettings en base — appelle GET /api/settings au moins une fois avant.")

    criteria = _criteria_from_settings(settings)
    result = ScrapeRunResult()
    seen_source_ids: set[str] = set()

    for scraper in AVAILABLE_SCRAPERS:
        try:
            listings = scraper.search(criteria)
        except ScraperBlockedError as e:
            result.blocked_sources.append(f"{e.source}: {e.reason}")
            continue

        for listing in listings:
            seen_source_ids.add(listing.source_id)
            is_new, price_changed = _upsert_listing(db, listing)
            if is_new:
                result.new_listings += 1
            elif price_changed:
                result.updated_prices += 1

    # Annonces plus vues lors de ce passage → probablement retirées par le vendeur
    still_active = (
        db.query(Car)
        .filter(Car.is_active.is_(True))
        .filter(~Car.source_id.in_(seen_source_ids))
        .all()
        if seen_source_ids
        else []
    )
    for car in still_active:
        car.is_active = False
        result.deactivated += 1

    db.commit()

    # Les moyennes de marché ont pu changer avec ces nouvelles annonces :
    # on recalcule le score de toutes les annonces actives, pas seulement
    # celles qui viennent d'être ajoutées.
    score_all_active_cars(db, km_reference=settings.km_max)

    return result
