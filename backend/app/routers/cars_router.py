# app/routers/cars.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from sqlalchemy.orm import Session
from configs.database import get_db
from models.schema import (
    CarCreate, 
    CarUpdate, 
    CarResponse, 
    CarFilter, 
    CarStats,
    PaginatedCars,
    SuccessResponse
)
from services.cars_service import CarService
from utils.auth import get_current_active_user, require_vendeur
from models.database import User

router = APIRouter(prefix="/api/cars", tags=["Cars"])


@router.post("/", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def create_car(
    car_data: CarCreate,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle voiture (vendeurs uniquement)
    """
    return CarService.create_car(db, car_data)


@router.get("/", response_model=PaginatedCars)
def get_cars(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    sort_by: str = Query("created_at", description="Champ de tri"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Ordre de tri"),
    db: Session = Depends(get_db)
):
    """
    Récupère la liste des voitures avec pagination
    """
    result = CarService.get_cars(db, page, size, sort_by, sort_order)
    return PaginatedCars(
        items=[CarResponse.from_orm(car) for car in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/available", response_model=PaginatedCars)
def get_available_cars(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    db: Session = Depends(get_db)
):
    """
    Récupère uniquement les voitures disponibles
    """
    result = CarService.get_available_cars(db, page, size)
    return PaginatedCars(
        items=[CarResponse.from_orm(car) for car in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.post("/filter", response_model=PaginatedCars)
def filter_cars(
    filters: CarFilter,
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    db: Session = Depends(get_db)
):
    """
    Filtre les voitures selon les critères
    """
    result = CarService.filter_cars(db, filters, page, size)
    return PaginatedCars(
        items=[CarResponse.from_orm(car) for car in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/search", response_model=PaginatedCars)
def search_cars(
    q: str = Query(..., min_length=2, description="Terme de recherche"),
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    db: Session = Depends(get_db)
):
    """
    Recherche les voitures par terme
    """
    result = CarService.search_cars(db, q, page, size)
    return PaginatedCars(
        items=[CarResponse.from_orm(car) for car in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/brand/{brand}", response_model=PaginatedCars)
def get_cars_by_brand(
    brand: str,
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    db: Session = Depends(get_db)
):
    """
    Récupère les voitures d'une marque spécifique
    """
    result = CarService.get_cars_by_brand(db, brand, page, size)
    return PaginatedCars(
        items=[CarResponse.from_orm(car) for car in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/statistics", response_model=CarStats)
def get_car_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques des voitures
    """
    return CarService.get_car_statistics(db)


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: int, db: Session = Depends(get_db)):
    """
    Récupère une voiture par son ID
    """
    car = CarService.get_car_by_id(db, car_id)
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Voiture non trouvée"
        )
    return CarResponse.from_orm(car)


@router.put("/{car_id}", response_model=CarResponse)
def update_car(
    car_id: int,
    car_update: CarUpdate,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Met à jour une voiture (vendeurs uniquement)
    """
    return CarService.update_car(db, car_id, car_update)


@router.patch("/{car_id}/availability", response_model=CarResponse)
def update_car_availability(
    car_id: int,
    availability: str = Query(..., regex="^(disponible|loue|vendu)$"),
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Met à jour uniquement la disponibilité d'une voiture (vendeurs uniquement)
    """
    return CarService.update_car_availability(db, car_id, availability)


@router.delete("/{car_id}", response_model=SuccessResponse)
def delete_car(
    car_id: int,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Supprime une voiture (vendeurs uniquement)
    """
    CarService.delete_car(db, car_id)
    return SuccessResponse(message="Voiture supprimée avec succès")