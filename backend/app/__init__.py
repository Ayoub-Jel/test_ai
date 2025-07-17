
# app/__init__.py
"""
Application de gestion de concessionnaire automobile
"""

__version__ = "1.0.0"
__author__ = "Votre Nom"
__email__ = "votre.email@example.com"


# # app/__init__.py
# """
# Application de gestion de concessionnaire automobile
# """

# __version__ = "1.0.0"
# __author__ = "Votre Nom"
# __email__ = "votre.email@example.com"

# # app/configs/__init__.py
# """
# Module de configuration de l'application
# """

# from app.configs.settings import settings
# from app.configs.database import get_db, create_tables, drop_tables

# __all__ = ["settings", "get_db", "create_tables", "drop_tables"]

# # app/models/__init__.py
# """
# Module des modèles de données
# """

# from app.models.database import User, Car, Reservation, AuditLog
# from app.models.schema import (
#     UserCreate, UserLogin, UserResponse, Token,
#     CarCreate, CarUpdate, CarResponse, CarFilter,
#     ReservationCreate, ReservationUpdate, ReservationResponse,
#     DashboardStats, CarStats
# )

# __all__ = [
#     # Database models
#     "User", "Car", "Reservation", "AuditLog",
#     # Pydantic schemas
#     "UserCreate", "UserLogin", "UserResponse", "Token",
#     "CarCreate", "CarUpdate", "CarResponse", "CarFilter",
#     "ReservationCreate", "ReservationUpdate", "ReservationResponse",
#     "DashboardStats", "CarStats"
# ]

# # app/services/__init__.py
# """
# Module des services métier
# """

# from app.services.auth_service import AuthService
# from app.services.cars_service import CarService
# from app.services.reservation_service import ReservationService

# __all__ = ["AuthService", "CarService", "ReservationService"]

# # app/utils/__init__.py
# """
# Module des utilitaires
# """

# from app.utils.auth import (
#     get_current_user,
#     get_current_active_user,
#     require_role,
#     require_roles,
#     require_vendeur,
#     require_client_or_vendeur
# )
# from app.utils.helpers import (
#     validate_email,
#     validate_phone,
#     format_price,
#     paginate_query,
#     sanitize_string
# )

# __all__ = [
#     # Auth utilities
#     "get_current_user", "get_current_active_user",
#     "require_role", "require_roles", "require_vendeur", "require_client_or_vendeur",
#     # Helper utilities
#     "validate_email", "validate_phone", "format_price",
#     "paginate_query", "sanitize_string"
# ]

# # app/routers/__init__.py
# """
# Module des routeurs API
# """

# from . import auth, cars, reservations

# __all__ = ["auth", "cars", "reservations"]