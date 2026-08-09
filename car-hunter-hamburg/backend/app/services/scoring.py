"""
Système de notation IA — calcule une note /100 pour chaque annonce.

Pondération (telle que définie dans le brief) :
    Fiabilité moteur         30 pts
    Prix vs marché            20 pts
    Kilométrage                15 pts
    Historique entretien       10 pts
    Coût entretien estimé      10 pts
    Nombre de propriétaires     5 pts
    Consommation                5 pts
    Équipements                 5 pts

LIMITE IMPORTANTE À CONNAÎTRE :
Les scrapers actuels (étape 3) extraient seulement prix / kilométrage /
carburant / boîte / marque / modèle de façon fiable. Ils ne récupèrent
PAS encore de champ structuré pour l'historique d'entretien ou les
équipements — ces deux critères sont donc estimés par une recherche de
mots-clés dans le champ `description` quand il existe, avec une valeur
neutre par défaut sinon. Le score reste utile pour classer les annonces
entre elles, mais "Historique entretien" et "Équipements" sont les deux
composantes les moins fiables tant que les scrapers n'extraient pas ces
informations plus précisément.
"""
import json
from dataclasses import dataclass, asdict

from sqlalchemy.orm import Session

from app.models.car import Car

# Fiabilité moteur / coût d'entretien estimé, sur une échelle de 0 à 10.
# Valeurs approximatives issues de la réputation générale de ces marques
# sur le marché allemand de l'occasion — pas une donnée mesurée par annonce.
# À affiner au fil du temps si tu as de meilleures sources (ex: ADAC Pannenstatistik).
BRAND_RELIABILITY = {
    "toyota": 9.5, "honda": 9.0, "mazda": 8.0, "skoda": 7.5,
    "kia": 7.5, "hyundai": 7.5, "volkswagen": 7.0,
}
DEFAULT_RELIABILITY = 6.5

MAINTENANCE_KEYWORDS = [
    "scheckheft", "wartungshistorie", "scheckheftgepflegt",
    "entretien complet", "carnet d'entretien", "carnet entretien", "service history",
]
EQUIPMENT_KEYWORDS = [
    "klimaanlage", "climatisation", "navigation", "gps",
    "rückfahrkamera", "caméra de recul", "sitzheizung", "sièges chauffants",
    "tempomat", "régulateur de vitesse", "einparkhilfe", "aide au stationnement",
]


@dataclass
class ScoreBreakdown:
    reliability: int       # /30
    price_vs_market: int   # /20
    mileage: int           # /15
    maintenance_history: int  # /10
    maintenance_cost: int   # /10
    owners: int             # /5
    consumption: int        # /5
    equipment: int          # /5

    @property
    def total(self) -> int:
        return (
            self.reliability + self.price_vs_market + self.mileage
            + self.maintenance_history + self.maintenance_cost
            + self.owners + self.consumption + self.equipment
        )


TIERS = [
    (95, "ACHAT EXCEPTIONNEL", "Contacter le vendeur dès aujourd'hui — ce niveau de score est rare."),
    (90, "À CONTACTER RAPIDEMENT", "Contacter le vendeur."),
    (80, "BONNE AFFAIRE", "Contacter le vendeur, marge de négociation limitée."),
    (70, "NÉGOCIATION NÉCESSAIRE", "Ne pas payer le prix affiché — négocier avant de contacter."),
    (0, "À ÉVITER", "Passer son chemin sauf si aucune meilleure option dans le budget."),
]


def _tier_for(score: int) -> tuple[str, str]:
    for threshold, label, recommendation in TIERS:
        if score >= threshold:
            return label, recommendation
    return TIERS[-1][1], TIERS[-1][2]


def _reliability_score(brand: str) -> int:
    r = BRAND_RELIABILITY.get(brand.lower().strip(), DEFAULT_RELIABILITY)
    return round(r / 10 * 30)


def _maintenance_cost_score(brand: str) -> int:
    # Corrélé à la fiabilité : une mécanique plus fiable coûte statistiquement
    # moins cher à entretenir. Simplification volontaire faute de données
    # de coût réel par modèle.
    r = BRAND_RELIABILITY.get(brand.lower().strip(), DEFAULT_RELIABILITY)
    return round(r / 10 * 10)


def _price_score(car_price: int, market_avg: float | None) -> int:
    if not market_avg or market_avg <= 0:
        return 12  # neutre : pas assez d'annonces comparables pour juger
    ratio = car_price / market_avg
    if ratio <= 0.85:
        return 20
    if ratio <= 0.95:
        return 17
    if ratio <= 1.05:
        return 13
    if ratio <= 1.15:
        return 8
    return 3


def _mileage_score(km: int, km_reference: int) -> int:
    ratio = km / km_reference if km_reference else 1.0
    if ratio <= 0.3:
        return 15
    if ratio <= 0.5:
        return 13
    if ratio <= 0.7:
        return 10
    if ratio <= 0.9:
        return 6
    return 3


def _keyword_score(description: str | None, keywords: list[str], found_score: int, absent_score: int, unknown_score: int) -> int:
    if description is None:
        return unknown_score
    text = description.lower()
    return found_score if any(kw in text for kw in keywords) else absent_score


def _owners_score(owners_count: int | None) -> int:
    if owners_count is None:
        return 3
    if owners_count <= 1:
        return 5
    if owners_count == 2:
        return 4
    if owners_count == 3:
        return 2
    return 1


def _consumption_score(consumption: float | None) -> int:
    if consumption is None:
        return 3
    if consumption <= 4.5:
        return 5
    if consumption <= 6:
        return 4
    if consumption <= 7.5:
        return 3
    if consumption <= 9:
        return 2
    return 1


def _equipment_score(description: str | None) -> int:
    if description is None:
        return 2
    text = description.lower()
    matches = sum(1 for kw in EQUIPMENT_KEYWORDS if kw in text)
    return min(5, matches)


def compute_score(car: Car, market_avg_price: float | None, km_reference: int) -> tuple[ScoreBreakdown, dict]:
    breakdown = ScoreBreakdown(
        reliability=_reliability_score(car.brand),
        price_vs_market=_price_score(car.price, market_avg_price),
        mileage=_mileage_score(car.mileage_km, km_reference),
        maintenance_history=_keyword_score(car.description, MAINTENANCE_KEYWORDS, found_score=10, absent_score=4, unknown_score=5),
        maintenance_cost=_maintenance_cost_score(car.brand),
        owners=_owners_score(car.owners_count),
        consumption=_consumption_score(car.consumption_l_100km),
        equipment=_equipment_score(car.description),
    )

    label, recommendation = _tier_for(breakdown.total)

    # Points forts / points faibles : les composantes qui s'en sortent le
    # mieux / le moins bien, exprimées en % de leur maximum respectif.
    maxima = {"reliability": 30, "price_vs_market": 20, "mileage": 15,
              "maintenance_history": 10, "maintenance_cost": 10,
              "owners": 5, "consumption": 5, "equipment": 5}
    labels_fr = {
        "reliability": "Fiabilité moteur",
        "price_vs_market": "Prix par rapport au marché",
        "mileage": "Kilométrage",
        "maintenance_history": "Historique d'entretien",
        "maintenance_cost": "Coût d'entretien estimé",
        "owners": "Nombre de propriétaires",
        "consumption": "Consommation",
        "equipment": "Équipements",
    }
    ratios = {k: getattr(breakdown, k) / maxima[k] for k in maxima}
    strengths = [labels_fr[k] for k, v in ratios.items() if v >= 0.8]
    watch = [labels_fr[k] for k, v in ratios.items() if v <= 0.4]

    analysis = {
        "label": label,
        "recommendation": recommendation,
        "strengths": strengths,
        "watch": watch,
    }
    return breakdown, analysis


def score_all_active_cars(db: Session, km_reference: int = 150000) -> int:
    """Recalcule le score de toutes les annonces actives. À appeler après
    chaque cycle de scraping (les moyennes de marché changent avec de
    nouvelles annonces)."""
    cars = db.query(Car).filter(Car.is_active.is_(True)).all()

    # Moyenne de prix par (marque, modèle) sur l'ensemble des annonces actives
    averages: dict[tuple[str, str], list[int]] = {}
    for c in cars:
        key = (c.brand.lower(), c.model.lower())
        averages.setdefault(key, []).append(c.price)
    avg_by_key = {k: sum(v) / len(v) for k, v in averages.items()}

    updated = 0
    for car in cars:
        key = (car.brand.lower(), car.model.lower())
        comparables = [p for p in averages.get(key, []) if True]
        # Exclure le prix de la voiture elle-même de sa propre moyenne de référence
        others = [p for p in comparables if p != car.price] or comparables
        market_avg = sum(others) / len(others) if others else None

        breakdown, analysis = compute_score(car, market_avg, km_reference)
        car.score = breakdown.total
        car.score_breakdown = json.dumps(asdict(breakdown), ensure_ascii=False)
        car.ai_analysis = json.dumps(analysis, ensure_ascii=False)
        updated += 1

    db.commit()
    return updated
