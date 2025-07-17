# scripts/dev.py
"""
Scripts utiles pour le développement
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def run_command(command, check=True):
    """Exécute une commande shell"""
    print(f"🔧 Exécution: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0

def setup_dev_environment():
    """Configure l'environnement de développement"""
    print("🚀 Configuration de l'environnement de développement...")
    
    commands = [
        "python -m pip install --upgrade pip",
        "pip install -r requirements.txt",
        "cp .env.example .env",
    ]
    
    for cmd in commands:
        if not run_command(cmd, check=False):
            print(f"❌ Échec de la commande: {cmd}")
            return False
    
    print("✅ Environnement configuré avec succès!")
    return True

def run_tests():
    """Lance les tests"""
    print("🧪 Lancement des tests...")
    
    # Tests unitaires
    if not run_command("python -m pytest tests/ -v", check=False):
        print("❌ Échec des tests unitaires")
        return False
    
    # Tests de l'API
    if not run_command("python scripts/test_api.py", check=False):
        print("❌ Échec des tests API")
        return False
    
    print("✅ Tous les tests sont passés!")
    return True

def format_code():
    """Formate le code avec black et isort"""
    print("🎨 Formatage du code...")
    
    commands = [
        "black app/ scripts/ --line-length 100",
        "isort app/ scripts/ --profile black",
        "flake8 app/ --max-line-length 100 --ignore E203,W503"
    ]
    
    for cmd in commands:
        run_command(cmd, check=False)
    
    print("✅ Code formaté!")

def generate_requirements():
    """Génère le fichier requirements.txt"""
    print("📦 Génération des requirements...")
    
    # Requirements de base
    base_requirements = [
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "sqlalchemy==2.0.23",
        "pymysql==1.1.0",
        "python-jose[cryptography]==3.3.0",
        "passlib[bcrypt]==1.7.4",
        "bcrypt==4.1.2",
        "python-multipart==0.0.6",
        "python-dotenv==1.0.0",
        "email-validator==2.1.0",
        "python-dateutil==2.8.2"
    ]
    
    # Requirements de développement
    dev_requirements = [
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "httpx==0.25.2",
        "black==23.11.0",
        "isort==5.12.0",
        "flake8==6.1.0"
    ]
    
    with open("requirements.txt", "w") as f:
        f.write("# Production requirements\n")
        for req in base_requirements:
            f.write(f"{req}\n")
        
        f.write("\n# Development requirements (optional)\n")
        for req in dev_requirements:
            f.write(f"# {req}\n")
    
    print("✅ Requirements.txt généré!")

def build_docker():
    """Construit l'image Docker"""
    print("🐳 Construction de l'image Docker...")
    
    commands = [
        "docker build -t car-dealership-api .",
        "docker tag car-dealership-api car-dealership-api:latest"
    ]
    
    for cmd in commands:
        if not run_command(cmd):
            return False
    
    print("✅ Image Docker construite!")
    return True

def deploy_docker():
    """Déploie avec Docker Compose"""
    print("🚀 Déploiement avec Docker Compose...")
    
    commands = [
        "docker-compose down",
        "docker-compose up --build -d",
        "sleep 10",  # Attendre que les services démarrent
        "docker-compose exec -T api python scripts/init_db.py"
    ]
    
    for cmd in commands:
        if not run_command(cmd, check=False):
            print(f"⚠️  Problème avec: {cmd}")
    
    print("✅ Déploiement terminé!")
    print("📡 API disponible sur: http://localhost:8000")
    print("📊 phpMyAdmin sur: http://localhost:8080")

def backup_database():
    """Sauvegarde la base de données"""
    print("💾 Sauvegarde de la base de données...")
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_car_dealership_{timestamp}.sql"
    
    cmd = f"""docker-compose exec -T mysql mysqldump \
        -u car_user -pcar_password car_dealership > backups/{backup_file}"""
    
    # Créer le dossier de sauvegarde
    os.makedirs("backups", exist_ok=True)
    
    if run_command(cmd, check=False):
        print(f"✅ Sauvegarde créée: backups/{backup_file}")
    else:
        print("❌ Échec de la sauvegarde")

def restore_database(backup_file):
    """Restaure la base de données"""
    print(f"🔄 Restauration de la base de données depuis {backup_file}...")
    
    if not os.path.exists(backup_file):
        print(f"❌ Fichier de sauvegarde non trouvé: {backup_file}")
        return False
    
    cmd = f"""docker-compose exec -T mysql mysql \
        -u car_user -pcar_password car_dealership < {backup_file}"""
    
    if run_command(cmd, check=False):
        print("✅ Base de données restaurée!")
        return True
    else:
        print("❌ Échec de la restauration")
        return False

def show_logs():
    """Affiche les logs de l'application"""
    print("📋 Affichage des logs...")
    run_command("docker-compose logs -f api", check=False)

def clean_docker():
    """Nettoie les ressources Docker"""
    print("🧹 Nettoyage des ressources Docker...")
    
    commands = [
        "docker-compose down -v",
        "docker system prune -f",
        "docker volume prune -f"
    ]
    
    for cmd in commands:
        run_command(cmd, check=False)
    
    print("✅ Nettoyage terminé!")

def main():
    parser = argparse.ArgumentParser(description="Scripts de développement")
    parser.add_argument("command", choices=[
        "setup", "test", "format", "requirements", 
        "docker-build", "docker-deploy", "backup", 
        "restore", "logs", "clean"
    ], help="Commande à exécuter")
    parser.add_argument("--file", help="Fichier de sauvegarde pour la restauration")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup_dev_environment()
    elif args.command == "test":
        run_tests()
    elif args.command == "format":
        format_code()
    elif args.command == "requirements":
        generate_requirements()
    elif args.command == "docker-build":
        build_docker()
    elif args.command == "docker-deploy":
        deploy_docker()
    elif args.command == "backup":
        backup_database()
    elif args.command == "restore":
        if not args.file:
            print("❌ Veuillez spécifier un fichier avec --file")
            sys.exit(1)
        restore_database(args.file)
    elif args.command == "logs":
        show_logs()
    elif args.command == "clean":
        clean_docker()

if __name__ == "__main__":
    main()