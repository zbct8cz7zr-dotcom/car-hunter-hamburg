"""
Scraper pour AutoScout24 — mêmes avertissements que mobile_de.py :
protection anti-bot active, sélecteurs à vérifier/ajuster manuellement,
repli possible sur les alertes email si le scraping direct est bloqué.
"""
import time
import re

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.scrapers.base import ScraperBase, SearchCriteria, RawListing, ScraperBlockedError

REQUEST_DELAY_SECONDS = 2.0
BASE_URL = "https://www.autoscout24.de"
SEARCH_PATH = "/lst"

FUEL_CODE = {
    "essence": "B",
    "diesel": "D",
    "hybride": "2",
    "électrique": "E",
}


class AutoScout24Scraper(ScraperBase):
    name = "autoscout24"

    def __init__(self):
        self.settings = get_settings()

    def _build_params(self, criteria: SearchCriteria) -> dict:
        params = {
            "priceto": criteria.budget_max,
            "kmto": criteria.km_max,
            "zipr": criteria.radius_km,
            "zip": "20095",
        }
        fuel_codes = [FUEL_CODE[f] for f in criteria.fuel_types if f in FUEL_CODE]
        if fuel_codes:
            params["fuel"] = ",".join(fuel_codes)
        return params

    def search(self, criteria: SearchCriteria) -> list[RawListing]:
        headers = {"User-Agent": self.settings.scrape_user_agent}
        results: list[RawListing] = []

        with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
            for brand in (criteria.brands or [None]):
                params = self._build_params(criteria)
                if brand:
                    params["mmvmk0"] = brand

                time.sleep(REQUEST_DELAY_SECONDS)
                response = client.get(f"{BASE_URL}{SEARCH_PATH}", params=params)

                if response.status_code in (403, 429):
                    raise ScraperBlockedError(
                        self.name,
                        f"HTTP {response.status_code} — probablement bloqué par la protection anti-bot",
                    )

                soup = BeautifulSoup(response.text, "lxml")
                listing_nodes = soup.select("article[data-testid='list-item']")  # à vérifier/ajuster

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
            title = node.select_one("h2")
            price_text = node.select_one("[data-testid='regular-price']")
            details = node.select("[data-testid='VehicleDetails'] span")

            if not (link and title and price_text):
                return None

            price = int(re.sub(r"[^\d]", "", price_text.get_text()))
            mileage = 0
            for d in details:
                txt = d.get_text(strip=True)
                if "km" in txt.lower():
                    mileage = int(re.sub(r"[^\d]", "", txt) or 0)
                    break

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
            return None
