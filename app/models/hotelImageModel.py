from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.managers.databaseManager import Base
import datetime

class HotelImage(Base):
    __tablename__ = 'hotel_image'

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False, unique=True)
    url = Column(String(1024), nullable=False)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete='CASCADE'), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)

    hotel = relationship("Hotel", back_populates="images")