#!/bin/bash

# =================================================================
# SCRIPT DE LANCEMENT STREAMLIT - QUANTUM MOTORS
# =================================================================

echo "🚗 Quantum Motors - Lancement de l'Interface Streamlit"
echo "======================================================"

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification de l'environnement virtuel
check_venv() {
    if [[ "$VIRTUAL_ENV" == "" ]]; then
        log_warn "Environnement virtuel non activé"
        
        if [ -d "streamlit_env" ]; then
            log_info "Activation de l'environnement virtuel..."
            source streamlit_env/bin/activate
        else
            log_error "Environnement virtuel non trouvé. Créez-le avec:"
            echo "python3 -m venv streamlit_env"
            echo "source streamlit_env/bin/activate"
            echo "pip install -r requirements.txt"
            exit 1
        fi
    else
        log_info "✅ Environnement virtuel activé: $VIRTUAL_ENV"
    fi
}

# Vérification des dépendances
check_dependencies() {
    log_info "Vérification des dépendances..."
    
    if ! python -c "import streamlit" 2>/dev/null; then
        log_error "Streamlit non installé. Installation..."
        pip install -r requirements.txt
    else
        log_info "✅ Streamlit installé"
    fi
    
    if ! python -c "import requests" 2>/dev/null; then
        log_warn "Installation des dépendances manquantes..."
        pip install -r requirements.txt
    fi
}

# Vérification de la connexion Backend
check_backend() {
    log_info "Vérification de la connexion Backend..."
    
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        log_info "✅ Backend API accessible sur http://localhost:8000"
    else
        log_warn "⚠️  Backend API non accessible"
        log_warn "Assurez-vous que le backend FastAPI est démarré:"
        log_warn "cd ../backend && source venv/bin/activate && python run.py"
    fi
}

# Nettoyage du cache Streamlit
clean_cache() {
    if [ "$1" == "--clean" ]; then
        log_info "Nettoyage du cache Streamlit..."
        rm -rf .streamlit/cache
        streamlit cache clear
    fi
}

# Fonction principale
main() {
    log_info "Démarrage de l'application Streamlit..."
    
    # Vérifications
    check_venv
    check_dependencies
    check_backend
    
    # Nettoyage si demandé
    clean_cache $1
    
    # Configuration
    export STREAMLIT_SERVER_HEADLESS=true
    export STREAMLIT_SERVER_PORT=8501
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    
    log_info "🚀 Lancement de Streamlit sur http://localhost:8501"
    log_info "📱 Également accessible via http://$(hostname -I | awk '{print $1}'):8501"
    log_info ""
    log_info "Pour arrêter l'application: Ctrl+C"
    log_info "======================================================"
    
    # Lancement de Streamlit
    streamlit run app.py \
        --server.port 8501 \
        --server.address 0.0.0.0 \
        --server.headless true \
        --browser.gatherUsageStats false
}

# Affichage de l'aide
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean    Nettoie le cache avant le lancement"
    echo "  --help     Affiche cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0                 # Lancement normal"
    echo "  $0 --clean        # Lancement avec nettoyage du cache"
}

# Gestion des arguments
case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --clean)
        main --clean
        ;;
    "")
        main
        ;;
    *)
        log_error "Option inconnue: $1"
        show_help
        exit 1
        ;;
esac