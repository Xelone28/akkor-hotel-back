from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.userSchemas import UserCreate, UserUpdate, UserResponse
from app.services.userService import UserService
from app.managers.databaseManager import get_db
from app.security import get_current_user
from app.models import userModel
from typing import List

from app.security import verify_password, create_access_token
from datetime import timedelta

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve the current authenticated user."""
    return current_user

@router.post("/login", response_model=dict)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Authentifie l'utilisateur avec son pseudo et renvoie un JWT."""
    user = await UserService.get_user_by_pseudo_raw(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Pseudo ou mot de passe invalide")

    access_token = create_access_token(data={"sub": user.pseudo}, expires_delta=timedelta(minutes=60))

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/", response_model=List[UserResponse])
async def get_users(db: AsyncSession = Depends(get_db)):
    """Récupère tous les utilisateurs."""
    return await UserService.get_users(db)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Récupère un utilisateur par son ID."""
    user = await UserService.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Crée un utilisateur."""
    try:
        user = await UserService.create_user(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, update_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    """Met à jour un utilisateur."""
    user = await UserService.update_user(db, user_id, update_data)
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    return user

@router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)  # 🔒 Vérification du token
):
    """Supprime un utilisateur UNIQUEMENT si c'est lui-même qui fait la demande."""
    user_to_delete = await UserService.get_user(db, user_id)
    
    if not user_to_delete:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")

    # 🔒 Vérification : Seul l'utilisateur propriétaire peut se supprimer
    if user_to_delete.id != current_user.id:
        raise HTTPException(status_code=403, detail="Action interdite")

    deleted = await UserService.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur lors de la suppression")
