from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    old_price = Column(Integer, nullable=False)
    new_price = Column(Integer, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    car = relationship("Car", back_populates="price_history")
