# app/services/car_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from fastapi import HTTPException, status
from models.database import Car, Reservation
from models.schema import CarCreate, CarUpdate, CarFilter, CarResponse, CarStats
from utils.helpers import paginate_query, sanitize_string, calculate_age_from_year


class CarService:
    """
    Service pour la gestion des voitures
    """
    
    @staticmethod
    def create_car(db: Session, car_data: CarCreate) -> CarResponse:
        """
        Crée une nouvelle voiture
        """
        # Nettoyer et valider les données
        marque = sanitize_string(car_data.marque.strip().title())
        modele = sanitize_string(car_data.modele.strip().title())
        couleur = sanitize_string(car_data.couleur.strip().lower())
        motorisation = sanitize_string(car_data.motorisation.strip())
        
        if not marque or not modele:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La marque et le modèle sont obligatoires"
            )
        
        if car_data.prix <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Le prix doit être supérieur à 0"
            )
        
        # Vérifier si une voiture similaire existe déjà
        existing_car = db.query(Car).filter(
            Car.marque == marque,
            Car.modele == modele,
            Car.couleur == couleur,
            Car.motorisation == motorisation,
            Car.is_active == True
        ).first()
        
        if existing_car:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Une voiture similaire existe déjà dans l'inventaire"
            )
        
        # Créer la voiture
        db_car = Car(
            marque=marque,
            modele=modele,
            couleur=couleur,
            motorisation=motorisation,
            prix=car_data.prix,
            disponibilite=car_data.disponibilite,
            description=sanitize_string(car_data.description) if car_data.description else None,
            kilometrage=car_data.kilometrage,
            annee=car_data.annee,
            image_url=car_data.image_url
        )
        
        try:
            db.add(db_car)
            db.commit()
            db.refresh(db_car)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création de la voiture"
            )
        
        return CarResponse.from_orm(db_car)
    
    @staticmethod
    def get_car_by_id(db: Session, car_id: int) -> Optional[Car]:
        """
        Récupère une voiture par son ID
        """
        return db.query(Car).filter(Car.id == car_id, Car.is_active == True).first()
    
    @staticmethod
    def get_cars(
        db: Session,
        page: int = 1,
        size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Récupère la liste des voitures avec pagination
        """
        query = db.query(Car).filter(Car.is_active == True)
        
        # Tri
        if hasattr(Car, sort_by):
            if sort_order.lower() == "asc":
                query = query.order_by(asc(getattr(Car, sort_by)))
            else:
                query = query.order_by(desc(getattr(Car, sort_by)))
        
        return paginate_query(query, page, size)
    
    @staticmethod
    def filter_cars(db: Session, filters: CarFilter, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """
        Filtre les voitures selon les critères
        """
        query = db.query(Car).filter(Car.is_active == True)
        
        # Appliquer les filtres
        if filters.marque:
            query = query.filter(Car.marque.ilike(f"%{filters.marque}%"))
        
        if filters.modele:
            query = query.filter(Car.modele.ilike(f"%{filters.modele}%"))
        
        if filters.couleur:
            query = query.filter(Car.couleur.ilike(f"%{filters.couleur}%"))
        
        if filters.motorisation:
            query = query.filter(Car.motorisation.ilike(f"%{filters.motorisation}%"))
        
        if filters.prix_min is not None:
            query = query.filter(Car.prix >= filters.prix_min)
        
        if filters.prix_max is not None:
            query = query.filter(Car.prix <= filters.prix_max)
        
        if filters.disponibilite:
            query = query.filter(Car.disponibilite == filters.disponibilite)
        
        if filters.annee_min is not None:
            query = query.filter(Car.annee >= filters.annee_min)
        
        if filters.annee_max is not None:
            query = query.filter(Car.annee <= filters.annee_max)
        
        if filters.kilometrage_max is not None:
            query = query.filter(Car.kilometrage <= filters.kilometrage_max)
        
        # Trier par pertinence puis par date
        query = query.order_by(desc(Car.created_at))
        
        return paginate_query(query, page, size)
    
    @staticmethod
    def update_car(db: Session, car_id: int, update_data: CarUpdate) -> CarResponse:
        """
        Met à jour une voiture
        """
        car = db.query(Car).filter(Car.id == car_id, Car.is_active == True).first()
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voiture non trouvée"
            )
        
        # Vérifier s'il y a des réservations en cours avant de modifier la disponibilité
        if update_data.disponibilite and update_data.disponibilite != car.disponibilite:
            active_reservations = db.query(Reservation).filter(
                Reservation.car_id == car_id,
                Reservation.statut.in_(["en_attente", "confirmee"])
            ).count()
            
            if active_reservations > 0 and update_data.disponibilite == "disponible":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Impossible de rendre disponible une voiture avec des réservations actives"
                )
        
        # Mettre à jour les champs fournis
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(car, field) and value is not None:
                if field in ["marque", "modele"]:
                    value = sanitize_string(str(value).strip().title())
                elif field == "couleur":
                    value = sanitize_string(str(value).strip().lower())
                elif field == "description":
                    value = sanitize_string(str(value))
                elif field == "prix" and value <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Le prix doit être supérieur à 0"
                    )
                
                setattr(car, field, value)
        
        try:
            db.commit()
            db.refresh(car)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour de la voiture"
            )
        
        return CarResponse.from_orm(car)
    
    @staticmethod
    def delete_car(db: Session, car_id: int) -> bool:
        """
        Supprime (désactive) une voiture
        """
        car = db.query(Car).filter(Car.id == car_id).first()
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voiture non trouvée"
            )
        
        # Vérifier s'il y a des réservations actives
        active_reservations = db.query(Reservation).filter(
            Reservation.car_id == car_id,
            Reservation.statut.in_(["en_attente", "confirmee"])
        ).count()
        
        if active_reservations > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impossible de supprimer une voiture avec des réservations actives"
            )
        
        # Soft delete
        car.is_active = False
        
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la suppression de la voiture"
            )
        
        return True
    
    @staticmethod
    def get_car_statistics(db: Session) -> CarStats:
        """
        Récupère les statistiques des voitures
        """
        # Statistiques générales
        total_cars = db.query(Car).filter(Car.is_active == True).count()
        
        # Par disponibilité
        by_availability = {}
        availability_stats = db.query(
            Car.disponibilite,
            func.count(Car.id)
        ).filter(Car.is_active == True).group_by(Car.disponibilite).all()
        
        for status, count in availability_stats:
            by_availability[status] = count
        
        # Par marque
        by_brand = {}
        brand_stats = db.query(
            Car.marque,
            func.count(Car.id)
        ).filter(Car.is_active == True).group_by(Car.marque).order_by(desc(func.count(Car.id))).limit(10).all()
        
        for brand, count in brand_stats:
            by_brand[brand] = count
        
        # Prix moyen
        avg_price_result = db.query(func.avg(Car.prix)).filter(Car.is_active == True).scalar()
        average_price = float(avg_price_result) if avg_price_result else 0.0
        
        # Fourchette de prix
        min_price = db.query(func.min(Car.prix)).filter(Car.is_active == True).scalar() or 0
        max_price = db.query(func.max(Car.prix)).filter(Car.is_active == True).scalar() or 0
        
        price_range = {
            "min": float(min_price),
            "max": float(max_price)
        }
        
        return CarStats(
            total=total_cars,
            by_availability=by_availability,
            by_brand=by_brand,
            average_price=average_price,
            price_range=price_range
        )
    
    @staticmethod
    def search_cars(db: Session, search_term: str, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """
        Recherche les voitures par terme de recherche
        """
        query = db.query(Car).filter(Car.is_active == True)
        
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                (Car.marque.ilike(search_pattern)) |
                (Car.modele.ilike(search_pattern)) |
                (Car.couleur.ilike(search_pattern)) |
                (Car.motorisation.ilike(search_pattern)) |
                (Car.description.ilike(search_pattern))
            )
        
        # Trier par pertinence
        query = query.order_by(desc(Car.created_at))
        
        return paginate_query(query, page, size)
    
    @staticmethod
    def get_available_cars(db: Session, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """
        Récupère uniquement les voitures disponibles
        """
        query = db.query(Car).filter(
            Car.is_active == True,
            Car.disponibilite == "disponible"
        ).order_by(desc(Car.created_at))
        
        return paginate_query(query, page, size)
    
    @staticmethod
    def get_cars_by_brand(db: Session, brand: str, page: int = 1, size: int = 20) -> Dict[str, Any]:
        """
        Récupère les voitures d'une marque spécifique
        """
        query = db.query(Car).filter(
            Car.is_active == True,
            Car.marque.ilike(f"%{brand}%")
        ).order_by(desc(Car.created_at))
        
        return paginate_query(query, page, size)
    
    @staticmethod
    def update_car_availability(db: Session, car_id: int, availability: str) -> CarResponse:
        """
        Met à jour uniquement la disponibilité d'une voiture
        """
        car = db.query(Car).filter(Car.id == car_id, Car.is_active == True).first()
        if not car:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Voiture non trouvée"
            )
        
        if availability not in ["disponible", "loue", "vendu"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Statut de disponibilité invalide"
            )
        
        car.disponibilite = availability
        
        try:
            db.commit()
            db.refresh(car)
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la mise à jour de la disponibilité"
            )
        
        return CarResponse.from_orm(car)