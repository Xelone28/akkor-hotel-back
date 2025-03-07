from pydantic import BaseModel, EmailStr
from typing import Optional

# Schéma de base (CE QUI EST AFFICHÉ À L'UTILISATEUR)
class UserBase(BaseModel):
    email: EmailStr
    pseudo: str

# Modèle pour la création d'un utilisateur (mot de passe requis)
class UserCreate(UserBase):
    password: str

# Modèle pour la mise à jour (tous les champs optionnels)
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    pseudo: Optional[str] = None
    password: Optional[str] = None

# Modèle pour la réponse (sans exposer le mot de passe)
class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True  # Permet la conversion depuis SQLAlchemy