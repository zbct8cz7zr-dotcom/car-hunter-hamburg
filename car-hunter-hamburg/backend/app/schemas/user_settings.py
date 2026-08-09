from pydantic import BaseModel, ConfigDict


class UserSettingsBase(BaseModel):
    budget_max: int
    km_max: int
    radius_km: int
    fuel_types: str            # CSV, ex: "essence,hybride"
    favorite_brands: str       # CSV, ex: "toyota,honda"
    notify_email: bool
    notify_telegram: bool
    daily_summary_hour: int
    instant_alert_score_threshold: int


class UserSettingsUpdate(BaseModel):
    """Tous les champs optionnels : on ne modifie que ce qui est envoyé."""
    budget_max: int | None = None
    km_max: int | None = None
    radius_km: int | None = None
    fuel_types: str | None = None
    favorite_brands: str | None = None
    notify_email: bool | None = None
    notify_telegram: bool | None = None
    daily_summary_hour: int | None = None
    instant_alert_score_threshold: int | None = None


class UserSettingsOut(UserSettingsBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
