from sqlalchemy import Column, ForeignKey, Integer
from app.managers.databaseManager import Base

class UserHotel(Base):
    __tablename__ = "user_hotels"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), primary_key=True)
