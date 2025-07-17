# components/sidebar.py
"""
Composant de navigation sidebar
"""

import streamlit as st
from utils.session_state import get_user, get_user_role

def render_sidebar():
    """Rend la sidebar avec navigation"""
    
    with st.sidebar:
        # Header utilisateur
        render_user_info()
        
        st.markdown("---")
        
        # Navigation principale
        selected_page = render_navigation()
        
        st.markdown("---")
        
        # Outils et utilitaires
        render_tools()
        
        # Footer sidebar
        render_sidebar_footer()
    
    return selected_page

def render_user_info():
    """Affiche les informations utilisateur"""
    user = get_user()
    role = get_user_role()
    
    # Avatar et nom
    st.markdown(f"""
    <div style="text-align: center; padding: 1rem 0;">
        <div style="
            width: 60px; 
            height: 60px; 
            border-radius: 50%; 
            background: linear-gradient(135deg, #3182ce, #4299e1);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            font-weight: bold;
            margin: 0 auto 0.5rem auto;
        ">
            {get_user_initials()}
        </div>
        <div style="font-weight: bold; color: #2d3748;">
            {user.get('prenom', '')} {user.get('nom', '')}
        </div>
        <div style="color: #718096; font-size: 0.9rem;">
            {get_role_display(role)}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Rend le menu de navigation"""
    user_role = get_user_role()
    
    # Menu principal
    st.markdown("### 🧭 Navigation")
    
    # Pages accessibles à tous
    pages = ["Dashboard"]
    
    # Pages spécifiques au rôle
    if user_role == "vendeur":
        pages.extend(["Véhicules", "Réservations"])
    elif user_role == "client":
        pages.extend(["Véhicules", "Mes Réservations"])
    
    # Page profil accessible à tous
    pages.append("Profil")
    
    # Sélection de la page
    selected = st.radio(
        "Choisir une page",
        pages,
        index=0,
        key="navigation_radio"
    )
    
    # Bouton de déconnexion
    st.markdown("---")
    if st.button("🚪 Déconnexion", use_container_width=True):
        return "Déconnexion"
    
    return selected

def render_tools():
    """Rend les outils et utilitaires"""
    st.markdown("### 🛠️ Outils")
    
    # Actualiser les données
    if st.button("🔄 Actualiser", use_container_width=True):
        # Vider le cache pour forcer le rechargement
        from utils.session_state import clear_cache
        clear_cache()
        st.success("✅ Données actualisées")
        st.rerun()
    
    # Test connexion API
    if st.button("🔌 Tester API", use_container_width=True):
        from utils.api_client import APIClient
        api_client = APIClient()
        
        with st.spinner("Test en cours..."):
            success, message = api_client.test_connection()
            
            if success:
                st.success(message)
            else:
                st.error(message)
    
    # Paramètres (pour les vendeurs)
    if get_user_role() == "vendeur":
        with st.expander("⚙️ Paramètres Avancés"):
            
            # Debug mode
            debug_mode = st.toggle("Mode Debug", value=False)
            if debug_mode:
                from utils.session_state import debug_session_state
                debug_session_state()
            
            # Vider le cache
            if st.button("🗑️ Vider le Cache", use_container_width=True):
                from utils.session_state import clear_cache
                clear_cache()
                st.success("Cache vidé")

def render_sidebar_footer():
    """Rend le footer de la sidebar"""
    st.markdown("---")
    
    # Informations sur l'application
    st.markdown("""
    <div style="text-align: center; font-size: 0.8rem; color: #718096;">
        <p><strong>🚗 Quantum Motors</strong></p>
        <p>Version 1.0.0</p>
        <p>© 2024</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Liens utiles
    with st.expander("📚 Liens Utiles"):
        st.markdown("""
        - [📖 Documentation API](http://localhost:8000/docs)
        - [🔍 API Alternative](http://localhost:8000/redoc)
        - [💻 Code Source](https://github.com/quantum-motors)
        """)

def get_user_initials():
    """Retourne les initiales de l'utilisateur"""
    user = get_user()
    prenom = user.get('prenom', '')
    nom = user.get('nom', '')
    
    initials = ""
    if prenom:
        initials += prenom[0].upper()
    if nom:
        initials += nom[0].upper()
    
    return initials or "👤"

def get_role_display(role: str) -> str:
    """Convertit le rôle en affichage lisible"""
    role_map = {
        "vendeur": "💼 Vendeur",
        "client": "👤 Client",
        "admin": "⚡ Administrateur"
    }
    
    return role_map.get(role, f"👤 {role.title()}")

def render_quick_stats():
    """Affiche des statistiques rapides dans la sidebar"""
    from utils.api_client import APIClient
    from utils.session_state import get_cached_data, cache_data
    
    api_client = APIClient()
    
    # Vérifier le cache
    stats = get_cached_data("quick_stats")
    
    if stats is None:
        # Charger les statistiques
        with st.spinner("Chargement des stats..."):
            success, stats, _ = api_client.get_dashboard_stats()
            
            if success:
                cache_data("quick_stats", stats, expiry_minutes=5)
    
    if stats:
        st.markdown("### 📊 Aperçu Rapide")
        
        # Voitures disponibles
        if "available_cars" in stats:
            st.metric(
                "🚗 Disponibles", 
                stats["available_cars"],
                delta=None
            )
        
        # Réservations en attente
        if "pending_reservations" in stats:
            st.metric(
                "📋 En attente", 
                stats["pending_reservations"],
                delta=None
            )

def render_notifications():
    """Affiche les notifications dans la sidebar"""
    user_role = get_user_role()
    
    if user_role == "vendeur":
        st.markdown("### 🔔 Notifications")
        
        # Simuler quelques notifications (à remplacer par de vraies données)
        notifications = [
            {"type": "warning", "message": "3 réservations en attente"},
            {"type": "info", "message": "Nouveau véhicule ajouté"},
            {"type": "success", "message": "Vente confirmée"}
        ]
        
        for notif in notifications:
            icon = {
                "warning": "⚠️",
                "info": "ℹ️", 
                "success": "✅",
                "error": "❌"
            }.get(notif["type"], "📝")
            
            st.markdown(f"{icon} {notif['message']}")

def render_weather_widget():
    """Widget météo simple (optionnel)"""
    st.markdown("### 🌤️ Météo")
    
    # Simuler des données météo (à remplacer par une vraie API)
    st.markdown("""
    **Paris** ☀️ 22°C  
    Ensoleillé - Vent: 15 km/h
    """)

# Style CSS pour la sidebar
SIDEBAR_CSS = """
<style>
.sidebar-content {
    padding: 1rem;
}

.user-avatar {
    width: 50px;
    height: 50px;
    border-radius: 50%;
    background: linear-gradient(135deg, #3182ce, #4299e1);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    margin: 0 auto;
}

.sidebar-metric {
    background: white;
    padding: 0.5rem;
    border-radius: 8px;
    margin: 0.25rem 0;
    border-left: 4px solid #3182ce;
}

.notification-item {
    background: #f7fafc;
    padding: 0.5rem;
    border-radius: 6px;
    margin: 0.25rem 0;
    font-size: 0.85rem;
    border-left: 3px solid;
}

.notification-warning {
    border-left-color: #d69e2e;
}

.notification-info {
    border-left-color: #3182ce;
}

.notification-success {
    border-left-color: #38a169;
}
</style>
"""