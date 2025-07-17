#!/usr/bin/env python3
"""
🚗 Quantum Motors - Application de Gestion de Concessionnaire
Interface Streamlit pour la gestion des voitures et réservations
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Configuration de la page
st.set_page_config(
    page_title="Quantum Motors - Gestion Concessionnaire",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ajout du répertoire racine au path
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

# Imports des modules locaux
from streamlit_app.pages import cars_page, dashboard_page, profile_page
from streamlit_app.utils.auth_ui_utils import AuthManager
from utils.api_client import APIClient
from utils.session_state import init_session_state, clear_session_state
from components.sidebar import render_sidebar
from components.header import render_header
from streamlit_app.pages import reservations_page

# CSS personnalisé
def load_css():
    """Charge les styles CSS personnalisés"""
    st.markdown("""
    <style>
    /* Variables CSS */
    :root {
        --primary-color: #3182ce;
        --secondary-color: #4a5568;
        --success-color: #38a169;
        --warning-color: #d69e2e;
        --error-color: #e53e3e;
        --background-color: #f7fafc;
    }
    
    /* Masquer le menu Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Personnalisation de la sidebar */
    .css-1d391kg {
        background-color: var(--background-color);
    }
    
    /* Carte personnalisée */
    .custom-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Métriques personnalisées */
    .metric-card {
        background: linear-gradient(135deg, var(--primary-color), #4299e1);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 0.5rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* Boutons personnalisés */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #2c5282;
        transform: translateY(-2px);
    }
    
    /* Alertes personnalisées */
    .alert-success {
        background-color: #f0fff4;
        border: 1px solid #68d391;
        color: #22543d;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .alert-error {
        background-color: #fed7d7;
        border: 1px solid #fc8181;
        color: #742a2a;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .alert-warning {
        background-color: #fffbeb;
        border: 1px solid #f6ad55;
        color: #744210;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Header personnalisé */
    .main-header {
        background: linear-gradient(90deg, var(--primary-color), #4299e1);
        color: white;
        padding: 1rem 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Statut badges */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        display: inline-block;
    }
    
    .status-disponible {
        background-color: #c6f6d5;
        color: #22543d;
    }
    
    .status-loue {
        background-color: #fed7af;
        color: #744210;
    }
    
    .status-vendu {
        background-color: #fed7d7;
        color: #742a2a;
    }
    
    .status-en-attente {
        background-color: #fef5e7;
        color: #744210;
    }
    
    .status-confirmee {
        background-color: #c6f6d5;
        color: #22543d;
    }
    
    .status-annulee {
        background-color: #fed7d7;
        color: #742a2a;
    }
    
    /* Navigation tabs */
    .nav-tabs {
        background: white;
        border-radius: 12px;
        padding: 0.5rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .main-footer {
        margin-top: 3rem;
        padding: 2rem;
        background: #f7fafc;
        border-radius: 12px;
        text-align: center;
        color: #4a5568;
        border-top: 1px solid #e2e8f0;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-card {
            margin: 0.25rem;
            padding: 1rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    """Fonction principale de l'application"""
    
    # Chargement des styles CSS
    load_css()
    
    # Initialisation de l'état de session
    init_session_state()
    
    # Initialisation des clients
    auth_manager = AuthManager()
    api_client = APIClient()
    
    # Vérification de l'authentification
    if not st.session_state.authenticated:
        # Page de connexion
        render_login_page(auth_manager)
    else:
        # Application principale
        render_main_app(api_client)

def render_login_page(auth_manager):
    """Rend la page de connexion"""
    
    # Header de connexion
    st.markdown("""
    <div class="main-header">
        <h1>🚗 Quantum Motors</h1>
        <p>Système de Gestion de Concessionnaire Automobile</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Colonnes pour centrer le formulaire
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.subheader("🔐 Connexion")
        
        # Formulaire de connexion
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="admin@cardealership.com")
            password = st.text_input("🔒 Mot de passe", type="password", placeholder="admin123")
            
            col1_btn, col2_btn, col3_btn = st.columns([1, 2, 1])
            with col2_btn:
                login_button = st.form_submit_button("Se connecter", use_container_width=True)
            
            if login_button:
                if email and password:
                    success, user_data, message = auth_manager.login(email, password)
                    
                    if success:
                        st.session_state.authenticated = True
                        st.session_state.user = user_data
                        st.session_state.token = user_data.get('access_token')
                        st.success(f"✅ {message}")
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
        
        # Comptes de démonstration
        st.markdown("---")
        st.subheader("🧪 Comptes de Test")
        
        col1_demo, col2_demo = st.columns(2)
        
        with col1_demo:
            if st.button("👤 Client Test", use_container_width=True):
                success, user_data, message = auth_manager.login("client@test.com", "client123")
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.session_state.token = user_data.get('access_token')
                    st.rerun()
        
        with col2_demo:
            if st.button("💼 Vendeur Admin", use_container_width=True):
                success, user_data, message = auth_manager.login("admin@cardealership.com", "admin123")
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = user_data
                    st.session_state.token = user_data.get('access_token')
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informations sur l'application
        st.markdown("---")
        st.info("""
        **🔍 Application de Démonstration**
        
        Cette application permet la gestion complète d'un concessionnaire automobile :
        - 📊 Tableau de bord avec statistiques
        - 🚗 Gestion du catalogue de véhicules
        - 📋 Gestion des réservations
        - 👥 Gestion des utilisateurs
        
        **Backend API** : http://localhost:8000/docs
        """)

def render_main_app(api_client):
    """Rend l'application principale après connexion"""
    
    # Header principal
    render_header()
    
    # Sidebar avec navigation
    selected_page = render_sidebar()
    
    # Rendu de la page sélectionnée
    if selected_page == "Dashboard":
        dashboard_page.render(api_client)
    elif selected_page == "Véhicules":
        cars_page.render(api_client)
    elif selected_page == "Réservations":
        reservations_page.render(api_client)
    elif selected_page == "Profil":
        profile_page.render(api_client)
    elif selected_page == "Déconnexion":
        clear_session_state()
        st.rerun()
    
    # Footer
    render_footer()

def render_footer():
    """Rend le footer de l'application"""
    st.markdown("""
    <div class="main-footer">
        <p>© 2024 Quantum Motors - Système de Gestion de Concessionnaire</p>
        <p>Développé avec ❤️ using Streamlit & FastAPI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()