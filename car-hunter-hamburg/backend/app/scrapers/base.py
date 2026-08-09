"""
Interface commune à tous les scrapers de sites d'annonces.

Chaque site (mobile.de, AutoScout24, Kleinanzeigen...) a sa propre classe
qui hérite de ScraperBase et implémente `search()`. Le reste de l'app
(scraper_service, scoring, etc.) ne dépend jamais d'un site en particulier —
seulement de cette interface. Ça permet d'ajouter/retirer/désactiver une
source sans toucher au reste du code, et de basculer vers une méthode de
repli (ex: parsing d'alertes email) si le scraping direct se fait bloquer.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class SearchCriteria:
    budget_max: int
    km_max: int
    radius_km: int
    fuel_types: list[str] = field(default_factory=list)   # ex: ["essence", "hybride"]
    brands: list[str] = field(default_factory=list)        # ex: ["toyota", "honda"]


@dataclass
class RawListing:
    """Une annonce brute telle qu'extraite du site, avant normalisation
    vers le modèle Car. Les champs optionnels dépendent de ce que le site
    expose réellement."""
    source: str
    source_id: str
    url: str
    brand: str
    model: str
    price: int
    mileage_km: int
    year: int | None = None
    fuel_type: str | None = None
    transmission: str | None = None
    location: str | None = None
    power_kw: int | None = None
    owners_count: int | None = None
    consumption_l_100km: float | None = None
    image_url: str | None = None
    description: str | None = None


class ScraperBase(ABC):
    """Classe de base : toute nouvelle source d'annonces doit hériter de
    celle-ci et implémenter `search`."""

    name: str = "base"

    @abstractmethod
    def search(self, criteria: SearchCriteria) -> list[RawListing]:
        """Retourne les annonces trouvées pour ces critères.
        Doit lever ScraperBlockedError si le site bloque la requête
        (protection anti-bot, CAPTCHA, code 403...), pour que le service
        appelant puisse basculer sur une méthode de repli plutôt que
        planter silencieusement."""
        raise NotImplementedError


class ScraperBlockedError(Exception):
    """Levée quand un site refuse la requête (403, CAPTCHA, structure HTML
    changée de façon inattendue...). Le service orchestrateur peut alors
    désactiver temporairement cette source et prévenir l'utilisateur plutôt
    que de renvoyer une liste vide silencieusement."""
    def __init__(self, source: str, reason: str):
        self.source = source
        self.reason = reason
        super().__init__(f"[{source}] bloqué : {reason}")
