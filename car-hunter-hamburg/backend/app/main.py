"""
Car Hunter Hamburg - point d'entrée de l'API.

Étape 1 : squelette de l'application, base de données, healthcheck.
Les routers (cars, settings, alerts...) seront ajoutés aux étapes suivantes.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import cars, settings, scrape, score, history

# Crée les tables si elles n'existent pas encore (suffisant pour SQLite en dev ;
# on passera à Alembic pour les migrations dès que le schéma se stabilise).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Car Hunter Hamburg",
    description="Assistant intelligent de recherche de voitures d'occasion à Hambourg",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # URL du frontend Vite en dev
    allow_credentials=false,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {"status": "ok", "app": "car-hunter-hamburg"}


app.include_router(cars.router, prefix="/api/cars", tags=["cars"])
app.include_router(settings.router, prefix="/api/settings", tags=["settings"])
app.include_router(scrape.router, prefix="/api/scrape", tags=["scrape"])
app.include_router(score.router, prefix="/api/score", tags=["score"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

# --- Sera branché à l'étape "Notifications" ---
# from app.routers import alerts
# app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])
