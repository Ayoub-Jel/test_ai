# app/configs/settings.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "mysql+pymysql://car_leadership:cars@localhost/car_dealership"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173"
    ]
    
    # App
    APP_NAME: str = "Car Dealership API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # Email (avec valeurs par défaut)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "your-email@gmail.com"
    SMTP_PASSWORD: str = "your-app-password"

    # Redis (avec valeur par défaut)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Upload (avec valeurs par défaut)
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    UPLOAD_DIR: str = "/app/uploads"
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]

    # Logging (avec valeurs par défaut)
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/app/logs/app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Instance globale des paramètres
settings = Settings()


# # app/configs/settings.py
# from pydantic_settings import BaseSettings
# from typing import List
# import os


# class Settings(BaseSettings):
#     # Database
#     DATABASE_URL: str = "mysql+pymysql://username:password@localhost/car_dealership"
    
#     # Security
#     SECRET_KEY: str = "your-secret-key-change-in-production"
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
#     # CORS
#     CORS_ORIGINS: List[str] = [
#         "http://localhost:3000",
#         "http://localhost:8080",
#         "http://localhost:5173",
#         "http://127.0.0.1:3000",
#         "http://127.0.0.1:8080",
#         "http://127.0.0.1:5173"
#     ]
    
#     # App
#     APP_NAME: str = "Car Dealership API"
#     APP_VERSION: str = "1.0.0"
#     DEBUG: bool = True
    
#     # Pagination
#     DEFAULT_PAGE_SIZE: int = 20
#     MAX_PAGE_SIZE: int = 100

#         # Email
#     SMTP_HOST: str
#     SMTP_PORT: int
#     SMTP_USER: str
#     SMTP_PASSWORD: str

#     # Redis
#     REDIS_URL: str

#     # Upload
#     MAX_UPLOAD_SIZE: int
#     UPLOAD_DIR: str
#     ALLOWED_EXTENSIONS: List[str]  # à parser automatiquement

#     # Logging
#     LOG_LEVEL: str
#     LOG_FILE: str
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = True


# # Instance globale des paramètres
# settings = Settings()