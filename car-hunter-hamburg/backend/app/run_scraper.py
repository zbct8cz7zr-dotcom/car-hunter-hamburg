"""
Lance un cycle de scraping manuellement.

Usage : depuis backend/, avec le venv activé :
    python -m app.run_scraper
"""
from app.core.database import SessionLocal
from app.services.scraper_service import run_scrape


def main():
    db = SessionLocal()
    try:
        result = run_scrape(db)
        print(f"Nouvelles annonces : {result.new_listings}")
        print(f"Prix mis à jour : {result.updated_prices}")
        print(f"Annonces désactivées (disparues) : {result.deactivated}")
        if result.blocked_sources:
            print("Sources bloquées lors de ce passage :")
            for b in result.blocked_sources:
                print(f"  - {b}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
