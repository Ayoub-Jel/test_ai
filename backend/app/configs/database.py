# app/configs/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from configs.settings import settings

# Configuration du moteur de base de données
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Affiche les requêtes SQL en mode debug
    pool_pre_ping=True,   # Vérifie la connexion avant utilisation
    pool_recycle=300      # Renouvelle les connexions toutes les 5 minutes
)

# Configuration de la session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base pour les modèles ORM
Base = declarative_base()


def get_db():
    """
    Générateur de session de base de données pour dependency injection
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crée toutes les tables dans la base de données
    """
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Supprime toutes les tables de la base de données
    """
    Base.metadata.drop_all(bind=engine)