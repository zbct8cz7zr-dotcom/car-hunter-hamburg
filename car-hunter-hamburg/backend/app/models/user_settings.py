from sqlalchemy import Column, Integer, String, Boolean

from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)

    budget_max = Column(Integer, default=10000)
    km_max = Column(Integer, default=150000)
    radius_km = Column(Integer, default=100)

    # Listes stockées en CSV simple pour rester SQLite-friendly
    # ex: "essence,hybride"  /  "toyota,honda,mazda"
    fuel_types = Column(String, default="essence,hybride")
    favorite_brands = Column(String, default="toyota,honda,mazda,hyundai,kia,volkswagen,skoda")

    # Notifications
    notify_email = Column(Boolean, default=True)
    notify_telegram = Column(Boolean, default=False)
    daily_summary_hour = Column(Integer, default=7)   # 7h du matin
    instant_alert_score_threshold = Column(Integer, default=95)
