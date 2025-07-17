#!/usr/bin/env python3
"""
Script d'initialisation complète de la base de données
Usage: python init_db.py [--reset] [--sample-data] [--check]
"""

import sys
import os
import argparse
import subprocess
from pathlib import Path

# Ajouter le répertoire racine au path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy import text, create_engine
from app.configs.database import engine, create_tables, SessionLocal
from app.models.database import User, Car, Reservation
from app.utils.auth import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_mysql_connection():
    """Vérifier que MySQL est accessible"""
    try:
        # Tenter connexion MySQL root (sans base spécifique)
        mysql_engine = create_engine("mysql+pymysql://root@localhost")
        with mysql_engine.connect() as conn:
            result = conn.execute(text("SELECT VERSION()"))
            version = result.scalar()
            logger.info(f"✅ MySQL connecté - Version: {version}")
            return True
    except Exception as e:
        logger.error(f"❌ Impossible de se connecter à MySQL: {e}")
        logger.error("Vérifiez que MySQL est démarré et accessible")
        return False


def run_sql_script(script_path):
    """Exécuter un script SQL via mysql command line"""
    try:
        cmd = f"mysql -u root < {script_path}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ Script exécuté: {script_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Erreur lors de l'exécution du script {script_path}")
        logger.error(f"Sortie: {e.stdout}")
        logger.error(f"Erreur: {e.stderr}")
        return False


def setup_database():
    """Setup complet de la base de données"""
    logger.info("🔧 Initialisation de la base de données...")
    
    # 1. Vérifier MySQL
    if not check_mysql_connection():
        return False
    
    # 2. Exécuter le script de setup
    script_path = Path(__file__).parent / "database_setup.sql"
    if not run_sql_script(script_path):
        return False
    
    # 3. Créer les tables avec SQLAlchemy
    try:
        create_tables()
        logger.info("✅ Tables créées avec SQLAlchemy")
    except Exception as e:
        logger.error(f"❌ Erreur lors de la création des tables: {e}")
        return False
    
    logger.info("🎉 Base de données initialisée avec succès !")
    return True


def load_sample_data():
    """Charger les données de démonstration"""
    logger.info("📊 Chargement des données de démonstration...")
    
    script_path = Path(__file__).parent / "sample_data.sql"
    if not run_sql_script(script_path):
        return False
    
    logger.info("✅ Données de démonstration chargées")
    return True


def create_admin_user():
    """Créer un utilisateur admin par défaut"""
    db = SessionLocal()
    try:
        # Vérifier si admin existe déjà
        admin = db.query(User).filter(User.email == "admin@cardealership.com").first()
        if admin:
            logger.info("ℹ️  Utilisateur admin existe déjà")
            return
        
        # Créer admin
        admin_user = User(
            email="admin@cardealership.com",
            password=get_password_hash("admin123"),
            nom="Administrator",
            prenom="Super",
            telephone="0123456789",
            role="vendeur",
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        logger.info("✅ Utilisateur admin créé : admin@cardealership.com / admin123")
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Erreur lors de la création de l'admin: {e}")
    finally:
        db.close()


def check_database_status():
    """Vérifier l'état de la base de données"""
    logger.info("🔍 Vérification de l'état de la base...")
    
    try:
        db = SessionLocal()
        
        # Compter les enregistrements
        users_count = db.query(User).count()
        cars_count = db.query(Car).count()
        reservations_count = db.query(Reservation).count()
        
        logger.info(f"📊 Statistiques base de données:")
        logger.info(f"   - Utilisateurs: {users_count}")
        logger.info(f"   - Voitures: {cars_count}")
        logger.info(f"   - Réservations: {reservations_count}")
        
        # Lister les utilisateurs
        users = db.query(User).all()
        logger.info("👤 Utilisateurs:")
        for user in users:
            logger.info(f"   - {user.email} ({user.role})")
        
        db.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification: {e}")
        return False


def reset_database():
    """Remise à zéro complète de la base"""
    logger.warning("⚠️  ATTENTION: Cette opération va SUPPRIMER toutes les données !")
    
    response = input("Êtes-vous sûr de vouloir continuer ? (tapez 'RESET' pour confirmer): ")
    if response != "RESET":
        logger.info("❌ Opération annulée")
        return False
    
    logger.info("🗑️  Remise à zéro de la base...")
    
    # 1. Setup de base
    if not setup_database():
        return False
    
    # 2. Données de demo
    if not load_sample_data():
        return False
    
    logger.info("✅ Base de données remise à zéro avec succès")
    return True


def main():
    parser = argparse.ArgumentParser(description="Gestion de la base de données Car Dealership")
    parser.add_argument("--reset", action="store_true", help="Remise à zéro complète")
    parser.add_argument("--sample-data", action="store_true", help="Charger données de démo")
    parser.add_argument("--check", action="store_true", help="Vérifier l'état")
    parser.add_argument("--admin", action="store_true", help="Créer utilisateur admin")
    
    args = parser.parse_args()
    
    if args.check:
        check_database_status()
    elif args.reset:
        reset_database()
    elif args.sample_data:
        load_sample_data()
    elif args.admin:
        create_admin_user()
    else:
        # Setup standard
        if setup_database():
            create_admin_user()


if __name__ == "__main__":
    main()


# # scripts/init_db.py
# """
# Script d'initialisation de la base de données
# """

# import sys
# import os
# from pathlib import Path

# # Ajouter le répertoire racine au path
# root_dir = Path(__file__).parent.parent
# sys.path.insert(0, str(root_dir))

# from sqlalchemy import text
# from app.configs.database import engine, create_tables, SessionLocal
# from app.models.database import User, Car, Reservation
# from app.utils.auth import get_password_hash
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# def init_database():
#     """
#     Initialise la base de données avec les tables et données de base
#     """
#     try:
#         logger.info("🔧 Initialisation de la base de données...")
        
#         # Créer les tables
#         create_tables()
#         logger.info("✅ Tables créées avec succès")
        
#         # Créer des données de test
#         create_sample_data()
#         logger.info("✅ Données de test créées")
        
#         logger.info("🎉 Initialisation terminée avec succès !")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur lors de l'initialisation: {e}")
#         raise


# def create_sample_data():
#     """
#     Crée des données de test pour le développement
#     """
#     db = SessionLocal()
#     try:
#         # Vérifier si des données existent déjà
#         if db.query(User).first():
#             logger.info("ℹ️  Des données existent déjà, création ignorée")
#             return
        
#         # Créer un vendeur de test
#         vendeur = User(
#             email="vendeur@test.com",
#             password=get_password_hash("password123"),
#             nom="Durand",
#             prenom="Jean",
#             telephone="0123456789",
#             role="vendeur",
#             is_active=True
#         )
#         db.add(vendeur)
        
#         # Créer un client de test
#         client = User(
#             email="client@test.com",
#             password=get_password_hash("password123"),
#             nom="Martin",
#             prenom="Marie",
#             telephone="0987654321",
#             role="client",
#             is_active=True
#         )
#         db.add(client)
        
#         # Créer quelques voitures de test
#         cars_data = [
#             {
#                 "marque": "Toyota",
#                 "modele": "Corolla",
#                 "couleur": "blanc",
#                 "motorisation": "Essence 1.2L",
#                 "prix": 22000.00,
#                 "disponibilite": "disponible",
#                 "description": "Berline compacte fiable et économique",
#                 "kilometrage": 15000,
#                 "annee": 2021
#             },
#             {
#                 "marque": "BMW",
#                 "modele": "Série 3",
#                 "couleur": "noir",
#                 "motorisation": "Diesel 2.0L",
#                 "prix": 35000.00,
#                 "disponibilite": "disponible",
#                 "description": "Berline premium avec finitions haut de gamme",
#                 "kilometrage": 8000,
#                 "annee": 2022
#             },
#             {
#                 "marque": "Renault",
#                 "modele": "Clio",
#                 "couleur": "rouge",
#                 "motorisation": "Essence 1.0L",
#                 "prix": 18000.00,
#                 "disponibilite": "disponible",
#                 "description": "Citadine pratique et moderne",
#                 "kilometrage": 25000,
#                 "annee": 2020
#             },
#             {
#                 "marque": "Mercedes",
#                 "modele": "Classe A",
#                 "couleur": "gris",
#                 "motorisation": "Essence 1.6L",
#                 "prix": 28000.00,
#                 "disponibilite": "loue",
#                 "description": "Compacte premium avec technologie avancée",
#                 "kilometrage": 12000,
#                 "annee": 2021
#             },
#             {
#                 "marque": "Volkswagen",
#                 "modele": "Golf",
#                 "couleur": "bleu",
#                 "motorisation": "Diesel 1.6L",
#                 "prix": 24000.00,
#                 "disponibilite": "vendu",
#                 "description": "Compacte polyvalente et robuste",
#                 "kilometrage": 18000,
#                 "annee": 2020
#             }
#         ]
        
#         for car_data in cars_data:
#             car = Car(**car_data)
#             db.add(car)
        
#         db.commit()
#         logger.info("📝 Utilisateurs de test créés:")
#         logger.info("   - Vendeur: vendeur@test.com / password123")
#         logger.info("   - Client: client@test.com / password123")
#         logger.info(f"🚗 {len(cars_data)} voitures de test créées")
        
#     except Exception as e:
#         db.rollback()
#         logger.error(f"Erreur lors de la création des données de test: {e}")
#         raise
#     finally:
#         db.close()


# def reset_database():
#     """
#     Remet à zéro la base de données (supprime toutes les données)
#     """
#     logger.warning("⚠️  ATTENTION: Cette opération va supprimer toutes les données !")
    
#     response = input("Êtes-vous sûr de vouloir continuer ? (oui/non): ")
#     if response.lower() not in ["oui", "yes", "y"]:
#         logger.info("❌ Opération annulée")
#         return
    
#     try:
#         from app.configs.database import drop_tables
        
#         logger.info("🗑️  Suppression des tables...")
#         drop_tables()
        
#         logger.info("🔧 Recréation des tables...")
#         init_database()
        
#         logger.info("✅ Base de données remise à zéro avec succès")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur lors de la remise à zéro: {e}")
#         raise


# def check_database_connection():
#     """
#     Vérifie la connexion à la base de données
#     """
#     try:
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             logger.info("✅ Connexion à la base de données réussie")
#             return True
#     except Exception as e:
#         logger.error(f"❌ Erreur de connexion à la base de données: {e}")
#         return False


# if __name__ == "__main__":
#     import argparse
    
#     parser = argparse.ArgumentParser(description="Script d'initialisation de la base de données")
#     parser.add_argument("--reset", action="store_true", help="Remet à zéro la base de données")
#     parser.add_argument("--check", action="store_true", help="Vérifie la connexion")
    
#     args = parser.parse_args()
    
#     if args.check:
#         check_database_connection()
#     elif args.reset:
#         reset_database()
#     else:
#         # Vérifier la connexion avant l'initialisation
#         if check_database_connection():
#             init_database()
#         else:
#             sys.exit(1)