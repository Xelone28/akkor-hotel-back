from sqlalchemy import Column, Integer, String, Float, Boolean
from app.managers.databaseManager import Base

class Hotel(Base):
    __tablename__ = "hotels"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    breakfast = Column(Boolean, default=False)