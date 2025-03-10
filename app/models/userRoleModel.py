from sqlalchemy import Column, Integer, ForeignKey, Boolean
from app.managers.databaseManager import Base

class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
