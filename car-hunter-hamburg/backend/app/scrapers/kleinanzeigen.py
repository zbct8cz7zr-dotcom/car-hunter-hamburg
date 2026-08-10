"""
Scraper pour eBay Kleinanzeigen (kleinanzeigen.de).

Historique des corrections :
- v2 (07/08/2026) : chemin de recherche corrigé, détection de marque par
  mot-clé plutôt que "premier mot du titre".
- v3 (09/08/2026) : le conteneur de chaque annonce n'est plus recherché
  via des noms de balises fixes (`<article>`, `<li>`) — cette hypothèse
  s'est révélée fragile (0 résultat en production alors que les annonces
  étaient bien présentes sur le site). À la place, on REMONTE depuis le
  lien `/s-anzeige/...` ancêtre par ancêtre jusqu'à trouver un conteneur
  dont le texte contient à la fois un prix ("€") et un kilométrage
  ("km") — une méthode indépendante du HTML exact utilisé par le site,
  qui continuera de fonctionner même si les noms de balises changent.

Recherche vérifiée manuellement le 09/08/2026 : la page
https://www.kleinanzeigen.de/s-autos/hamburg/auto/k0c216l9409 contient
bien des liens /s-anzeige/, avec un <h2> pour le titre et le motif de
texte "X.XXX € ... XXX.XXX km EZ MM/YYYY" pour prix/kilométrage/année —
confirmé par une récupération réelle de la page.

Les titres d'annonces sont du texte libre écrit par des particuliers
("VW Goli 7 - Baujahr 2014", "Auto sehr gut erhalten", fautes de frappe
incluses) — impossible de fiablement découper "marque + modèle" en
supposant que le premier mot est la marque. À la place, on cherche une
marque connue (KNOWN_BRANDS) n'importe où dans le titre. Une annonce
dont aucune marque connue n'est détectée est ignorée plutôt que
d'insérer une donnée fausse en base.
"""
import time
import re

import httpx
from bs4 import BeautifulSoup

from app.core.config import get_settings
from app.scrapers.base import ScraperBase, SearchCriteria, RawListing, ScraperBlockedError

REQUEST_DELAY_SECONDS = 2.0
BASE_URL = "https://www.kleinanzeigen.de"
# Catégorie "Autos" (c216) à Hambourg (l9409) — vérifié le 09/08/2026
SEARCH_PATH = "/s-autos/hamburg/auto/k0c216l9409"

PRICE_RE = re.compile(r"([\d.]+)\s*€")
KM_EZ_RE = re.compile(r"([\d.]+)\s*km\s*EZ\s*(\d{2})/(\d{4})")
MAX_ANCESTOR_LEVELS = 8  # limite de sécurité pour ne pas remonter jusqu'à <body>

# Marques connues à détecter dans les titres libres. Reprend les marques
# favorites habituelles + quelques marques fréquentes sur Kleinanzeigen,
# pour ne pas rater une bonne affaire hors de la liste favorite initiale.
KNOWN_BRANDS = [
    "toyota", "honda", "mazda", "hyundai", "kia", "volkswagen", "vw", "skoda",
    "bmw", "mercedes", "mercedes-benz", "audi", "opel", "ford", "renault",
    "peugeot", "citroen", "citroën", "seat", "nissan", "fiat", "volvo",
    "dacia", "mini", "smart", "mitsubishi", "suzuki", "subaru", "porsche",
    "chevrolet", "jaguar",
]


def _find_container(link):
    """Remonte les ancêtres du lien jusqu'à trouver un conteneur dont le
    texte contient à la fois un prix et un kilométrage — indépendant du
    nom des balises HTML utilisées par le site."""
    node = link.parent
    for _ in range(MAX_ANCESTOR_LEVELS):
        if node is None:
            break
        text = node.get_text(" ", strip=True)
        if "€" in text and "km" in text:
            return node
        node = node.parent
    return link.parent  # repli : au moins le parent direct


class KleinanzeigenScraper(ScraperBase):
    name = "kleinanzeigen"

    def __init__(self):
        self.settings = get_settings()

    def search(self, criteria: SearchCriteria) -> list[RawListing]:
        headers = {"User-Agent": self.settings.scrape_user_agent}
        results: list[RawListing] = []

        with httpx.Client(headers=headers, timeout=15.0, follow_redirects=True) as client:
            time.sleep(REQUEST_DELAY_SECONDS)
            response = client.get(f"{BASE_URL}{SEARCH_PATH}")

            if response.status_code in (403, 429):
                raise ScraperBlockedError(
                    self.name,
                    f"HTTP {response.status_code} — probablement bloqué par la protection anti-bot",
                )

            soup = BeautifulSoup(response.text, "lxml")

            if "captcha" in response.text.lower():
                raise ScraperBlockedError(self.name, "page de vérification / CAPTCHA détectée")

            # Toutes les annonces pointent vers une URL /s-anzeige/... —
            # motif stable, indépendant du nom des classes/balises CSS.
            seen_hrefs = set()
            for link in soup.select("a[href*='/s-anzeige/']"):
                href = link.get("href", "")
                if href in seen_hrefs:
                    continue
                seen_hrefs.add(href)

                listing = self._parse_listing(link, href)
                if listing and listing.mileage_km <= criteria.km_max and listing.price <= criteria.budget_max:
                    results.append(listing)

        return results

    def _parse_listing(self, link, href: str) -> RawListing | None:
        try:
            container = _find_container(link)
            if container is None:
                return None

            text = container.get_text(" ", strip=True)

            title_el = container.find(["h2", "h3"])
            title = title_el.get_text(strip=True) if title_el else link.get_text(strip=True)
            if not title:
                return None

            title_lower = title.lower()
            brand = next((b for b in KNOWN_BRANDS if b in title_lower), None)
            if brand is None:
                # Pas de marque reconnue dans ce titre en texte libre —
                # on préfère ignorer l'annonce plutôt que deviner.
                return None
            brand_display = "Volkswagen" if brand == "vw" else brand.replace("-", " ").title()
            model = title  # le titre entier sert de "modèle" faute de champ structuré

            price_match = PRICE_RE.search(text)
            if not price_match:
                return None
            price = int(price_match.group(1).replace(".", ""))

            km_ez_match = KM_EZ_RE.search(text)
            mileage = int(km_ez_match.group(1).replace(".", "")) if km_ez_match else 0
            year = int(km_ez_match.group(3)) if km_ez_match else None

            url = href if href.startswith("http") else f"{BASE_URL}{href}"
            # L'ID kleinanzeigen est le dernier segment numérique de l'URL
            source_id_match = re.search(r"(\d+)-\d+-\d+/?$", href)
            source_id = source_id_match.group(1) if source_id_match else href.rstrip("/").split("/")[-1]

            return RawListing(
                source=self.name,
                source_id=source_id,
                url=url,
                brand=brand_display,
                model=model,
                price=price,
                mileage_km=mileage,
                year=year,
                description=text,
            )
        except (AttributeError, ValueError, KeyError):
            return None
