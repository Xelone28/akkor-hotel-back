from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.managers.databaseManager import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    pseudo = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
