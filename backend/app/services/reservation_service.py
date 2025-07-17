# app/services/reservation_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, and_
from fastapi import HTTPException, status
from models.database import Reservation, Car, User
from models.schema import (
    ReservationCreate, 
    ReservationUpdate, 
    ReservationResponse,
    ReservationStatus,
    DashboardStats
)
from utils.helpers import paginate_query, validate_reservation_dates


class ReservationService:
    """
    Service pour la gestion des réservations
    """
    
    @staticmethod
    def create_reservation(db: Session, reservation_data: ReservationCreate, user_id: int) -> ReservationResponse:
        """
        Crée une nouvelle réservation
        """
        # Vérifier que la voiture existe et est disponible
        car = db.query(Car).filter(Car.id == reservation_data.car_id, Car.is_active == True).first()
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voiture non trouvée"
            )
        
        if car.disponibilite != "disponible":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette voiture n'est pas disponible"
            )
        
        # Valider les dates
        if not validate_reservation_dates(
            reservation_data.date_debut,
            reservation_data.date_fin,
            reservation_data.type_transaction
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dates de réservation invalides"
            )
        
        # Vérifier les conflits de dates pour les locations
        if reservation_data.type_transaction == "location" and reservation_data.date_fin:
            existing_reservations = db.query(Reservation).filter(
                Reservation.car_id == reservation_data.car_id,
                Reservation.type_transaction == "location",
                Reservation.statut.in_(["en_attente", "confirmee"]),
                and_(
                    Reservation.date_debut < reservation_data.date_fin,
                    Reservation.date_fin > reservation_data.date_debut
                )
            ).count()
            
            if existing_reservations > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="La voiture est déjà réservée pour cette période"
                )
        
        # Valider le prix
        if reservation_data.prix_final <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le prix final doit être supérieur à 0"
            )
        
        # Créer la réservation
        db_reservation = Reservation(
            car_id=reservation_data.car_id,
            user_id=user_id,
            type_transaction=reservation_data.type_transaction,
            date_debut=reservation_data.date_debut,
            date_fin=reservation_data.date_fin,
            prix_final=reservation_data.prix_final,
            notes=reservation_data.notes,
            statut="en_attente"
        )
        
        try:
            db.add(db_reservation)
            
            # Mettre à jour le statut de la voiture si nécessaire
            if reservation_data.type_transaction == "vente":
                car.disponibilite = "vendu"
            elif reservation_data.type_transaction == "location":
                car.disponibilite = "loue"
            
            db.commit()
            db.refresh(db_reservation)
            
            # Charger les relations
            db_reservation = db.query(Reservation).options(
                joinedload(Reservation.car),
                joinedload(Reservation.user)
            ).filter(Reservation.id == db_reservation.id).first()
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création de la réservation"
            )
        
        return ReservationResponse.from_orm(db_reservation)
    
    @staticmethod
    def get_reservation_by_id(db: Session, reservation_id: int) -> Optional[Reservation]:
        """
        Récupère une réservation par son ID
        """
        return db.query(Reservation).options(
            joinedload(Reservation.car),
            joinedload(Reservation.user)
        ).filter(Reservation.id == reservation_id).first()
    
    @staticmethod
    def get_reservations(
        db: Session,
        user_id: Optional[int] = None,
        user_role: str = "client",
        page: int = 1,
        size: int = 20,
        status_filter: Optional[str] = None,
        type_filter: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Récupère les réservations avec pagination et filtres
        """
        query = db.query(Reservation).options(
            joinedload(Reservation.car),
            joinedload(Reservation.user)
        )
        
        # Filtrer par utilisateur si c'est un client
        if user_role == "client" and user_id:
            query = query.filter(Reservation.user_id == user_id)
        
        # Filtres additionnels
        if status_filter:
            query = query.filter(Reservation.statut == status_filter)
        
        if type_filter:
            query = query.filter(Reservation.type_transaction == type_filter)
        
        # Trier par date de création (plus récentes en premier)
        query = query.order_by(desc(Reservation.created_at))
        
        return paginate_query(query, page, size)
    
    @staticmethod
    def update_reservation_status(
        db: Session, 
        reservation_id: int, 
        new_status: ReservationStatus,
        user_role: str = "vendeur"
    ) -> ReservationResponse:
        """
        Met à jour le statut d'une réservation
        """
        if user_role != "vendeur":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Seuls les vendeurs peuvent modifier le statut des réservations"
            )
        
        reservation = db.query(Reservation).options(
            joinedload(Reservation.car),
            joinedload(Reservation.user)
        ).filter(Reservation.id == reservation_id).first()
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Réservation non trouvée"
            )
        
        # Vérifier les transitions de statut valides
        valid_transitions = {
            "en_attente": ["confirmee", "annulee"],
            "confirmee": ["terminee", "annulee"],
            "annulee": [],  # Une réservation annulée ne peut pas changer de statut
            "terminee": []  # Une réservation terminée ne peut pas changer de statut
        }
        
        if new_status not in valid_transitions.get(reservation.statut, []):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Transition de statut invalide de '{reservation.statut}' vers '{new_status}'"
            )
        
        old_status = reservation.statut
        reservation.statut = new_status
        
        # Mettre à jour la disponibilité de la voiture selon le nouveau statut
        car = reservation.car
        if new_status == "annulee":
            # Si la réservation est annulée, remettre la voiture disponible
            car.disponibilite = "disponible"
        elif new_status == "terminee" and reservation.type_transaction == "location":
            # Si une location est terminée, remettre la voiture disponible
            car.disponibilite = "disponible"
        
        try:
            db.commit()
            db.refresh(reservation)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour du statut"
            )
        
        return ReservationResponse.from_orm(reservation)
    
    @staticmethod
    def update_reservation(
        db: Session,
        reservation_id: int,
        update_data: ReservationUpdate,
        user_id: int,
        user_role: str
    ) -> ReservationResponse:
        """
        Met à jour une réservation
        """
        reservation = db.query(Reservation).options(
            joinedload(Reservation.car),
            joinedload(Reservation.user)
        ).filter(Reservation.id == reservation_id).first()
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Réservation non trouvée"
            )
        
        # Vérifier les permissions
        if user_role == "client" and reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez modifier que vos propres réservations"
            )
        
        # Les clients ne peuvent modifier que les réservations en attente
        if user_role == "client" and reservation.statut != "en_attente":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vous ne pouvez modifier que les réservations en attente"
            )
        
        # Mettre à jour les champs fournis
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(reservation, field) and value is not None:
                # Validations spécifiques
                if field == "prix_final" and value <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Le prix final doit être supérieur à 0"
                    )
                
                setattr(reservation, field, value)
        
        # Valider les nouvelles dates si elles ont été modifiées
        if any(field in update_dict for field in ["date_debut", "date_fin", "type_transaction"]):
            if not validate_reservation_dates(
                reservation.date_debut,
                reservation.date_fin,
                reservation.type_transaction
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Dates de réservation invalides"
                )
        
        try:
            db.commit()
            db.refresh(reservation)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour de la réservation"
            )
        
        return ReservationResponse.from_orm(reservation)
    
    @staticmethod
    def cancel_reservation(db: Session, reservation_id: int, user_id: int, user_role: str) -> bool:
        """
        Annule une réservation
        """
        reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Réservation non trouvée"
            )
        
        # Vérifier les permissions
        if user_role == "client" and reservation.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Vous ne pouvez annuler que vos propres réservations"
            )
        
        # Vérifier que la réservation peut être annulée
        if reservation.statut in ["annulee", "terminee"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cette réservation ne peut pas être annulée"
            )
        
        # Annuler la réservation
        reservation.statut = "annulee"
        
        # Remettre la voiture disponible
        car = db.query(Car).filter(Car.id == reservation.car_id).first()
        if car:
            car.disponibilite = "disponible"
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de l'annulation de la réservation"
            )
        
        return True
    
    @staticmethod
    def get_dashboard_stats(db: Session, user_role: str, user_id: Optional[int] = None) -> DashboardStats:
        """
        Récupère les statistiques pour le tableau de bord
        """
        if user_role == "client" and user_id:
            # Statistiques pour un client spécifique
            query = db.query(Reservation).filter(Reservation.user_id == user_id)
        else:
            # Statistiques globales pour les vendeurs
            query = db.query(Reservation)
        
        total_reservations = query.count()
        pending_reservations = query.filter(Reservation.statut == "en_attente").count()
        confirmed_reservations = query.filter(Reservation.statut == "confirmee").count()
        
        # Statistiques des voitures
        total_cars = db.query(Car).filter(Car.is_active == True).count()
        available_cars = db.query(Car).filter(
            Car.is_active == True,
            Car.disponibilite == "disponible"
        ).count()
        sold_cars = db.query(Car).filter(
            Car.is_active == True,
            Car.disponibilite == "vendu"
        ).count()
        rented_cars = db.query(Car).filter(
            Car.is_active == True,
            Car.disponibilite == "loue"
        ).count()
        
        return DashboardStats(
            total_cars=total_cars,
            available_cars=available_cars,
            sold_cars=sold_cars,
            rented_cars=rented_cars,
            total_reservations=total_reservations,
            pending_reservations=pending_reservations,
            confirmed_reservations=confirmed_reservations
        )
    
    @staticmethod
    def get_reservations_by_car(db: Session, car_id: int) -> List[ReservationResponse]:
        """
        Récupère toutes les réservations pour une voiture donnée
        """
        reservations = db.query(Reservation).options(
            joinedload(Reservation.user)
        ).filter(Reservation.car_id == car_id).order_by(desc(Reservation.created_at)).all()
        
        return [ReservationResponse.from_orm(reservation) for reservation in reservations]
    
    @staticmethod
    def get_upcoming_reservations(db: Session, days_ahead: int = 7) -> List[ReservationResponse]:
        """
        Récupère les réservations à venir dans les prochains jours
        """
        end_date = datetime.now() + timedelta(days=days_ahead)
        
        reservations = db.query(Reservation).options(
            joinedload(Reservation.car),
            joinedload(Reservation.user)
        ).filter(
            Reservation.date_debut <= end_date,
            Reservation.date_debut >= datetime.now(),
            Reservation.statut == "confirmee"
        ).order_by(Reservation.date_debut).all()
        
        return [ReservationResponse.from_orm(reservation) for reservation in reservations]
    
    @staticmethod
    def get_reservation_statistics(db: Session) -> Dict[str, Any]:
        """
        Récupère les statistiques détaillées des réservations
        """
        # Statistiques par statut
        status_stats = db.query(
            Reservation.statut,
            func.count(Reservation.id)
        ).group_by(Reservation.statut).all()
        
        # Statistiques par type de transaction
        type_stats = db.query(
            Reservation.type_transaction,
            func.count(Reservation.id)
        ).group_by(Reservation.type_transaction).all()
        
        # Revenus par mois (derniers 12 mois)
        monthly_revenue = db.query(
            func.date_format(Reservation.created_at, '%Y-%m').label('month'),
            func.sum(Reservation.prix_final).label('revenue')
        ).filter(
            Reservation.statut.in_(["confirmee", "terminee"]),
            Reservation.created_at >= datetime.now() - timedelta(days=365)
        ).group_by(
            func.date_format(Reservation.created_at, '%Y-%m')
        ).order_by(
            func.date_format(Reservation.created_at, '%Y-%m')
        ).all()
        
        return {
            "by_status": {status: count for status, count in status_stats},
            "by_type": {type_: count for type_, count in type_stats},
            "monthly_revenue": {month: float(revenue) for month, revenue in monthly_revenue},
            "total_revenue": sum(revenue for _, revenue in monthly_revenue)
        }