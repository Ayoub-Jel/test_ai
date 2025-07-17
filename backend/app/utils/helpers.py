# app/utils/helpers.py
from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Query
from sqlalchemy import or_, and_
from math import ceil
from datetime import datetime
import re
import json


def validate_email(email: str) -> bool:
    """
    Valide le format d'un email
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Valide le format d'un numéro de téléphone français
    """
    # Supprime tous les espaces et caractères spéciaux
    cleaned_phone = re.sub(r'[^\d+]', '', phone)
    
    # Vérifie les formats français
    patterns = [
        r'^0[1-9]\d{8}$',  # 0123456789
        r'^\+33[1-9]\d{8}$',  # +33123456789
        r'^33[1-9]\d{8}$'   # 33123456789
    ]
    
    return any(re.match(pattern, cleaned_phone) for pattern in patterns)


def format_price(price: float) -> str:
    """
    Formate un prix en euros
    """
    return f"{price:,.2f} €".replace(',', ' ')


def paginate_query(
    query: Query,
    page: int = 1,
    size: int = 20,
    max_size: int = 100
) -> Dict[str, Any]:
    """
    Pagine une requête SQLAlchemy
    """
    # Validation des paramètres
    page = max(1, page)
    size = min(max(1, size), max_size)
    
    # Calcul de l'offset
    offset = (page - 1) * size
    
    # Exécution de la requête avec pagination
    total = query.count()
    items = query.offset(offset).limit(size).all()
    
    # Calcul du nombre de pages
    pages = ceil(total / size) if total > 0 else 0
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1
    }


def apply_car_filters(query: Query, filters: Dict[str, Any]) -> Query:
    """
    Applique les filtres sur une requête de voitures
    """
    if filters.get("marque"):
        query = query.filter(
            or_(
                query.column_descriptions[0]['type'].marque.ilike(f"%{filters['marque']}%"),
                query.column_descriptions[0]['type'].marque.ilike(f"{filters['marque']}%")
            )
        )
    
    if filters.get("modele"):
        query = query.filter(
            query.column_descriptions[0]['type'].modele.ilike(f"%{filters['modele']}%")
        )
    
    if filters.get("couleur"):
        query = query.filter(
            query.column_descriptions[0]['type'].couleur.ilike(f"%{filters['couleur']}%")
        )
    
    if filters.get("motorisation"):
        query = query.filter(
            query.column_descriptions[0]['type'].motorisation.ilike(f"%{filters['motorisation']}%")
        )
    
    if filters.get("prix_min") is not None:
        query = query.filter(query.column_descriptions[0]['type'].prix >= filters["prix_min"])
    
    if filters.get("prix_max") is not None:
        query = query.filter(query.column_descriptions[0]['type'].prix <= filters["prix_max"])
    
    if filters.get("disponibilite"):
        query = query.filter(query.column_descriptions[0]['type'].disponibilite == filters["disponibilite"])
    
    if filters.get("annee_min") is not None:
        query = query.filter(query.column_descriptions[0]['type'].annee >= filters["annee_min"])
    
    if filters.get("annee_max") is not None:
        query = query.filter(query.column_descriptions[0]['type'].annee <= filters["annee_max"])
    
    if filters.get("kilometrage_max") is not None:
        query = query.filter(query.column_descriptions[0]['type'].kilometrage <= filters["kilometrage_max"])
    
    return query


def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    Nettoie et limite une chaîne de caractères
    """
    if not text:
        return ""
    
    # Supprime les caractères dangereux
    sanitized = re.sub(r'[<>"\']', '', text.strip())
    
    # Limite la longueur
    return sanitized[:max_length]


def convert_to_json(obj: Any) -> str:
    """
    Convertit un objet en JSON en gérant les dates
    """
    def json_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
    
    return json.dumps(obj, default=json_serializer, ensure_ascii=False)


def generate_search_terms(text: str) -> List[str]:
    """
    Génère des termes de recherche à partir d'un texte
    """
    if not text:
        return []
    
    # Normalise le texte
    normalized = text.lower().strip()
    
    # Sépare par espaces et caractères spéciaux
    terms = re.split(r'[\s\-_.,;:!?]+', normalized)
    
    # Filtre les termes vides et trop courts
    terms = [term for term in terms if len(term) >= 2]
    
    return list(set(terms))  # Supprime les doublons


def calculate_age_from_year(year: Optional[int]) -> Optional[int]:
    """
    Calcule l'âge d'un véhicule à partir de son année
    """
    if not year:
        return None
    
    current_year = datetime.now().year
    return current_year - year


def format_kilometrage(km: Optional[int]) -> str:
    """
    Formate le kilométrage
    """
    if km is None:
        return "Non spécifié"
    
    if km == 0:
        return "0 km"
    
    if km < 1000:
        return f"{km} km"
    
    return f"{km:,} km".replace(',', ' ')


def validate_reservation_dates(date_debut: datetime, date_fin: Optional[datetime], type_transaction: str) -> bool:
    """
    Valide les dates d'une réservation
    """
    now = datetime.now()
    
    # La date de début ne peut pas être dans le passé
    if date_debut < now:
        return False
    
    # Pour les locations, la date de fin est obligatoire
    if type_transaction == "location":
        if not date_fin:
            return False
        if date_fin <= date_debut:
            return False
    
    return True


def get_availability_color(availability: str) -> str:
    """
    Retourne la couleur associée à un statut de disponibilité
    """
    colors = {
        "disponible": "#28a745",  # Vert
        "loue": "#ffc107",        # Jaune
        "vendu": "#dc3545"        # Rouge
    }
    return colors.get(availability, "#6c757d")  # Gris par défaut


def get_status_color(status: str) -> str:
    """
    Retourne la couleur associée à un statut de réservation
    """
    colors = {
        "en_attente": "#ffc107",   # Jaune
        "confirmee": "#28a745",    # Vert
        "annulee": "#dc3545",      # Rouge
        "terminee": "#6c757d"      # Gris
    }
    return colors.get(status, "#6c757d")