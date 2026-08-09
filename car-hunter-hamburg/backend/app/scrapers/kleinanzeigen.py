"""
Scraper pour eBay Kleinanzeigen (kleinanzeigen.de) — généralement moins
protégé contre le scraping que mobile.de/AutoScout24, mais reste sujet à
changement sans préavis. Mêmes précautions : sélecteurs à vérifier,
fréquence de requêtes raisonnable, gestion du blocage éventuel.

Kleinanzeigen étant principalement un site de particulier à particulier,
c'est une bonne source complémentaire pour des prix plus bas, mais avec
moins de garanties (pas de reprise, historique d'entretien souvent flou).
"""
import time
import re

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.scrapers.base import ScraperBase, SearchCriteria, RawListing, ScraperBlockedError

REQUEST_DELAY_SECONDS = 2.0
BASE_URL = "https://www.kleinanzeigen.de"
SEARCH_PATH = "/s-autos/hamburg"


class KleinanzeigenScraper(ScraperBase):
    name = "kleinanzeigen"

    def __init__(self):
        self.settings = get_settings()

    def search(self, criteria: SearchCriteria) -> list[RawListing]:
        headers = {"User-Agent": self.settings.scrape_user_agent}
        results: list[RawListing] = []

        with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
            params = {
                "priceType": "FIXED",
                "maxPrice": criteria.budget_max,
            }

            time.sleep(REQUEST_DELAY_SECONDS)
            response = client.get(f"{BASE_URL}{SEARCH_PATH}", params=params)

            if response.status_code in (403, 429):
                raise ScraperBlockedError(
                    self.name,
                    f"HTTP {response.status_code} — probablement bloqué par la protection anti-bot",
                )

            soup = BeautifulSoup(response.text, "lxml")
            listing_nodes = soup.select("article.aditem")  # à vérifier/ajuster

            if not listing_nodes and "captcha" in response.text.lower():
                raise ScraperBlockedError(self.name, "page de vérification / CAPTCHA détectée")

            for node in listing_nodes:
                listing = self._parse_listing(node)
                if listing and listing.mileage_km <= criteria.km_max:
                    results.append(listing)

        return results

    def _parse_listing(self, node) -> RawListing | None:
        try:
            link = node.select_one("a.ellipsis")
            price_text = node.select_one(".aditem-main--middle--price-shipping--price")
            description = node.select_one(".aditem-main--middle--description")

            if not (link and price_text):
                return None

            price_raw = price_text.get_text(strip=True)
            if "vb" in price_raw.lower():  # "à débattre" — on garde le chiffre quand même
                price_raw = price_raw.lower().replace("vb", "")
            price = int(re.sub(r"[^\d]", "", price_raw) or 0)

            title = link.get_text(strip=True)
            brand_model = title.split(" ", 1)
            brand = brand_model[0]
            model = brand_model[1] if len(brand_model) > 1 else ""

            # Le kilométrage n'est pas toujours dans un champ dédié sur
            # Kleinanzeigen : on tente de l'extraire de la description.
            mileage = 0
            if description:
                match = re.search(r"([\d.]{4,7})\s*km", description.get_text())
                if match:
                    mileage = int(match.group(1).replace(".", ""))

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
            return None
