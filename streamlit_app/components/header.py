# components/header.py
"""
Composant header principal
"""

import streamlit as st
from datetime import datetime
from utils.session_state import get_user, get_user_role, display_flash_messages

def render_header():
    """Rend le header principal de l'application"""
    
    # Afficher les messages flash s'il y en a
    display_flash_messages()
    
    # Header principal
    col1, col2, col3 = st.columns([3, 1, 2])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <div style="font-size: 2.5rem;">🚗</div>
            <div>
                <h1 style="margin: 0; color: #2d3748;">Quantum Motors</h1>
                <p style="margin: 0; color: #718096; font-size: 1rem;">Gestion de Concessionnaire</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Heure actuelle
        current_time = datetime.now().strftime("%H:%M")
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="font-size: 1.5rem; font-weight: bold; color: #3182ce;">{current_time}</div>
            <div style="font-size: 0.9rem; color: #718096;">{current_date}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        render_user_status()
    
    # Ligne de séparation
    st.markdown("---")

def render_user_status():
    """Rend le statut utilisateur dans le header"""
    user = get_user()
    role = get_user_role()
    
    # Badge de statut utilisateur
    role_color = {
        "vendeur": "#3182ce",
        "client": "#38a169",
        "admin": "#e53e3e"
    }.get(role, "#718096")
    
    role_icon = {
        "vendeur": "💼",
        "client": "👤", 
        "admin": "⚡"
    }.get(role, "👤")
    
    st.markdown(f"""
    <div style="text-align: right;">
        <div style="
            display: inline-block;
            background-color: {role_color};
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 600;
        ">
            {role_icon} {role.title()}
        </div>
        <div style="font-size: 0.9rem; color: #718096; margin-top: 0.25rem;">
            {user.get('prenom', '')} {user.get('nom', '')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_page_header(title: str, subtitle: str = "", icon: str = "📄"):
    """
    Rend un header de page
    
    Args:
        title: Titre de la page
        subtitle: Sous-titre optionnel
        icon: Icône de la page
    """
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
    ">
        <h1 style="margin: 0; font-size: 2.5rem;">
            {icon} {title}
        </h1>
        {f'<p style="margin: 0.5rem 0 0 0; font-size: 1.1rem; opacity: 0.9;">{subtitle}</p>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)

def render_breadcrumb(items: list):
    """
    Rend un fil d'Ariane
    
    Args:
        items: Liste des éléments du breadcrumb
    """
    breadcrumb_html = " > ".join([
        f'<span style="color: #3182ce;">{item}</span>' if i == len(items) - 1 
        else f'<span style="color: #718096;">{item}</span>'
        for i, item in enumerate(items)
    ])
    
    st.markdown(f"""
    <div style="
        background: #f7fafc;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
    ">
        🏠 {breadcrumb_html}
    </div>
    """, unsafe_allow_html=True)

def render_search_bar(placeholder: str = "Rechercher...", key: str = "search"):
    """
    Rend une barre de recherche
    
    Args:
        placeholder: Texte placeholder
        key: Clé unique pour le widget
        
    Returns:
        str: Terme de recherche
    """
    col1, col2 = st.columns([4, 1])
    
    with col1:
        search_term = st.text_input(
            "",
            placeholder=placeholder,
            key=key,
            label_visibility="collapsed"
        )
    
    with col2:
        search_button = st.button("🔍 Rechercher", use_container_width=True)
    
    return search_term if search_button or search_term else ""

def render_action_bar(actions: list):
    """
    Rend une barre d'actions
    
    Args:
        actions: Liste de dictionnaires avec 'label', 'action', 'type'
    """
    cols = st.columns(len(actions))
    
    results = {}
    
    for i, action in enumerate(actions):
        with cols[i]:
            button_type = action.get('type', 'primary')
            
            # Configuration du bouton selon le type
            if button_type == 'primary':
                if st.button(action['label'], use_container_width=True):
                    results[action['action']] = True
            elif button_type == 'secondary':
                if st.button(action['label'], use_container_width=True):
                    results[action['action']] = True
            elif button_type == 'danger':
                if st.button(action['label'], use_container_width=True):
                    results[action['action']] = True
    
    return results

def render_status_banner(message: str, status_type: str = "info"):
    """
    Rend une bannière de statut
    
    Args:
        message: Message à afficher
        status_type: Type de statut (success, error, warning, info)
    """
    colors = {
        "success": {"bg": "#f0fff4", "border": "#68d391", "text": "#22543d"},
        "error": {"bg": "#fed7d7", "border": "#fc8181", "text": "#742a2a"},
        "warning": {"bg": "#fffbeb", "border": "#f6ad55", "text": "#744210"},
        "info": {"bg": "#ebf8ff", "border": "#63b3ed", "text": "#2c5282"}
    }
    
    color_scheme = colors.get(status_type, colors["info"])
    
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "ℹ️"
    }
    
    icon = icons.get(status_type, "ℹ️")
    
    st.markdown(f"""
    <div style="
        background-color: {color_scheme['bg']};
        border: 1px solid {color_scheme['border']};
        color: {color_scheme['text']};
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    ">
        <span style="font-size: 1.2rem;">{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)

def render_loading_spinner(message: str = "Chargement..."):
    """Rend un spinner de chargement"""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 2rem;
        color: #718096;
    ">
        <div style="
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #e2e8f0;
            border-top: 4px solid #3182ce;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 1rem;
        "></div>
        <p>{message}</p>
    </div>
    
    <style>
    @keyframes spin {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}
    </style>
    """, unsafe_allow_html=True)