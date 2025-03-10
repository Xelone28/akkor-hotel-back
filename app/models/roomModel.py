from sqlalchemy import Column, Integer, ForeignKey, DECIMAL
from app.managers.databaseManager import Base

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id", ondelete="CASCADE"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    number_of_beds = Column(Integer, nullable=False)
