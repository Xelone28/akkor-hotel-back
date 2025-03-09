from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, func
from app.managers.databaseManager import Base

class HotelPicture(Base):
    __tablename__ = "hotel_pictures"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    uuid = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
