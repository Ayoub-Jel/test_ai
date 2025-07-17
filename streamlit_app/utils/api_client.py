# utils/api_client.py
"""
Client API pour communiquer avec le backend FastAPI
"""

import streamlit as st
import requests
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import json

class APIClient:
    """Client pour interagir avec l'API FastAPI"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 30
    
    def _get_headers(self) -> Dict[str, str]:
        """Retourne les headers avec le token d'authentification"""
        headers = {"Content-Type": "application/json"}
        
        token = st.session_state.get("token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Tuple[bool, Any, str]:
        """
        Traite la réponse de l'API
        
        Returns:
            Tuple[bool, Any, str]: (success, data, message)
        """
        try:
            if response.status_code in [200, 201]:
                data = response.json() if response.content else {}
                return True, data, "Succès"
            
            elif response.status_code == 401:
                return False, None, "Non authentifié - Veuillez vous reconnecter"
            
            elif response.status_code == 403:
                return False, None, "Accès refusé"
            
            elif response.status_code == 404:
                return False, None, "Ressource non trouvée"
            
            elif response.status_code == 422:
                error_data = response.json() if response.content else {}
                detail = error_data.get("detail", "Erreur de validation")
                return False, None, f"Erreur de validation: {detail}"
            
            else:
                error_data = response.json() if response.content else {}
                detail = error_data.get("detail", f"Erreur HTTP {response.status_code}")
                return False, None, detail
                
        except json.JSONDecodeError:
            return False, None, f"Erreur de décodage JSON (Status: {response.status_code})"
        except Exception as e:
            return False, None, f"Erreur inattendue: {str(e)}"
    
    # ========================================
    # GESTION DES VOITURES
    # ========================================
    
    def get_cars(self, page: int = 1, size: int = 50, filters: Dict = None) -> Tuple[bool, List[Dict], str]:
        """Récupère la liste des voitures"""
        try:
            params = {"page": page, "size": size}
            if filters:
                params.update(filters)
            
            response = requests.get(
                f"{self.base_url}/api/cars",
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )
            
            success, data, message = self._handle_response(response)
            if success:
                # Gérer le format de réponse (peut être paginé ou direct)
                cars = data.get("items", data) if isinstance(data, dict) else data
                return True, cars, message
            
            return False, [], message
            
        except requests.exceptions.ConnectionError:
            return False, [], "Impossible de se connecter au serveur API"
        except Exception as e:
            return False, [], f"Erreur: {str(e)}"
    
    def get_car_by_id(self, car_id: int) -> Tuple[bool, Optional[Dict], str]:
        """Récupère une voiture par son ID"""
        try:
            response = requests.get(
                f"{self.base_url}/api/cars/{car_id}",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def create_car(self, car_data: Dict) -> Tuple[bool, Optional[Dict], str]:
        """Crée une nouvelle voiture"""
        try:
            response = requests.post(
                f"{self.base_url}/api/cars",
                headers=self._get_headers(),
                json=car_data,
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def update_car(self, car_id: int, car_data: Dict) -> Tuple[bool, Optional[Dict], str]:
        """Met à jour une voiture"""
        try:
            response = requests.put(
                f"{self.base_url}/api/cars/{car_id}",
                headers=self._get_headers(),
                json=car_data,
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def delete_car(self, car_id: int) -> Tuple[bool, Optional[Dict], str]:
        """Supprime une voiture"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/cars/{car_id}",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def update_car_availability(self, car_id: int, availability: str) -> Tuple[bool, Optional[Dict], str]:
        """Met à jour la disponibilité d'une voiture"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/cars/{car_id}/availability",
                headers=self._get_headers(),
                params={"availability": availability},
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    # ========================================
    # GESTION DES RÉSERVATIONS
    # ========================================
    
    def get_reservations(self, page: int = 1, size: int = 50, filters: Dict = None) -> Tuple[bool, List[Dict], str]:
        """Récupère la liste des réservations"""
        try:
            params = {"page": page, "size": size}
            if filters:
                params.update(filters)
            
            response = requests.get(
                f"{self.base_url}/api/reservations",
                headers=self._get_headers(),
                params=params,
                timeout=self.timeout
            )
            
            success, data, message = self._handle_response(response)
            if success:
                reservations = data.get("items", data) if isinstance(data, dict) else data
                return True, reservations, message
            
            return False, [], message
            
        except Exception as e:
            return False, [], f"Erreur: {str(e)}"
    
    def create_reservation(self, reservation_data: Dict) -> Tuple[bool, Optional[Dict], str]:
        """Crée une nouvelle réservation"""
        try:
            response = requests.post(
                f"{self.base_url}/api/reservations",
                headers=self._get_headers(),
                json=reservation_data,
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def update_reservation_status(self, reservation_id: int, status: str) -> Tuple[bool, Optional[Dict], str]:
        """Met à jour le statut d'une réservation"""
        try:
            response = requests.patch(
                f"{self.base_url}/api/reservations/{reservation_id}/status",
                headers=self._get_headers(),
                json={"statut": status},
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def cancel_reservation(self, reservation_id: int) -> Tuple[bool, Optional[Dict], str]:
        """Annule une réservation"""
        try:
            response = requests.post(
                f"{self.base_url}/api/reservations/{reservation_id}/cancel",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    # ========================================
    # STATISTIQUES ET DASHBOARD
    # ========================================
    
    def get_dashboard_stats(self) -> Tuple[bool, Optional[Dict], str]:
        """Récupère les statistiques du dashboard"""
        try:
            response = requests.get(
                f"{self.base_url}/api/reservations/dashboard/stats",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def get_car_statistics(self) -> Tuple[bool, Optional[Dict], str]:
        """Récupère les statistiques des voitures"""
        try:
            response = requests.get(
                f"{self.base_url}/api/cars/statistics",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            return self._handle_response(response)
            
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    # ========================================
    # UTILITAIRES
    # ========================================
    
    def test_connection(self) -> Tuple[bool, str]:
        """Teste la connexion avec l'API"""
        try:
            response = requests.get(
                f"{self.base_url}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                return True, "✅ Connexion API réussie"
            else:
                return False, f"❌ API répond avec le code {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "❌ Impossible de se connecter au serveur API"
        except Exception as e:
            return False, f"❌ Erreur de connexion: {str(e)}"
    
    def to_dataframe(self, data: List[Dict], columns: List[str] = None) -> pd.DataFrame:
        """Convertit les données en DataFrame pandas"""
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        if columns:
            # Garder seulement les colonnes spécifiées qui existent
            existing_columns = [col for col in columns if col in df.columns]
            df = df[existing_columns]
        
        return df
    
    def format_car_data(self, cars: List[Dict]) -> pd.DataFrame:
        """Formate les données de voitures pour l'affichage"""
        if not cars:
            return pd.DataFrame()
        
        df = pd.DataFrame(cars)
        
        # Colonnes à afficher
        display_columns = [
            'id', 'marque', 'modele', 'couleur', 'annee', 
            'prix', 'disponibilite', 'created_at'
        ]
        
        existing_columns = [col for col in display_columns if col in df.columns]
        df = df[existing_columns]
        
        # Formatage des colonnes
        if 'prix' in df.columns:
            df['prix'] = df['prix'].apply(lambda x: f"{x:,.0f} €" if pd.notnull(x) else "")
        
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d/%m/%Y')
        
        # Renommage des colonnes
        column_rename = {
            'id': 'ID',
            'marque': 'Marque',
            'modele': 'Modèle',
            'couleur': 'Couleur',
            'annee': 'Année',
            'prix': 'Prix',
            'disponibilite': 'Statut',
            'created_at': 'Ajouté le'
        }
        
        df = df.rename(columns=column_rename)
        
        return df
    
    def format_reservation_data(self, reservations: List[Dict]) -> pd.DataFrame:
        """Formate les données de réservations pour l'affichage"""
        if not reservations:
            return pd.DataFrame()
        
        df = pd.DataFrame(reservations)
        
        # Extraction des informations imbriquées
        if 'car' in df.columns:
            df['car_info'] = df['car'].apply(
                lambda x: f"{x.get('marque', '')} {x.get('modele', '')}" 
                if isinstance(x, dict) else ""
            )
        
        if 'user' in df.columns:
            df['user_info'] = df['user'].apply(
                lambda x: f"{x.get('prenom', '')} {x.get('nom', '')}" 
                if isinstance(x, dict) else ""
            )
        
        # Colonnes à afficher
        display_columns = [
            'id', 'car_info', 'user_info', 'type_transaction', 
            'statut', 'date_debut', 'prix_final', 'created_at'
        ]
        
        existing_columns = [col for col in display_columns if col in df.columns]
        df = df[existing_columns]
        
        # Formatage des dates
        date_columns = ['date_debut', 'created_at']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%d/%m/%Y')
        
        # Formatage du prix
        if 'prix_final' in df.columns:
            df['prix_final'] = df['prix_final'].apply(
                lambda x: f"{x:,.0f} €" if pd.notnull(x) else ""
            )
        
        # Renommage des colonnes
        column_rename = {
            'id': 'ID',
            'car_info': 'Véhicule',
            'user_info': 'Client',
            'type_transaction': 'Type',
            'statut': 'Statut',
            'date_debut': 'Date début',
            'prix_final': 'Prix final',
            'created_at': 'Créé le'
        }
        
        df = df.rename(columns=column_rename)
        
        return df