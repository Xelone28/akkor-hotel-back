from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.managers.databaseManager import Base
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    pseudo = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

    roles = relationship(
        "UserRole",
        back_populates="user",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )
    bookings = relationship(
        "Booking",
        back_populates="user",
        cascade="all, delete, delete-orphan",
        passive_deletes=True
    )