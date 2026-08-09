# Car Hunter Hamburg

Assistant intelligent de recherche de voitures d'occasion à Hambourg.

## Structure du projet (Étape 1)

```
car-hunter-hamburg/
├── backend/
│   ├── app/
│   │   ├── core/          # config, connexion base de données
│   │   ├── models/        # Car, PriceHistory, UserSettings (SQLAlchemy)
│   │   ├── routers/       # endpoints API (à venir étape 2)
│   │   ├── services/      # logique métier : scoring, notifications (à venir)
│   │   ├── scrapers/      # scrapers mobile.de / autoscout24 (à venir)
│   │   └── main.py        # point d'entrée FastAPI
│   ├── tests/
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # cartes véhicules, etc. (à venir)
│   │   ├── pages/         # Dashboard, Annonces, Détail, Paramètres (à venir)
│   │   ├── hooks/
│   │   ├── types/
│   │   └── api/
│   └── public/
├── docker-compose.yml
└── README.md
```

## Lancer le backend en local (sans Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # puis remplir les valeurs si besoin
uvicorn app.main:app --reload
```

Vérifier que ça tourne : http://localhost:8000/health doit répondre `{"status": "ok", ...}`.

La documentation interactive de l'API est générée automatiquement par FastAPI :
http://localhost:8000/docs

## Base de données

SQLite est utilisé par défaut (fichier `car_hunter.db` créé automatiquement au
premier lancement). Pour migrer vers PostgreSQL plus tard, il suffira de changer
`DATABASE_URL` dans `.env` — le reste du code (modèles SQLAlchemy) ne change pas.

## Prochaines étapes

1. ✅ Architecture du projet, modèles de données, squelette FastAPI
2. ⬜ Endpoints API (CRUD annonces, filtres, paramètres)
3. ⬜ Scraper mobile.de / AutoScout24
4. ⬜ Système de scoring IA
5. ⬜ Interface React (Dashboard, Annonces, Détail véhicule, Paramètres)
6. ⬜ Notifications email / Telegram
7. ⬜ Déploiement Docker + GitHub Actions
