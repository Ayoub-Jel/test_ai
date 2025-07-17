#!/bin/bash

# =================================================================
# SCRIPT DE DÉMARRAGE DOCKER - CAR DEALERSHIP
# =================================================================

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier que Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    
    log_success "Docker et Docker Compose sont installés"
}

# Vérifier que les fichiers nécessaires existent
check_files() {
    local required_files=(
        "docker-compose.yml"
        "Dockerfile"
        "requirements.txt"
        "app/main.py"
        "scripts/01-setup.sql"
        "scripts/02-sample-data.sql"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Fichier manquant: $file"
            exit 1
        fi
    done
    
    log_success "Tous les fichiers nécessaires sont présents"
}

# Nettoyer les anciens conteneurs
cleanup() {
    log_info "Nettoyage des anciens conteneurs..."
    docker-compose down --remove-orphans --volumes || true
    docker system prune -f || true
    log_success "Nettoyage terminé"
}

# Construire et démarrer les services
start_services() {
    log_info "Construction et démarrage des services..."
    
    # Construire les images
    log_info "Construction de l'image backend..."
    docker-compose build --no-cache
    
    # Démarrer les services
    log_info "Démarrage des services..."
    docker-compose up -d
    
    log_success "Services démarrés"
}

# Attendre que les services soient prêts
wait_for_services() {
    log_info "Attente que les services soient prêts..."
    
    # Attendre MySQL
    log_info "Attente de MySQL..."
    while ! docker-compose exec mysql mysqladmin ping -h localhost --silent; do
        sleep 2
    done
    log_success "MySQL est prêt"
    
    # Attendre l'API
    log_info "Attente de l'API..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            break
        fi
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "L'API n'a pas démarré dans les temps"
        exit 1
    fi
    
    log_success "API est prête"
}

# Afficher les informations de connexion
show_info() {
    log_success "=== CAR DEALERSHIP DOCKER SETUP TERMINÉ ==="
    echo
    log_info "🚗 API Backend: http://localhost:8000"
    log_info "📚 Documentation API: http://localhost:8000/docs"
    log_info "🔧 phpMyAdmin: http://localhost:8080"
    log_info "🗄️  MySQL: localhost:3306"
    log_info "🔴 Redis: localhost:6379"
    echo
    log_info "Comptes de test disponibles:"
    echo "  👨‍💼 Admin: admin@cardealership.com / password123"
    echo "  🛒 Vendeur: vendeur@test.com / password123"
    echo "  👤 Client: client@test.com / password123"
    echo
    log_info "Commandes utiles:"
    echo "  - Voir les logs: docker-compose logs -f"
    echo "  - Arrêter: docker-compose down"
    echo "  - Redémarrer: docker-compose restart"
    echo "  - Shell API: docker-compose exec api bash"
    echo "  - Shell MySQL: docker-compose exec mysql mysql -u car_user -p car_dealership"
}

# Vérifier la santé des services
health_check() {
    log_info "Vérification de la santé des services..."
    
    # Vérifier MySQL
    if docker-compose exec mysql mysqladmin ping -h localhost --silent; then
        log_success "MySQL: OK"
    else
        log_error "MySQL: ERREUR"
    fi
    
    # Vérifier l'API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API: OK"
    else
        log_error "API: ERREUR"
    fi
    
    # Vérifier Redis
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis: OK"
    else
        log_error "Redis: ERREUR"
    fi
}

# Fonction principale
main() {
    log_info "🐳 Démarrage de Car Dealership avec Docker"
    echo
    
    case "${1:-start}" in
        "start")
            check_docker
            check_files
            start_services
            wait_for_services
            show_info
            ;;
        "restart")
            check_docker
            docker-compose restart
            wait_for_services
            show_info
            ;;
        "stop")
            log_info "Arrêt des services..."
            docker-compose down
            log_success "Services arrêtés"
            ;;
        "clean")
            log_warning "Cette opération va supprimer tous les conteneurs et volumes"
            read -p "Continuer ? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cleanup
            fi
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "health")
            health_check
            ;;
        "shell")
            docker-compose exec api bash
            ;;
        "mysql")
            docker-compose exec mysql mysql -u car_user -p car_dealership
            ;;
        *)
            echo "Usage: $0 {start|restart|stop|clean|logs|health|shell|mysql}"
            echo
            echo "Commandes disponibles:"
            echo "  start   - Démarrer tous les services"
            echo "  restart - Redémarrer tous les services"
            echo "  stop    - Arrêter tous les services"
            echo "  clean   - Nettoyer conteneurs et volumes"
            echo "  logs    - Afficher les logs en temps réel"
            echo "  health  - Vérifier la santé des services"
            echo "  shell   - Ouvrir un shell dans le conteneur API"
            echo "  mysql   - Ouvrir MySQL CLI"
            exit 1
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"