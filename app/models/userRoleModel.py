from sqlalchemy import Column, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.managers.databaseManager import Base

class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    is_admin = Column(Boolean, default=False, nullable=False)

    user = relationship(
        "User",
        back_populates="roles"
    )