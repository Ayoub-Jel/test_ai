#!/usr/bin/env python3
"""
Script de validation complet pour vérifier le bon fonctionnement 
du setup Docker complet (Backend FastAPI + Frontend Streamlit)
"""

import requests
import json
import time
import sys
import subprocess
from typing import Dict, Any
import urllib.parse

# Configuration
API_BASE_URL = "http://localhost:8000"
FRONTEND_BASE_URL = "http://localhost:8501"
TIMEOUT = 60
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
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

def log_info(message: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

def log_success(message: str):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def log_warning(message: str):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def log_error(message: str):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def log_header(message: str):
    print(f"{Colors.CYAN}{Colors.BOLD}=== {message} ==={Colors.NC}")

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
        
        running_services = result.stdout.strip().split('\n') if result.stdout.strip() else []
        expected_services = ["mysql", "api", "frontend", "phpmyadmin", "redis"]
        
        all_running = True
        for service in expected_services:
            if service in running_services:
                log_success(f"Service {service}: ✅ En cours d'exécution")
            else:
                log_error(f"Service {service}: ❌ Arrêté")
                all_running = False
        
        return all_running
    except subprocess.CalledProcessError as e:
        log_error(f"Erreur lors de la vérification des services: {e}")
        return False

def wait_for_service(url: str, service_name: str, health_endpoint: str = None):
    """Attendre qu'un service soit disponible"""
    log_info(f"Attente de la disponibilité de {service_name}...")
    
    test_url = f"{url}{health_endpoint}" if health_endpoint else url
    
    for attempt in range(TIMEOUT):
        try:
            response = requests.get(test_url, timeout=5)
            if response.status_code == 200:
                log_success(f"{service_name} disponible")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
        if attempt % 10 == 0:  # Afficher le progrès toutes les 10 secondes
            print(f"⏳ Tentative {attempt + 1}/{TIMEOUT} pour {service_name}...")
    
    log_error(f"{service_name} n'est pas disponible après {TIMEOUT} secondes")
    return False

def test_api_endpoints():
    """Tester les endpoints principaux de l'API"""
    log_info("Test des endpoints de l'API...")
    
    endpoints = [
        ("/", "Endpoint racine"),
        ("/health", "Endpoint health"),
        ("/docs", "Documentation Swagger"),
        ("/api/cars/", "Liste des voitures"),
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                log_success(f"{description}: ✅")
            elif response.status_code == 401 and endpoint == "/api/cars/":
                # Normal pour un endpoint protégé
                log_success(f"{description}: ✅ (Authentification requise)")
            else:
                log_error(f"{description}: ❌ Status {response.status_code}")
                return False
        except Exception as e:
            log_error(f"{description}: ❌ - {e}")
            return False
    
    return True

def test_frontend_endpoints():
    """Tester les endpoints du frontend Streamlit"""
    log_info("Test des endpoints du frontend...")
    
    endpoints = [
        ("/_stcore/health", "Health check"),
        ("/_stcore/allowed-message-origins", "Message origins"),
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{FRONTEND_BASE_URL}{endpoint}", timeout=10)
            if response.status_code == 200:
                log_success(f"Frontend {description}: ✅")
            else:
                log_warning(f"Frontend {description}: ⚠️  Status {response.status_code}")
        except Exception as e:
            log_warning(f"Frontend {description}: ⚠️  - {e}")
    
    # Test de la page principale
    try:
        response = requests.get(FRONTEND_BASE_URL, timeout=10)
        if response.status_code == 200 and "streamlit" in response.text.lower():
            log_success("Frontend page principale: ✅")
            return True
        else:
            log_error(f"Frontend page principale: ❌ Status {response.status_code}")
            return False
    except Exception as e:
        log_error(f"Frontend page principale: ❌ - {e}")
        return False

def test_authentication():
    """Tester l'authentification via l'API"""
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
                log_success(f"Authentification {role}: ✅")
            else:
                log_error(f"Authentification {role}: ❌ - Status {response.status_code}")
                return False
                
        except Exception as e:
            log_error(f"Authentification {role}: ❌ - {e}")
            return False
    
    return True

def test_database_operations():
    """Tester les opérations de base de données via l'API"""
    log_info("Test des opérations de base de données...")
    
    try:
        # Se connecter en tant que vendeur
        login_response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json=TEST_CREDENTIALS["vendeur"],
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
            log_success(f"Lecture base de données: ✅ ({data.get('total', 0)} voitures)")
        else:
            log_error(f"Lecture base de données: ❌ - Status {response.status_code}")
            return False
        
        # Tester les statistiques
        stats_response = requests.get(
            f"{API_BASE_URL}/api/cars/statistics",
            headers=headers,
            timeout=10
        )
        
        if stats_response.status_code == 200:
            log_success("Statistiques base de données: ✅")
            return True
        else:
            log_warning(f"Statistiques base de données: ⚠️  - Status {stats_response.status_code}")
            return True  # Non critique
            
    except Exception as e:
        log_error(f"Test base de données: ❌ - {e}")
        return False

def test_external_services():
    """Tester les services externes"""
    log_info("Test des services externes...")
    
    services = [
        ("http://localhost:8081", "phpMyAdmin"),
        ("http://localhost:3310", "MySQL", "mysql"),
    ]
    
    for url, name, *service_type in services:
        try:
            if service_type and service_type[0] == "mysql":
                # Pour MySQL, on teste via l'API plutôt que directement
                continue
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                log_success(f"{name}: ✅")
            else:
                log_warning(f"{name}: ⚠️  Status {response.status_code}")
        except Exception as e:
            log_warning(f"{name}: ⚠️  - {e}")
    
    return True

def test_integration():
    """Tester l'intégration frontend-backend"""
    log_info("Test de l'intégration frontend-backend...")
    
    # Vérifier que le frontend peut accéder à l'API
    # Note: Ceci nécessiterait une API endpoint spécifique dans Streamlit
    # Pour l'instant, on vérifie juste que les deux services répondent
    
    api_available = False
    frontend_available = False
    
    try:
        api_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        api_available = api_response.status_code == 200
    except:
        pass
    
    try:
        frontend_response = requests.get(f"{FRONTEND_BASE_URL}/_stcore/health", timeout=5)
        frontend_available = frontend_response.status_code == 200
    except:
        pass
    
    if api_available and frontend_available:
        log_success("Intégration frontend-backend: ✅ (Services disponibles)")
        return True
    else:
        log_error("Intégration frontend-backend: ❌ (Services non disponibles)")
        return False

def generate_full_report():
    """Générer un rapport de validation complet"""
    log_header("RAPPORT DE VALIDATION COMPLET")
    
    tests = [
        ("Services Docker", check_docker_services),
        ("API disponible", lambda: wait_for_service(API_BASE_URL, "API Backend", "/health")),
        ("Frontend disponible", lambda: wait_for_service(FRONTEND_BASE_URL, "Frontend Streamlit", "/_stcore/health")),
        ("Endpoints API", test_api_endpoints),
        ("Endpoints Frontend", test_frontend_endpoints),
        ("Authentification", test_authentication),
        ("Base de données", test_database_operations),
        ("Services externes", test_external_services),
        ("Intégration", test_integration),
    ]
    
    results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tests_passed": 0,
        "tests_failed": 0,
        "details": []
    }
    
    print("\n" + "="*80)
    
    for test_name, test_func in tests:
        log_info(f"🧪 Test: {test_name}")
        try:
            result = test_func()
            if result:
                results["tests_passed"] += 1
                results["details"].append({"test": test_name, "status": "PASSED"})
                log_success(f"✅ {test_name}: RÉUSSI")
            else:
                results["tests_failed"] += 1
                results["details"].append({"test": test_name, "status": "FAILED"})
                log_error(f"❌ {test_name}: ÉCHOUÉ")
        except Exception as e:
            log_error(f"🔥 Exception dans {test_name}: {e}")
            results["tests_failed"] += 1
            results["details"].append({"test": test_name, "status": "ERROR", "error": str(e)})
        
        print("-" * 60)
    
    # Résumé final
    total_tests = results["tests_passed"] + results["tests_failed"]
    success_rate = (results["tests_passed"] / total_tests * 100) if total_tests > 0 else 0
    
    log_header("RÉSUMÉ FINAL")
    print(f"📊 Tests réussis: {Colors.GREEN}{results['tests_passed']}{Colors.NC}")
    print(f"📊 Tests échoués: {Colors.RED}{results['tests_failed']}{Colors.NC}")
    print(f"📊 Taux de réussite: {Colors.CYAN}{success_rate:.1f}%{Colors.NC}")
    
    if results["tests_failed"] == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 SUCCÈS COMPLET !{Colors.NC}")
        print(f"{Colors.GREEN}Tous les services fonctionnent correctement.{Colors.NC}")
        print_access_info()
        return True
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ ÉCHECS DÉTECTÉS{Colors.NC}")
        print(f"{Colors.RED}Certains tests ont échoué. Vérifiez les logs ci-dessus.{Colors.NC}")
        print_troubleshooting_info()
        return False

def print_access_info():
    """Afficher les informations d'accès"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}🌐 ACCÈS AUX SERVICES{Colors.NC}")
    print(f"Frontend (Streamlit): {Colors.YELLOW}http://localhost:8501{Colors.NC}")
    print(f"API Backend: {Colors.YELLOW}http://localhost:8000{Colors.NC}")
    print(f"Documentation API: {Colors.YELLOW}http://localhost:8000/docs{Colors.NC}")
    print(f"phpMyAdmin: {Colors.YELLOW}http://localhost:8081{Colors.NC}")
    
    print(f"\n{Colors.CYAN}{Colors.BOLD}👤 COMPTES DE TEST{Colors.NC}")
    for role, creds in TEST_CREDENTIALS.items():
        print(f"{role.capitalize()}: {Colors.YELLOW}{creds['email']}{Colors.NC} / {Colors.YELLOW}{creds['password']}{Colors.NC}")

def print_troubleshooting_info():
    """Afficher les informations de dépannage"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}🔧 COMMANDES DE DÉPANNAGE{Colors.NC}")
    print("Vérifier les logs:")
    print("  docker-compose logs api")
    print("  docker-compose logs frontend")
    print("  docker-compose logs mysql")
    print("\nVérifier les services:")
    print("  docker-compose ps")
    print("  docker-compose top")
    print("\nRedémarrer les services:")
    print("  docker-compose restart")
    print("  docker-compose down && docker-compose up -d")

def main():
    """Fonction principale"""
    print(f"{Colors.CYAN}{Colors.BOLD}")
    print("=" * 80)
    print("🚗 VALIDATION COMPLÈTE - CAR DEALERSHIP")
    print("   Backend FastAPI + Frontend Streamlit")
    print("=" * 80)
    print(f"{Colors.NC}")
    
    success = generate_full_report()
    
    print("\n" + "="*80)
    
    if success:
        print(f"{Colors.GREEN}{Colors.BOLD}✅ VALIDATION RÉUSSIE !{Colors.NC}")
        print(f"{Colors.GREEN}L'application est prête à être utilisée.{Colors.NC}")
        sys.exit(0)
    else:
        print(f"{Colors.RED}{Colors.BOLD}❌ VALIDATION ÉCHOUÉE{Colors.NC}")
        print(f"{Colors.RED}Des problèmes ont été détectés.{Colors.NC}")
        sys.exit(1)

if __name__ == "__main__":
    main()