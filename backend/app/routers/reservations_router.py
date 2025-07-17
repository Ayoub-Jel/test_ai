# app/routers/reservations.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from sqlalchemy.orm import Session
from configs.database import get_db
from models.schema import (
    ReservationCreate,
    ReservationUpdate,
    ReservationResponse,
    StatusUpdate,
    PaginatedReservations,
    DashboardStats,
    SuccessResponse
)
from services.reservation_service import ReservationService
from utils.auth import get_current_active_user, require_vendeur
from models.database import User

router = APIRouter(prefix="/api/reservations", tags=["Reservations"])


@router.post("/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    reservation_data: ReservationCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Crée une nouvelle réservation
    """
    return ReservationService.create_reservation(db, reservation_data, current_user.id)


@router.get("/", response_model=PaginatedReservations)
def get_reservations(
    page: int = Query(1, ge=1, description="Numéro de page"),
    size: int = Query(20, ge=1, le=100, description="Taille de page"),
    status_filter: Optional[str] = Query(None, description="Filtrer par statut"),
    type_filter: Optional[str] = Query(None, description="Filtrer par type de transaction"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les réservations (toutes pour les vendeurs, personnelles pour les clients)
    """
    result = ReservationService.get_reservations(
        db,
        user_id=current_user.id,
        user_role=current_user.role,
        page=page,
        size=size,
        status_filter=status_filter,
        type_filter=type_filter
    )
    
    return PaginatedReservations(
        items=[ReservationResponse.from_orm(reservation) for reservation in result["items"]],
        total=result["total"],
        page=result["page"],
        size=result["size"],
        pages=result["pages"]
    )


@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques pour le tableau de bord
    """
    user_id = current_user.id if current_user.role == "client" else None
    return ReservationService.get_dashboard_stats(db, current_user.role, user_id)


@router.get("/upcoming", response_model=List[ReservationResponse])
def get_upcoming_reservations(
    days_ahead: int = Query(7, ge=1, le=30, description="Nombre de jours à venir"),
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Récupère les réservations à venir (vendeurs uniquement)
    """
    return ReservationService.get_upcoming_reservations(db, days_ahead)


@router.get("/statistics")
def get_reservation_statistics(
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Récupère les statistiques détaillées des réservations (vendeurs uniquement)
    """
    return ReservationService.get_reservation_statistics(db)


@router.get("/car/{car_id}", response_model=List[ReservationResponse])
def get_reservations_by_car(
    car_id: int,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Récupère toutes les réservations pour une voiture donnée (vendeurs uniquement)
    """
    return ReservationService.get_reservations_by_car(db, car_id)


@router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Récupère une réservation par son ID
    """
    reservation = ReservationService.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Réservation non trouvée"
        )
    
    # Vérifier les permissions pour les clients
    if current_user.role == "client" and reservation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez voir que vos propres réservations"
        )
    
    return ReservationResponse.from_orm(reservation)


@router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    update_data: ReservationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Met à jour une réservation
    """
    return ReservationService.update_reservation(
        db, reservation_id, update_data, current_user.id, current_user.role
    )


@router.patch("/{reservation_id}/status", response_model=ReservationResponse)
def update_reservation_status(
    reservation_id: int,
    status_update: StatusUpdate,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Met à jour le statut d'une réservation (vendeurs uniquement)
    """
    return ReservationService.update_reservation_status(
        db, reservation_id, status_update.statut, current_user.role
    )


@router.post("/{reservation_id}/cancel", response_model=SuccessResponse)
def cancel_reservation(
    reservation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Annule une réservation
    """
    ReservationService.cancel_reservation(db, reservation_id, current_user.id, current_user.role)
    return SuccessResponse(message="Réservation annulée avec succès")


@router.delete("/{reservation_id}", response_model=SuccessResponse)
def delete_reservation(
    reservation_id: int,
    current_user: User = Depends(require_vendeur),
    db: Session = Depends(get_db)
):
    """
    Supprime définitivement une réservation (vendeurs uniquement)
    """
    reservation = ReservationService.get_reservation_by_id(db, reservation_id)
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Réservation non trouvée"
        )
    
    # Seules les réservations annulées peuvent être supprimées
    if reservation.statut != "annulee":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Seules les réservations annulées peuvent être supprimées"
        )
    
    try:
        db.delete(reservation)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors de la suppression de la réservation"
        )
    
    return SuccessResponse(message="Réservation supprimée avec succès")