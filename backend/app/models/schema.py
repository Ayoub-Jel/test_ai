# app/models/schemas.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


# Enums pour la validation
class UserRole(str, Enum):
    CLIENT = "client"
    VENDEUR = "vendeur"


class CarAvailability(str, Enum):
    DISPONIBLE = "disponible"
    LOUE = "loue"
    VENDU = "vendu"


class TransactionType(str, Enum):
    VENTE = "vente"
    LOCATION = "location"


class ReservationStatus(str, Enum):
    EN_ATTENTE = "en_attente"
    CONFIRMEE = "confirmee"
    ANNULEE = "annulee"
    TERMINEE = "terminee"


# Schémas de base
class UserBase(BaseModel):
    email: EmailStr
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    telephone: str = Field(..., min_length=10, max_length=20)
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')
        return v


class UserUpdate(BaseModel):
    nom: Optional[str] = Field(None, min_length=2, max_length=100)
    prenom: Optional[str] = Field(None, min_length=2, max_length=100)
    telephone: Optional[str] = Field(None, min_length=10, max_length=20)
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class CarBase(BaseModel):
    marque: str = Field(..., min_length=2, max_length=100)
    modele: str = Field(..., min_length=1, max_length=100)
    couleur: str = Field(..., min_length=2, max_length=50)
    motorisation: str = Field(..., min_length=2, max_length=100)
    prix: float = Field(..., gt=0)
    disponibilite: CarAvailability = CarAvailability.DISPONIBLE
    description: Optional[str] = Field(None, max_length=1000)
    kilometrage: Optional[int] = Field(None, ge=0)
    annee: Optional[int] = Field(None, ge=1900, le=2030)
    image_url: Optional[str] = Field(None, max_length=500)


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    marque: Optional[str] = Field(None, min_length=2, max_length=100)
    modele: Optional[str] = Field(None, min_length=1, max_length=100)
    couleur: Optional[str] = Field(None, min_length=2, max_length=50)
    motorisation: Optional[str] = Field(None, min_length=2, max_length=100)
    prix: Optional[float] = Field(None, gt=0)
    disponibilite: Optional[CarAvailability] = None
    description: Optional[str] = Field(None, max_length=1000)
    kilometrage: Optional[int] = Field(None, ge=0)
    annee: Optional[int] = Field(None, ge=1900, le=2030)
    image_url: Optional[str] = Field(None, max_length=500)


class CarResponse(CarBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CarFilter(BaseModel):
    marque: Optional[str] = None
    modele: Optional[str] = None
    couleur: Optional[str] = None
    motorisation: Optional[str] = None
    prix_min: Optional[float] = Field(None, ge=0)
    prix_max: Optional[float] = Field(None, ge=0)
    disponibilite: Optional[CarAvailability] = None
    annee_min: Optional[int] = Field(None, ge=1900)
    annee_max: Optional[int] = Field(None, le=2030)
    kilometrage_max: Optional[int] = Field(None, ge=0)
    
    @validator('prix_max')
    def validate_prix_range(cls, v, values):
        if v is not None and 'prix_min' in values and values['prix_min'] is not None:
            if v < values['prix_min']:
                raise ValueError('Le prix maximum doit être supérieur au prix minimum')
        return v


class ReservationBase(BaseModel):
    car_id: int
    type_transaction: TransactionType
    date_debut: datetime
    date_fin: Optional[datetime] = None
    prix_final: float = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=500)
    
    @validator('date_fin')
    def validate_date_fin(cls, v, values):
        if 'type_transaction' in values and values['type_transaction'] == TransactionType.LOCATION:
            if v is None:
                raise ValueError('La date de fin est obligatoire pour les locations')
            if 'date_debut' in values and v <= values['date_debut']:
                raise ValueError('La date de fin doit être postérieure à la date de début')
        return v


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    type_transaction: Optional[TransactionType] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    prix_final: Optional[float] = Field(None, gt=0)
    statut: Optional[ReservationStatus] = None
    notes: Optional[str] = Field(None, max_length=500)


class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    statut: ReservationStatus
    created_at: datetime
    updated_at: datetime
    car: Optional[CarResponse] = None
    user: Optional[UserResponse] = None
    
    class Config:
        from_attributes = True


class StatusUpdate(BaseModel):
    statut: ReservationStatus


# Schémas pour les statistiques
class DashboardStats(BaseModel):
    total_cars: int
    available_cars: int
    sold_cars: int
    rented_cars: int
    total_reservations: int
    pending_reservations: int
    confirmed_reservations: int


class CarStats(BaseModel):
    total: int
    by_availability: dict
    by_brand: dict
    average_price: float
    price_range: dict


# Schémas de pagination
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int


class PaginatedCars(PaginatedResponse):
    items: List[CarResponse]


class PaginatedReservations(PaginatedResponse):
    items: List[ReservationResponse]


# Schémas pour les réponses d'erreur
class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None


class ValidationErrorResponse(BaseModel):
    detail: List[dict]
    message: str = "Erreur de validation"


# Schémas pour les messages de succès
class SuccessResponse(BaseModel):
    message: str
    data: Optional[dict] = None