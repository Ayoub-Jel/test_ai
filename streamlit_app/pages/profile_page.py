# pages/profile.py
"""Page de profil utilisateur"""
import streamlit as st
from components.header import render_page_header
from utils.session_state import get_user

def render(api_client):
    render_page_header("Mon Profil", "Gestion de mon compte utilisateur", "👤")
    
    user = get_user()
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📋 Informations")
        st.write(f"**Nom:** {user.get('nom', '')}")
        st.write(f"**Prénom:** {user.get('prenom', '')}")
        st.write(f"**Email:** {user.get('email', '')}")
        st.write(f"**Rôle:** {user.get('role', '')}")
    
    with col2:
        st.subheader("⚙️ Paramètres")
        st.info("🚧 Modification du profil - En cours de développement")
    
    if st.button("🚪 Se Déconnecter"):
        from utils.session_state import clear_session_state
        clear_session_state()
        st.rerun()