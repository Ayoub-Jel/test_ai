# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from configs.database import get_db
from models.schema import UserCreate, UserLogin, Token, UserResponse, UserUpdate, SuccessResponse
from services.auth_service import AuthService
from utils.auth import get_current_active_user, require_vendeur
from models.database import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=Token)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Connexion d'un utilisateur
    """
    return AuthService.login_user(db, login_data)


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Récupère les informations de l'utilisateur connecté
    """
    return UserResponse.from_orm(current_user)


@router.put("/me", response_model=UserResponse)
def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour les informations de l'utilisateur connecté
    """
    return AuthService.update_user(db, current_user.id, update_data.dict(exclude_unset=True))


@router.post("/change-password", response_model=SuccessResponse)
def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change le mot de passe de l'utilisateur connecté
    """
    AuthService.change_password(db, current_user.id, old_password, new_password)
    return SuccessResponse(message="Mot de passe changé avec succès")


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Récupère un utilisateur par son ID (vendeurs uniquement)
    """
    user = AuthService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé"
        )
    return UserResponse.from_orm(user)


@router.get("/statistics")
def get_user_statistics(
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques des utilisateurs (vendeurs uniquement)
    """
    return AuthService.get_user_statistics(db)


@router.post("/deactivate/{user_id}", response_model=SuccessResponse)
def deactivate_user(
    user_id: int,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Désactive un utilisateur (vendeurs uniquement)
    """
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vous ne pouvez pas désactiver votre propre compte"
        )
    
    AuthService.deactivate_user(db, user_id)
    return SuccessResponse(message="Utilisateur désactivé avec succès")


@router.post("/verify-token", response_model=UserResponse)
def verify_token(current_user: User = Depends(get_current_active_user)):
    """
    Vérifie la validité du token et retourne les informations utilisateur
    """
    return UserResponse.from_orm(current_user)