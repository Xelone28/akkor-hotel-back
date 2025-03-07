from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.userModel import User
from app.schemas.userSchemas import UserCreate, UserUpdate, UserResponse
from typing import List, Optional
import bcrypt  # Pour hacher les mots de passe

class UserService:

    @staticmethod
    async def get_user(db: AsyncSession, user_id: int) -> Optional[UserResponse]:
        """Récupère un utilisateur par son ID et retourne un schéma Pydantic."""
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def get_users(db: AsyncSession) -> List[UserResponse]:
        """Récupère la liste de tous les utilisateurs sous forme de schéma."""
        result = await db.execute(select(User))
        users = result.scalars().all()
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """Crée un nouvel utilisateur avec un mot de passe haché et retourne un schéma."""
        hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        new_user = User(
            email=user_data.email,
            pseudo=user_data.pseudo,
            password=hashed_password  # Stocké sous forme de chaîne
        )

        db.add(new_user)
        try:
            await db.commit()
            await db.refresh(new_user)
            return UserResponse.model_validate(new_user)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Cet email ou pseudo est déjà utilisé.")

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: UserUpdate) -> Optional[UserResponse]:
        """Met à jour un utilisateur et retourne le schéma mis à jour."""
        user = await UserService.get_user(db, user_id)
        if not user:
            return None
        
        # Mise à jour des champs fournis
        user_db = await db.execute(select(User).filter(User.id == user_id))
        user_db = user_db.scalars().first()
        
        for key, value in update_data.dict(exclude_unset=True).items():
            if key == "password":
                value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            setattr(user_db, key, value)

        try:
            await db.commit()
            await db.refresh(user_db)
            return UserResponse.model_validate(user_db)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Cet email ou pseudo est déjà utilisé.")
    
    @staticmethod
    async def delete_user(db: AsyncSession, user_id: int) -> bool:
        """Supprime un utilisateur et renvoie un booléen pour succès/échec."""
        user = await db.get(User, user_id)
        if not user:
            return False
        
        await db.delete(user)
        await db.commit()
        return True

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par email sous forme de schéma."""
        result = await db.execute(select(User).filter(User.email == email))
        user = result.scalars().first()
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def get_user_by_pseudo(db: AsyncSession, pseudo: str) -> Optional[UserResponse]:
        """Récupère un utilisateur par pseudo sous forme de schéma."""
        result = await db.execute(select(User).filter(User.pseudo == pseudo))
        user = result.scalars().first()
        return UserResponse.model_validate(user) if user else None

    @staticmethod
    async def get_user_by_pseudo_raw(db: AsyncSession, pseudo: str) -> Optional[User]:
        """Récupère un utilisateur par son pseudo avec accès au mot de passe."""
        result = await db.execute(select(User).filter(User.pseudo == pseudo))
        return result.scalars().first()  # Retourne directement un objet modèle SQLAlchemy