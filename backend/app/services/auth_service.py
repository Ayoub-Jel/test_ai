# app/services/auth_service.py
from datetime import timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.database import User
from models.schema import UserCreate, UserLogin, Token, UserResponse
from utils.auth import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    verify_password
)
from utils.helpers import validate_email, validate_phone
from configs.settings import settings


class AuthService:
    """
    Service pour la gestion de l'authentification
    """
    
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> UserResponse:
        """
        Inscrit un nouvel utilisateur
        """
        # Vérifier si l'email existe déjà
        existing_user = db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Un utilisateur avec cet email existe déjà"
            )
        
        # Valider le format de l'email
        if not validate_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format d'email invalide"
            )
        
        # Valider le format du téléphone
        if not validate_phone(user_data.telephone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Format de téléphone invalide"
            )
        
        # Valider le rôle
        if user_data.role not in ["client", "vendeur"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rôle invalide. Doit être 'client' ou 'vendeur'"
            )
        
        # Créer l'utilisateur
        hashed_password = get_password_hash(user_data.password)
        
        db_user = User(
            email=user_data.email,
            password=hashed_password,
            nom=user_data.nom.strip().title(),
            prenom=user_data.prenom.strip().title(),
            telephone=user_data.telephone.strip(),
            role=user_data.role
        )
        
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création de l'utilisateur"
            )
        
        return UserResponse.from_orm(db_user)
    
    @staticmethod
    def login_user(db: Session, login_data: UserLogin) -> Token:
        """
        Connecte un utilisateur
        """
        # Authentifier l'utilisateur
        user = authenticate_user(db, login_data.email, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email ou mot de passe incorrect",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Vérifier que l'utilisateur est actif
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Compte utilisateur désactivé"
            )
        
        # Créer le token d'accès
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.from_orm(user)
        )
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Récupère un utilisateur par son ID
        """
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Récupère un utilisateur par son email
        """
        return db.query(User).filter(User.email == email, User.is_active == True).first()
    
    @staticmethod
    def update_user(db: Session, user_id: int, update_data: dict) -> UserResponse:
        """
        Met à jour les informations d'un utilisateur
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Mettre à jour les champs fournis
        for field, value in update_data.items():
            if hasattr(user, field) and value is not None:
                if field in ["nom", "prenom"]:
                    value = value.strip().title()
                elif field == "telephone":
                    if not validate_phone(value):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Format de téléphone invalide"
                        )
                    value = value.strip()
                
                setattr(user, field, value)
        
        try:
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour de l'utilisateur"
            )
        
        return UserResponse.from_orm(user)
    
    @staticmethod
    def change_password(db: Session, user_id: int, old_password: str, new_password: str) -> bool:
        """
        Change le mot de passe d'un utilisateur
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        # Vérifier l'ancien mot de passe
        if not verify_password(old_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe actuel incorrect"
            )
        
        # Valider le nouveau mot de passe
        if len(new_password) < 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le nouveau mot de passe doit contenir au moins 6 caractères"
            )
        
        # Mettre à jour le mot de passe
        user.password = get_password_hash(new_password)
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors du changement de mot de passe"
            )
        
        return True
    
    @staticmethod
    def deactivate_user(db: Session, user_id: int) -> bool:
        """
        Désactive un utilisateur
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur non trouvé"
            )
        
        user.is_active = False
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la désactivation de l'utilisateur"
            )
        
        return True
    
    @staticmethod
    def get_user_statistics(db: Session) -> dict:
        """
        Récupère les statistiques des utilisateurs
        """
        total_users = db.query(User).filter(User.is_active == True).count()
        clients = db.query(User).filter(User.role == "client", User.is_active == True).count()
        vendeurs = db.query(User).filter(User.role == "vendeur", User.is_active == True).count()
        
        return {
            "total_users": total_users,
            "clients": clients,
            "vendeurs": vendeurs,
            "inactive_users": db.query(User).filter(User.is_active == False).count()
        }