# pages/cars.py
"""Page de gestion des véhicules"""
import streamlit as st
from components.header import render_page_header

def render(api_client):
    render_page_header("Gestion des Véhicules", "Catalogue et gestion du parc automobile", "🚗")
    
    st.success("✅ Page véhicules - En cours de développement")
    
    # Test de connexion API
    success, cars, message = api_client.get_cars()
    if success:
        st.write(f"📊 {len(cars)} véhicules trouvés")
        if cars:
            st.json(cars[0])  # Affichage du premier véhicule
    else:
        st.error(f"❌ {message}")