from app.scrapers.base import ScraperBase, ScraperBlockedError, SearchCriteria, RawListing
from app.scrapers.mobile_de import MobileDeScraper
from app.scrapers.autoscout24 import AutoScout24Scraper
from app.scrapers.kleinanzeigen import KleinanzeigenScraper

# Registre central : ajouter/retirer une source = une ligne ici.
AVAILABLE_SCRAPERS: list[ScraperBase] = [
    MobileDeScraper(),
    AutoScout24Scraper(),
    KleinanzeigenScraper(),
]

__all__ = [
    "ScraperBase", "ScraperBlockedError", "SearchCriteria", "RawListing",
    "AVAILABLE_SCRAPERS",
]
