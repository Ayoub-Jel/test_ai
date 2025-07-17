#!/bin/bash

# =================================================================
# SCRIPT DE DÉMARRAGE GLOBAL - CAR DEALERSHIP (Backend + Frontend)
# =================================================================

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
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

log_header() {
    echo -e "${CYAN}$1${NC}"
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
        "backend/Dockerfile"
        "backend/requirements.txt"
        "backend/app/main.py"
        "streamlit_app/Dockerfile"
        "streamlit_app/requirements.txt"
        "streamlit_app/app.py"
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
    log_info "Construction des images..."
    docker-compose build --no-cache
    
    # Démarrer les services en arrière-plan
    log_info "Démarrage des services..."
    docker-compose up -d
    
    log_success "Services démarrés"
}

# Attendre que les services soient prêts
wait_for_services() {
    log_info "Attente que les services soient prêts..."
    
    # Attendre MySQL
    log_info "⏳ Attente de MySQL..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose exec mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
            break
        fi
        sleep 2
        ((attempt++))
        echo -ne "Tentative $attempt/$max_attempts...\r"
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "MySQL n'a pas démarré dans les temps"
        exit 1
    fi
    log_success "MySQL est prêt"
    
    # Attendre l'API
    log_info "⏳ Attente de l'API Backend..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8000/health > /dev/null 2>&1; then
            break
        fi
        sleep 2
        ((attempt++))
        echo -ne "Tentative $attempt/$max_attempts...\r"
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "L'API Backend n'a pas démarré dans les temps"
        exit 1
    fi
    log_success "API Backend est prête"
    
    # Attendre le Frontend
    log_info "⏳ Attente du Frontend Streamlit..."
    max_attempts=30
    attempt=0
    while [ $attempt -lt $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
            break
        fi
        sleep 2
        ((attempt++))
        echo -ne "Tentative $attempt/$max_attempts...\r"
    done
    
    if [ $attempt -eq $max_attempts ]; then
        log_error "Le Frontend Streamlit n'a pas démarré dans les temps"
        exit 1
    fi
    log_success "Frontend Streamlit est prêt"
}

# Afficher les informations de connexion
show_info() {
    log_header "==============================================="
    log_header "🚗 CAR DEALERSHIP - DÉPLOYEMENT TERMINÉ 🚗"
    log_header "==============================================="
    echo
    log_success "🎉 Tous les services sont opérationnels !"
    echo
    log_info "📱 INTERFACES UTILISATEUR:"
    echo "  🌐 Frontend (Streamlit): http://localhost:8501"
    echo "  📚 Documentation API: http://localhost:8000/docs"
    echo "  🔧 phpMyAdmin: http://localhost:8081"
    echo
    log_info "🔗 API & SERVICES:"
    echo "  🚀 API Backend: http://localhost:8000"
    echo "  🗄️  MySQL: localhost:3310"
    echo "  🔴 Redis: localhost:6379"
    echo
    log_info "👤 COMPTES DE TEST:"
    echo "  👨‍💼 Admin: admin@cardealership.com / password123"
    echo "  🛒 Vendeur: vendeur@test.com / password123"
    echo "  👤 Client: client@test.com / password123"
    echo
    log_info "🛠️  COMMANDES UTILES:"
    echo "  📋 Voir les logs: docker-compose logs -f"
    echo "  🔄 Redémarrer: docker-compose restart"
    echo "  🛑 Arrêter: docker-compose down"
    echo "  🐚 Shell API: docker-compose exec api bash"
    echo "  🐚 Shell Frontend: docker-compose exec frontend bash"
    echo "  💾 MySQL CLI: docker-compose exec mysql mysql -u car_user -p car_dealership"
    echo
    log_header "==============================================="
}

# Vérifier la santé des services
health_check() {
    log_info "🔍 Vérification de la santé des services..."
    echo
    
    # Vérifier MySQL
    if docker-compose exec mysql mysqladmin ping -h localhost --silent 2>/dev/null; then
        log_success "MySQL: ✅ OK"
    else
        log_error "MySQL: ❌ ERREUR"
    fi
    
    # Vérifier l'API
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API Backend: ✅ OK"
    else
        log_error "API Backend: ❌ ERREUR"
    fi
    
    # Vérifier Streamlit
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        log_success "Frontend Streamlit: ✅ OK"
    else
        log_error "Frontend Streamlit: ❌ ERREUR"
    fi
    
    # Vérifier phpMyAdmin
    if curl -f http://localhost:8081 > /dev/null 2>&1; then
        log_success "phpMyAdmin: ✅ OK"
    else
        log_warning "phpMyAdmin: ⚠️  Problème de connexion"
    fi
    
    # Vérifier Redis
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        log_success "Redis: ✅ OK"
    else
        log_error "Redis: ❌ ERREUR"
    fi
    
    echo
}

# Exécuter les tests
run_tests() {
    log_info "🧪 Exécution des tests..."
    
    # Tests du backend
    log_info "Test du backend..."
    if docker-compose --profile testing run --rm test; then
        log_success "Tests backend: ✅ PASSÉS"
    else
        log_error "Tests backend: ❌ ÉCHOUÉS"
    fi
    
    # Test simple du frontend
    log_info "Test du frontend..."
    if curl -f http://localhost:8501/_stcore/health > /dev/null 2>&1; then
        log_success "Tests frontend: ✅ PASSÉS"
    else
        log_error "Tests frontend: ❌ ÉCHOUÉS"
    fi
}

# Afficher les logs
show_logs() {
    case "${2:-all}" in
        "api"|"backend")
            docker-compose logs -f api
            ;;
        "frontend"|"streamlit")
            docker-compose logs -f frontend
            ;;
        "mysql"|"db")
            docker-compose logs -f mysql
            ;;
        "redis")
            docker-compose logs -f redis
            ;;
        "all"|*)
            docker-compose logs -f
            ;;
    esac
}

# Fonction principale
main() {
    log_header "🐳 Car Dealership - Backend + Frontend"
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
            log_info "Redémarrage des services..."
            docker-compose restart
            wait_for_services
            show_info
            ;;
        "stop")
            log_info "🛑 Arrêt des services..."
            docker-compose down
            log_success "Services arrêtés"
            ;;
        "clean")
            log_warning "⚠️  Cette opération va supprimer tous les conteneurs et volumes"
            read -p "Continuer ? (y/N) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cleanup
            fi
            ;;
        "logs")
            show_logs "$@"
            ;;
        "health")
            health_check
            ;;
        "test")
            run_tests
            ;;
        "shell")
            case "${2:-api}" in
                "frontend"|"streamlit")
                    docker-compose exec frontend bash
                    ;;
                "api"|"backend"|*)
                    docker-compose exec api bash
                    ;;
            esac
            ;;
        "mysql")
            docker-compose exec mysql mysql -u car_user -p car_dealership
            ;;
        "build")
            log_info "🔨 Reconstruction des images..."
            docker-compose build --no-cache
            log_success "Images reconstruites"
            ;;
        *)
            echo "Usage: $0 {start|restart|stop|clean|logs|health|test|shell|mysql|build}"
            echo
            echo "📋 Commandes disponibles:"
            echo "  start    - Démarrer tous les services"
            echo "  restart  - Redémarrer tous les services"
            echo "  stop     - Arrêter tous les services"
            echo "  clean    - Nettoyer conteneurs et volumes"
            echo "  logs     - Afficher les logs [all|api|frontend|mysql|redis]"
            echo "  health   - Vérifier la santé des services"
            echo "  test     - Exécuter les tests"
            echo "  shell    - Ouvrir un shell [api|frontend]"
            echo "  mysql    - Ouvrir MySQL CLI"
            echo "  build    - Reconstruire les images"
            echo
            echo "📖 Exemples:"
            echo "  $0 start                 # Démarrer tout"
            echo "  $0 logs frontend         # Logs du frontend seulement"
            echo "  $0 shell frontend        # Shell dans le conteneur frontend"
            exit 1
            ;;
    esac
}

# Exécuter la fonction principale
main "$@"