"""
Scraper pour mobile.de.

IMPORTANT — à lire avant de lancer ceci en production :
- mobile.de utilise une protection anti-bot active. Ce scraper basique
  (requêtes HTTP simples) risque fort d'être bloqué (code 403, ou page de
  vérification à la place des résultats). C'est normal et attendu, pas un
  bug de ce code — voir ScraperBlockedError plus bas.
- Les sélecteurs CSS ci-dessous sont une base de départ : la structure HTML
  réelle du site doit être vérifiée et ajustée manuellement (inspecte une
  page de résultats dans ton navigateur, "Voir le code source").
- Respecte le fichier robots.txt du site et limite la fréquence des requêtes
  (voir REQUEST_DELAY_SECONDS) pour rester raisonnable.
- Si ce scraper est bloqué de façon persistante, la solution de repli
  discutée est le parsing des alertes email officielles de mobile.de.
"""
import time
import re

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.scrapers.base import ScraperBase, SearchCriteria, RawListing, ScraperBlockedError

REQUEST_DELAY_SECONDS = 2.0
BASE_URL = "https://www.mobile.de"
SEARCH_PATH = "/fahrzeuge/search.html"


class MobileDeScraper(ScraperBase):
    name = "mobile.de"

    def __init__(self):
        self.settings = get_settings()

    def _build_params(self, criteria: SearchCriteria) -> dict:
        # Paramètres illustratifs — à confronter à ceux réellement utilisés
        # par le site lors d'une recherche manuelle (inspecter l'URL générée).
        return {
            "priceTo": criteria.budget_max,
            "mileageTo": criteria.km_max,
            "radius": criteria.radius_km,
            "zipCode": "20095",  # Hambourg centre — ajustable
        }

    def search(self, criteria: SearchCriteria) -> list[RawListing]:
        headers = {"User-Agent": self.settings.scrape_user_agent}
        results: list[RawListing] = []

        with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
            for brand in (criteria.brands or [None]):
                params = self._build_params(criteria)
                if brand:
                    params["makeModelVariant1.makeId"] = brand

                time.sleep(REQUEST_DELAY_SECONDS)  # limiter la fréquence des requêtes
                response = client.get(f"{BASE_URL}{SEARCH_PATH}", params=params)

                if response.status_code in (403, 429):
                    raise ScraperBlockedError(
                        self.name,
                        f"HTTP {response.status_code} — probablement bloqué par la protection anti-bot",
                    )

                soup = BeautifulSoup(response.text, "lxml")
                listing_nodes = soup.select("[data-testid='result-item']")  # à vérifier/ajuster

                if not listing_nodes and "captcha" in response.text.lower():
                    raise ScraperBlockedError(self.name, "page de vérification / CAPTCHA détectée")

                for node in listing_nodes:
                    listing = self._parse_listing(node)
                    if listing:
                        results.append(listing)

        return results

    def _parse_listing(self, node) -> RawListing | None:
        try:
            link = node.select_one("a[href]")
            title = node.select_one("[data-testid='result-item-title']")
            price_text = node.select_one("[data-testid='result-item-price']")
            mileage_text = node.select_one("[data-testid='result-item-mileage']")

            if not (link and title and price_text):
                return None

            price = int(re.sub(r"[^\d]", "", price_text.get_text()))
            mileage = int(re.sub(r"[^\d]", "", mileage_text.get_text())) if mileage_text else 0
            brand_model = title.get_text(strip=True).split(" ", 1)
            brand = brand_model[0]
            model = brand_model[1] if len(brand_model) > 1 else ""

            url = link["href"]
            source_id = url.rstrip("/").split("/")[-1]

            return RawListing(
                source=self.name,
                source_id=source_id,
                url=url if url.startswith("http") else f"{BASE_URL}{url}",
                brand=brand,
                model=model,
                price=price,
                mileage_km=mileage,
            )
        except (AttributeError, ValueError, KeyError):
            # Une annonce individuelle mal formée ne doit pas faire échouer
            # tout le scraping — on la saute et on continue.
            return None
