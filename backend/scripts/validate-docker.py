#!/usr/bin/env python3
"""
Script de validation pour vérifier le bon fonctionnement du setup Docker
"""

import requests
import json
import time
import sys
import subprocess
from typing import Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30
TEST_CREDENTIALS = {
    "admin": {"email": "admin@cardealership.com", "password": "password123"},
    "vendeur": {"email": "vendeur@test.com", "password": "password123"},
    "client": {"email": "client@test.com", "password": "password123"}
}

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    NC = '\033[0m'  # No Color

def log_info(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def check_docker_services():
    """Vérifier que les services Docker sont actifs"""
    log_info("Vérification des services Docker...")
    
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--services", "--filter", "status=running"],
            capture_output=True,
            text=True,
            check=True
        )
        
        running_services = result.stdout.strip().split('\n')
        expected_services = ["mysql", "api", "phpmyadmin", "redis"]
        
        for service in expected_services:
            if service in running_services:
                log_success(f"Service {service}: ✓ En cours d'exécution")
            else:
                log_error(f"Service {service}: ✗ Arrêté")
                return False
        
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Erreur lors de la vérification des services: {e}")
        return False

def wait_for_api():
    """Attendre que l'API soit disponible"""
    log_info("Attente de la disponibilité de l'API...")
    
    for attempt in range(TIMEOUT):
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                log_success("API disponible")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        print(f"Tentative {attempt + 1}/{TIMEOUT}...", end='\r')
    
    log_error("L'API n'est pas disponible après 30 secondes")
    return False

def test_api_endpoints():
    """Tester les endpoints principaux de l'API"""
    log_info("Test des endpoints de l'API...")
    
    # Test endpoint racine
    try:
        response = requests.get(f"{API_BASE_URL}/")
        assert response.status_code == 200, f"Endpoint racine: {response.status_code}"
        log_success("Endpoint racine: ✓")
    except Exception as e:
        log_error(f"Endpoint racine: ✗ - {e}")
        return False
    
    # Test endpoint health
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        assert response.status_code == 200, f"Endpoint health: {response.status_code}"
        log_success("Endpoint health: ✓")
    except Exception as e:
        log_error(f"Endpoint health: ✗ - {e}")
        return False
    
    # Test endpoint docs
    try:
        response = requests.get(f"{API_BASE_URL}/docs")
        assert response.status_code == 200, f"Endpoint docs: {response.status_code}"
        log_success("Endpoint docs: ✓")
    except Exception as e:
        log_error(f"Endpoint docs: ✗ - {e}")
        return False
    
    return True

def test_authentication():
    """Tester l'authentification"""
    log_info("Test de l'authentification...")
    
    for role, credentials in TEST_CREDENTIALS.items():
        try:
            response = requests.post(
                f"{API_BASE_URL}/api/auth/login",
                json=credentials,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                assert "access_token" in data, f"Token manquant pour {role}"
                assert "user" in data, f"Données utilisateur manquantes pour {role}"
                log_success(f"Authentification {role}: ✓")
            else:
                log_error(f"Authentification {role}: ✗ - Status {response.status_code}")
                return False
                
        except Exception as e:
            log_error(f"Authentification {role}: ✗ - {e}")
            return False
    
    return True

def test_database_connection():
    """Tester la connexion à la base de données via l'API"""
    log_info("Test de la connexion à la base de données...")
    
    try:
        # Se connecter en tant qu'admin
        login_response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS["admin"],
            timeout=10
        )
        
        if login_response.status_code != 200:
            log_error("Impossible de se connecter pour tester la base de données")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Tester l'endpoint des voitures
        response = requests.get(
            f"{API_BASE_URL}/api/cars/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            log_success(f"Base de données: ✓ ({data.get('total', 0)} voitures)")
            return True
        else:
            log_error(f"Test base de données: ✗ - Status {response.status_code}")
            return False
            
    except Exception as e:
        log_error(f"Test base de données: ✗ - {e}")
        return False

def test_crud_operations():
    """Tester les opérations CRUD"""
    log_info("Test des opérations CRUD...")
    
    try:
        # Se connecter en tant que vendeur
        login_response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS["vendeur"],
            timeout=10
        )
        
        if login_response.status_code != 200:
            log_error("Impossible de se connecter pour tester les opérations CRUD")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Créer une voiture test
        car_data = {
            "marque": "TEST",
            "modele": "Model",
            "couleur": "rouge",
            "motorisation": "Test 1.0L",
            "prix": 15000.00,
            "disponibilite": "disponible",
            "description": "Voiture de test",
            "kilometrage": 0,
            "annee": 2024
        }
        
        create_response = requests.post(
            f"{API_BASE_URL}/api/cars/",
            json=car_data,
            headers=headers,
            timeout=10
        )
        
        if create_response.status_code != 201:
            log_error(f"Création voiture: ✗ - Status {create_response.status_code}")
            return False
        
        car_id = create_response.json()["id"]
        log_success(f"Création voiture: ✓ (ID: {car_id})")
        
        # Récupérer la voiture
        get_response = requests.get(
            f"{API_BASE_URL}/api/cars/{car_id}",
            headers=headers,
            timeout=10
        )
        
        if get_response.status_code != 200:
            log_error(f"Récupération voiture: ✗ - Status {get_response.status_code}")
            return False
        
        log_success("Récupération voiture: ✓")
        
        # Supprimer la voiture
        delete_response = requests.delete(
            f"{API_BASE_URL}/api/cars/{car_id}",
            headers=headers,
            timeout=10
        )
        
        if delete_response.status_code != 200:
            log_error(f"Suppression voiture: ✗ - Status {delete_response.status_code}")
            return False
        
        log_success("Suppression voiture: ✓")
        return True
        
    except Exception as e:
        log_error(f"Test CRUD: ✗ - {e}")
        return False

def test_external_services():
    """Tester les services externes (phpMyAdmin, etc.)"""
    log_info("Test des services externes...")
    
    # Test phpMyAdmin
    try:
        response = requests.get("http://localhost:8080", timeout=10)
        if response.status_code == 200:
            log_success("phpMyAdmin: ✓")
        else:
            log_warning(f"phpMyAdmin: Status {response.status_code}")
    except Exception as e:
        log_warning(f"phpMyAdmin: ✗ - {e}")
    
    return True

def generate_report():
    """Générer un rapport de validation"""
    log_info("Génération du rapport de validation...")
    
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "api_base_url": API_BASE_URL,
        "tests_passed": 0,
        "tests_failed": 0,
        "details": []
    }
    
    tests = [
        ("Services Docker", check_docker_services),
        ("Disponibilité API", wait_for_api),
        ("Endpoints API", test_api_endpoints),
        ("Authentification", test_authentication),
        ("Base de données", test_database_connection),
        ("Opérations CRUD", test_crud_operations),
        ("Services externes", test_external_services)
    ]
    
    log_info("=" * 60)
    log_info("RAPPORT DE VALIDATION DOCKER")
    log_info("=" * 60)
    
    for test_name, test_func in tests:
        log_info(f"Test: {test_name}")
        try:
            result = test_func()
            if result:
                report["tests_passed"] += 1
                report["details"].append({"test": test_name, "status": "PASSED"})
            else:
                report["tests_failed"] += 1
                report["details"].append({"test": test_name, "status": "FAILED"})
        except Exception as e:
            log_error(f"Exception dans {test_name}: {e}")
            report["tests_failed"] += 1
            report["details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        log_info("-" * 40)
    
    # Résumé final
    total_tests = report["tests_passed"] + report["tests_failed"]
    success_rate = (report["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
    
    log_info("RÉSUMÉ:")
    log_info(f"Tests réussis: {report['tests_passed']}")
    log_info(f"Tests échoués: {report['tests_failed']}")
    log_info(f"Taux de réussite: {success_rate:.1f}%")
    
    if report["tests_failed"] == 0:
        log_success("🎉 Tous les tests sont passés ! Le setup Docker fonctionne correctement.")
        return True
    else:
        log_error("❌ Certains tests ont échoué. Vérifiez les logs ci-dessus.")
        return False

def main():
    """Fonction principale"""
    print(f"{Colors.CYAN}=== VALIDATION DU SETUP DOCKER - CAR DEALERSHIP ==={Colors.NC}")
    print()
    
    success = generate_report()
    
    if success:
        print()
        log_success("✅ Validation terminée avec succès !")
        log_info("Vous pouvez maintenant utiliser l'application:")
        log_info("  🚗 API: http://localhost:8000")
        log_info("  📚 Documentation: http://localhost:8000/docs")
        log_info("  🔧 phpMyAdmin: http://localhost:8080")
        sys.exit(0)
    else:
        print()
        log_error("❌ Validation échouée. Vérifiez les erreurs ci-dessus.")
        log_info("Commandes utiles pour diagnostiquer:")
        log_info("  docker-compose logs api")
        log_info("  docker-compose logs mysql")
        log_info("  docker-compose ps")
        sys.exit(1)

if __name__ == "__main__":
    main()