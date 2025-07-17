# utils/session_state.py
"""
Gestion du state de session pour Streamlit
"""

import streamlit as st
from typing import Any, Dict

def init_session_state():
    """Initialise les variables de session state"""
    
    # État d'authentification
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "token" not in st.session_state:
        st.session_state.token = None
    
    if "user" not in st.session_state:
        st.session_state.user = {}
    
    # Cache des données
    if "cars_cache" not in st.session_state:
        st.session_state.cars_cache = []
    
    if "reservations_cache" not in st.session_state:
        st.session_state.reservations_cache = []
    
    if "stats_cache" not in st.session_state:
        st.session_state.stats_cache = {}
    
    # Timestamps pour le cache
    if "cars_cache_time" not in st.session_state:
        st.session_state.cars_cache_time = 0
    
    if "reservations_cache_time" not in st.session_state:
        st.session_state.reservations_cache_time = 0
    
    if "stats_cache_time" not in st.session_state:
        st.session_state.stats_cache_time = 0
    
    # Filtres et état des pages
    if "car_filters" not in st.session_state:
        st.session_state.car_filters = {}
    
    if "reservation_filters" not in st.session_state:
        st.session_state.reservation_filters = {}
    
    # État des formulaires
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    # Page actuelle
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Dashboard"
    
    # Messages flash
    if "flash_messages" not in st.session_state:
        st.session_state.flash_messages = []
    
    # État de chargement
    if "loading" not in st.session_state:
        st.session_state.loading = False

def clear_session_state():
    """Nettoie le session state (déconnexion)"""
    keys_to_clear = [
        "authenticated", "token", "user", 
        "cars_cache", "reservations_cache", "stats_cache",
        "cars_cache_time", "reservations_cache_time", "stats_cache_time",
        "car_filters", "reservation_filters", "form_data",
        "flash_messages"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Réinitialiser après nettoyage
    init_session_state()

def set_page(page_name: str):
    """Définit la page actuelle"""
    st.session_state.current_page = page_name

def get_page() -> str:
    """Retourne la page actuelle"""
    return st.session_state.get("current_page", "Dashboard")

def add_flash_message(message: str, message_type: str = "info"):
    """
    Ajoute un message flash
    
    Args:
        message: Le message à afficher
        message_type: Type de message (success, error, warning, info)
    """
    if "flash_messages" not in st.session_state:
        st.session_state.flash_messages = []
    
    st.session_state.flash_messages.append({
        "message": message,
        "type": message_type
    })

def get_flash_messages():
    """Récupère et vide les messages flash"""
    messages = st.session_state.get("flash_messages", [])
    st.session_state.flash_messages = []
    return messages

def display_flash_messages():
    """Affiche les messages flash et les supprime"""
    messages = get_flash_messages()
    
    for msg in messages:
        message_type = msg.get("type", "info")
        message_text = msg.get("message", "")
        
        if message_type == "success":
            st.success(message_text)
        elif message_type == "error":
            st.error(message_text)
        elif message_type == "warning":
            st.warning(message_text)
        else:
            st.info(message_text)

def set_loading(loading: bool):
    """Définit l'état de chargement"""
    st.session_state.loading = loading

def is_loading() -> bool:
    """Vérifie si l'application est en cours de chargement"""
    return st.session_state.get("loading", False)

def cache_data(key: str, data: Any, expiry_minutes: int = 5):
    """
    Met en cache des données avec expiration
    
    Args:
        key: Clé du cache
        data: Données à mettre en cache
        expiry_minutes: Durée d'expiration en minutes
    """
    import time
    
    cache_key = f"{key}_cache"
    time_key = f"{key}_cache_time"
    
    st.session_state[cache_key] = data
    st.session_state[time_key] = time.time() + (expiry_minutes * 60)

def get_cached_data(key: str) -> Any:
    """
    Récupère des données du cache si elles ne sont pas expirées
    
    Args:
        key: Clé du cache
        
    Returns:
        Les données en cache ou None si expirées/inexistantes
    """
    import time
    
    cache_key = f"{key}_cache"
    time_key = f"{key}_cache_time"
    
    if cache_key in st.session_state and time_key in st.session_state:
        if time.time() < st.session_state[time_key]:
            return st.session_state[cache_key]
    
    return None

def clear_cache(key: str = None):
    """
    Vide le cache
    
    Args:
        key: Clé spécifique à vider, ou None pour tout vider
    """
    if key:
        cache_key = f"{key}_cache"
        time_key = f"{key}_cache_time"
        
        if cache_key in st.session_state:
            del st.session_state[cache_key]
        if time_key in st.session_state:
            del st.session_state[time_key]
    else:
        # Vider tout le cache
        cache_keys = [k for k in st.session_state.keys() if k.endswith("_cache") or k.endswith("_cache_time")]
        for k in cache_keys:
            del st.session_state[k]

def save_form_data(form_name: str, data: Dict):
    """Sauvegarde les données d'un formulaire"""
    if "form_data" not in st.session_state:
        st.session_state.form_data = {}
    
    st.session_state.form_data[form_name] = data

def get_form_data(form_name: str) -> Dict:
    """Récupère les données d'un formulaire"""
    return st.session_state.get("form_data", {}).get(form_name, {})

def clear_form_data(form_name: str = None):
    """Vide les données de formulaire"""
    if form_name:
        if "form_data" in st.session_state and form_name in st.session_state.form_data:
            del st.session_state.form_data[form_name]
    else:
        st.session_state.form_data = {}

def set_filters(filter_type: str, filters: Dict):
    """Définit les filtres pour une page"""
    filter_key = f"{filter_type}_filters"
    st.session_state[filter_key] = filters

def get_filters(filter_type: str) -> Dict:
    """Récupère les filtres d'une page"""
    filter_key = f"{filter_type}_filters"
    return st.session_state.get(filter_key, {})

def clear_filters(filter_type: str = None):
    """Vide les filtres"""
    if filter_type:
        filter_key = f"{filter_type}_filters"
        st.session_state[filter_key] = {}
    else:
        filter_keys = [k for k in st.session_state.keys() if k.endswith("_filters")]
        for k in filter_keys:
            st.session_state[k] = {}

def get_user() -> Dict:
    """Récupère l'utilisateur actuel"""
    return st.session_state.get("user", {})

def get_user_role() -> str:
    """Récupère le rôle de l'utilisateur actuel"""
    user = get_user()
    return user.get("role", "")

def is_authenticated() -> bool:
    """Vérifie si l'utilisateur est authentifié"""
    return st.session_state.get("authenticated", False)

def get_token() -> str:
    """Récupère le token d'authentification"""
    return st.session_state.get("token", "")

def debug_session_state():
    """Affiche le contenu du session state pour debug"""
    st.sidebar.markdown("### 🐛 Debug Session State")
    
    with st.sidebar.expander("Voir Session State"):
        for key, value in st.session_state.items():
            if not key.startswith("_"):  # Éviter les clés internes de Streamlit
                st.write(f"**{key}:** {type(value)}")
                if not isinstance(value, (dict, list)) or len(str(value)) < 100:
                    st.write(value)
                else:
                    st.write(f"[{type(value).__name__} avec {len(value) if hasattr(value, '__len__') else '?'} éléments]")