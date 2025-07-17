# pages/reservations.py
"""Page de gestion des réservations"""
import streamlit as st
from components.header import render_page_header

def render(api_client):
    render_page_header("Gestion des Réservations", "Suivi et gestion des réservations", "📋")
    
    st.success("✅ Page réservations - En cours de développement")
    
    # Test de connexion API
    success, reservations, message = api_client.get_reservations()
    if success:
        st.write(f"📊 {len(reservations)} réservations trouvées")
        if reservations:
            st.json(reservations[0])  # Affichage de la première réservation
    else:
        st.error(f"❌ {message}")
