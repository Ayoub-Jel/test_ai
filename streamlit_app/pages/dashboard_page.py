# pages/dashboard.py
"""
Page Dashboard - Vue d'ensemble de l'activité
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from components.header import render_page_header, render_loading_spinner
from utils.session_state import get_cached_data, cache_data, get_user_role
from utils.api_client import APIClient

def render(api_client: APIClient):
    """Rend la page dashboard"""
    
    # Header de la page
    render_page_header(
        "Tableau de Bord", 
        "Vue d'ensemble de l'activité du concessionnaire",
        "📊"
    )
    
    # Chargement des données
    stats_data = load_dashboard_data(api_client)
    
    if stats_data:
        # Métriques principales
        render_main_metrics(stats_data)
        
        st.markdown("---")
        
        # Graphiques et analyses
        col1, col2 = st.columns(2)
        
        with col1:
            render_cars_chart(stats_data, api_client)
        
        with col2:
            render_reservations_chart(stats_data, api_client)
        
        st.markdown("---")
        
        # Activité récente et tableaux
        render_recent_activity(api_client)
        
    else:
        st.error("❌ Impossible de charger les données du dashboard")

def load_dashboard_data(api_client: APIClient):
    """Charge les données du dashboard avec cache"""
    
    # Vérifier le cache
    cached_stats = get_cached_data("dashboard_stats")
    
    if cached_stats is None:
        with st.spinner("Chargement des statistiques..."):
            success, stats_data, message = api_client.get_dashboard_stats()
            
            if success:
                cache_data("dashboard_stats", stats_data, expiry_minutes=3)
                return stats_data
            else:
                st.error(f"Erreur: {message}")
                return None
    
    return cached_stats

def render_main_metrics(stats_data):
    """Rend les métriques principales"""
    
    st.subheader("📈 Métriques Principales")
    
    # Extraire les données
    total_cars = stats_data.get("total_cars", 0)
    available_cars = stats_data.get("available_cars", 0)
    sold_cars = stats_data.get("sold_cars", 0)
    rented_cars = stats_data.get("rented_cars", 0)
    
    total_reservations = stats_data.get("total_reservations", 0)
    pending_reservations = stats_data.get("pending_reservations", 0)
    confirmed_reservations = stats_data.get("confirmed_reservations", 0)
    
    # Calculs
    sales_rate = (sold_cars / total_cars * 100) if total_cars > 0 else 0
    availability_rate = (available_cars / total_cars * 100) if total_cars > 0 else 0
    
    # Affichage en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card(
            "🚗 Total Véhicules",
            total_cars,
            f"{availability_rate:.1f}% disponibles"
        )
    
    with col2:
        render_metric_card(
            "✅ Disponibles",
            available_cars,
            f"Sur {total_cars} véhicules"
        )
    
    with col3:
        render_metric_card(
            "💰 Vendues",
            sold_cars,
            f"{sales_rate:.1f}% du stock"
        )
    
    with col4:
        render_metric_card(
            "📋 Réservations",
            total_reservations,
            f"{pending_reservations} en attente"
        )

def render_metric_card(title, value, subtitle):
    """Rend une carte de métrique"""
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        border-left: 4px solid #3182ce;
    ">
        <h3 style="margin: 0; color: #718096; font-size: 0.9rem; font-weight: 600;">
            {title}
        </h3>
        <h1 style="margin: 0.5rem 0; color: #2d3748; font-size: 2.5rem; font-weight: bold;">
            {value}
        </h1>
        <p style="margin: 0; color: #4a5568; font-size: 0.8rem;">
            {subtitle}
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_cars_chart(stats_data, api_client: APIClient):
    """Rend le graphique de répartition des voitures"""
    
    st.subheader("🚗 Répartition des Véhicules")
    
    # Données pour le graphique
    cars_data = {
        "Statut": ["Disponible", "Loué", "Vendu"],
        "Nombre": [
            stats_data.get("available_cars", 0),
            stats_data.get("rented_cars", 0),
            stats_data.get("sold_cars", 0)
        ],
        "Couleur": ["#38a169", "#d69e2e", "#e53e3e"]
    }
    
    df_cars = pd.DataFrame(cars_data)
    
    # Graphique en secteurs
    fig_pie = px.pie(
        df_cars,
        values="Nombre",
        names="Statut",
        color_discrete_sequence=cars_data["Couleur"],
        title="Répartition par Statut"
    )
    
    fig_pie.update_layout(
        height=300,
        showlegend=True,
        font=dict(size=12)
    )
    
    st.plotly_chart(fig_pie, use_container_width=True)
    
    # Tableau de détails
    with st.expander("📋 Détails des véhicules"):
        render_cars_summary_table(api_client)

def render_reservations_chart(stats_data, api_client: APIClient):
    """Rend le graphique des réservations"""
    
    st.subheader("📋 État des Réservations")
    
    # Données pour le graphique
    reservations_data = {
        "Statut": ["En attente", "Confirmée", "Terminée"],
        "Nombre": [
            stats_data.get("pending_reservations", 0),
            stats_data.get("confirmed_reservations", 0),
            stats_data.get("completed_reservations", 0)
        ]
    }
    
    df_reservations = pd.DataFrame(reservations_data)
    
    # Graphique en barres
    fig_bar = px.bar(
        df_reservations,
        x="Statut",
        y="Nombre",
        color="Statut",
        color_discrete_map={
            "En attente": "#d69e2e",
            "Confirmée": "#38a169", 
            "Terminée": "#3182ce"
        },
        title="Réservations par Statut"
    )
    
    fig_bar.update_layout(
        height=300,
        showlegend=False,
        xaxis_title="",
        yaxis_title="Nombre de réservations"
    )
    
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Tendance des réservations (simulée)
    with st.expander("📈 Tendance des réservations"):
        render_reservations_trend()

def render_cars_summary_table(api_client: APIClient):
    """Rend un tableau résumé des voitures"""
    
    # Charger les voitures
    success, cars_data, _ = api_client.get_cars(size=10)
    
    if success and cars_data:
        df = api_client.format_car_data(cars_data)
        
        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Aucune voiture dans la base de données")
    else:
        st.error("Impossible de charger les données des voitures")

def render_reservations_trend():
    """Rend un graphique de tendance des réservations"""
    
    # Données simulées pour la tendance (à remplacer par de vraies données)
    dates = pd.date_range(
        start=datetime.now() - timedelta(days=30),
        end=datetime.now(),
        freq='D'
    )
    
    # Simulation de données de réservations
    import random
    reservations_count = [random.randint(0, 5) for _ in range(len(dates))]
    
    df_trend = pd.DataFrame({
        "Date": dates,
        "Réservations": reservations_count
    })
    
    fig_trend = px.line(
        df_trend,
        x="Date",
        y="Réservations",
        title="Évolution des réservations (30 derniers jours)",
        color_discrete_sequence=["#3182ce"]
    )
    
    fig_trend.update_layout(height=250)
    
    st.plotly_chart(fig_trend, use_container_width=True)

def render_recent_activity(api_client: APIClient):
    """Rend l'activité récente"""
    
    st.subheader("🕒 Activité Récente")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚗 Derniers Véhicules Ajoutés")
        render_recent_cars(api_client)
    
    with col2:
        st.markdown("#### 📋 Dernières Réservations")
        render_recent_reservations(api_client)

def render_recent_cars(api_client: APIClient):
    """Rend les dernières voitures ajoutées"""
    
    success, cars_data, _ = api_client.get_cars(size=5)
    
    if success and cars_data:
        # Trier par date de création (plus récent en premier)
        cars_sorted = sorted(
            cars_data, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )[:5]
        
        for car in cars_sorted:
            render_car_item(car)
    else:
        st.info("Aucune donnée disponible")

def render_recent_reservations(api_client: APIClient):
    """Rend les dernières réservations"""
    
    success, reservations_data, _ = api_client.get_reservations(size=5)
    
    if success and reservations_data:
        # Trier par date de création (plus récent en premier)
        reservations_sorted = sorted(
            reservations_data, 
            key=lambda x: x.get('created_at', ''), 
            reverse=True
        )[:5]
        
        for reservation in reservations_sorted:
            render_reservation_item(reservation)
    else:
        st.info("Aucune donnée disponible")

def render_car_item(car):
    """Rend un élément de voiture"""
    
    status_colors = {
        "disponible": "#38a169",
        "loue": "#d69e2e",
        "vendu": "#e53e3e"
    }
    
    status_color = status_colors.get(car.get('disponibilite', ''), "#718096")
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid {status_color};
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <div style="font-weight: bold; color: #2d3748;">
            {car.get('marque', '')} {car.get('modele', '')}
        </div>
        <div style="color: #718096; font-size: 0.9rem;">
            {car.get('couleur', '')} • {car.get('prix', 0):,.0f} €
        </div>
        <div style="
            display: inline-block;
            background-color: {status_color};
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-top: 0.5rem;
        ">
            {car.get('disponibilite', '').title()}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_reservation_item(reservation):
    """Rend un élément de réservation"""
    
    status_colors = {
        "en_attente": "#d69e2e",
        "confirmee": "#38a169",
        "annulee": "#e53e3e",
        "terminee": "#3182ce"
    }
    
    status_color = status_colors.get(reservation.get('statut', ''), "#718096")
    
    # Extraction des informations
    car_info = reservation.get('car', {})
    user_info = reservation.get('user', {})
    
    car_name = f"{car_info.get('marque', '')} {car_info.get('modele', '')}"
    user_name = f"{user_info.get('prenom', '')} {user_info.get('nom', '')}"
    
    st.markdown(f"""
    <div style="
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border-left: 4px solid {status_color};
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    ">
        <div style="font-weight: bold; color: #2d3748;">
            {car_name}
        </div>
        <div style="color: #718096; font-size: 0.9rem;">
            Client: {user_name}
        </div>
        <div style="
            display: inline-block;
            background-color: {status_color};
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            margin-top: 0.5rem;
        ">
            {reservation.get('statut', '').replace('_', ' ').title()}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_quick_actions():
    """Rend les actions rapides pour les vendeurs"""
    
    user_role = get_user_role()
    
    if user_role == "vendeur":
        st.subheader("⚡ Actions Rapides")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("➕ Ajouter Véhicule", use_container_width=True):
                st.session_state.current_page = "Véhicules"
                st.rerun()
        
        with col2:
            if st.button("📋 Voir Réservations", use_container_width=True):
                st.session_state.current_page = "Réservations"
                st.rerun()
        
        with col3:
            if st.button("🔄 Actualiser Données", use_container_width=True):
                from utils.session_state import clear_cache
                clear_cache()
                st.success("✅ Données actualisées")
                st.rerun()
        
        with col4:
            if st.button("📊 Rapport Complet", use_container_width=True):
                st.info("🚧 Fonctionnalité en développement")