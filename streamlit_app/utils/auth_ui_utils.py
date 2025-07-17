# utils/auth.py
"""
Module de gestion d'authentification pour Streamlit
"""

import streamlit as st
import requests
import json
from typing import Tuple, Dict, Optional

class AuthManager:
    """Gestionnaire d'authentification"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.login_endpoint = f"{api_base_url}/api/auth/login"
        self.me_endpoint = f"{api_base_url}/api/auth/me"
    
    def login(self, email: str, password: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Authentifie un utilisateur
        
        Returns:
            Tuple[bool, Optional[Dict], str]: (success, user_data, message)
        """
        try:
            # Données de connexion
            login_data = {
                "email": email,
                "password": password
            }
            
            # Requête de connexion
            response = requests.post(
                self.login_endpoint,
                json=login_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_data = {
                    "access_token": data.get("access_token"),
                    "token_type": data.get("token_type", "bearer"),
                    "user": data.get("user", {})
                }
                
                # Sauvegarder dans le session state
                st.session_state.token = user_data["access_token"]
                st.session_state.user = user_data["user"]
                
                return True, user_data, "Connexion réussie"
            
            elif response.status_code == 401:
                return False, None, "Email ou mot de passe incorrect"
            
            elif response.status_code == 422:
                return False, None, "Données de connexion invalides"
            
            else:
                return False, None, f"Erreur serveur ({response.status_code})"
                
        except requests.exceptions.ConnectionError:
            return False, None, "Impossible de se connecter au serveur API"
        
        except requests.exceptions.Timeout:
            return False, None, "Timeout - Le serveur ne répond pas"
        
        except Exception as e:
            return False, None, f"Erreur inattendue: {str(e)}"
    
    def get_current_user(self, token: str) -> Tuple[bool, Optional[Dict], str]:
        """
        Récupère les informations de l'utilisateur actuel
        
        Args:
            token: Token d'authentification
            
        Returns:
            Tuple[bool, Optional[Dict], str]: (success, user_data, message)
        """
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                self.me_endpoint,
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, user_data, "Utilisateur récupéré"
            
            elif response.status_code == 401:
                return False, None, "Token expiré ou invalide"
            
            else:
                return False, None, f"Erreur serveur ({response.status_code})"
                
        except Exception as e:
            return False, None, f"Erreur: {str(e)}"
    
    def logout(self):
        """Déconnecte l'utilisateur"""
        # Nettoyer le session state
        keys_to_remove = ["authenticated", "token", "user"]
        for key in keys_to_remove:
            if key in st.session_state:
                del st.session_state[key]
    
    def is_authenticated(self) -> bool:
        """Vérifie si l'utilisateur est authentifié"""
        return (
            st.session_state.get("authenticated", False) and
            st.session_state.get("token") is not None
        )
    
    def get_user_role(self) -> Optional[str]:
        """Retourne le rôle de l'utilisateur actuel"""
        user = st.session_state.get("user", {})
        return user.get("role")
    
    def is_vendeur(self) -> bool:
        """Vérifie si l'utilisateur est un vendeur"""
        return self.get_user_role() == "vendeur"
    
    def is_client(self) -> bool:
        """Vérifie si l'utilisateur est un client"""
        return self.get_user_role() == "client"
    
    def get_user_name(self) -> str:
        """Retourne le nom complet de l'utilisateur"""
        user = st.session_state.get("user", {})
        prenom = user.get("prenom", "")
        nom = user.get("nom", "")
        return f"{prenom} {nom}".strip() or "Utilisateur"
    
    def get_user_initials(self) -> str:
        """Retourne les initiales de l'utilisateur"""
        user = st.session_state.get("user", {})
        prenom = user.get("prenom", "")
        nom = user.get("nom", "")
        
        initials = ""
        if prenom:
            initials += prenom[0].upper()
        if nom:
            initials += nom[0].upper()
        
        return initials or "U"
    
    def check_permission(self, required_role: str = None) -> bool:
        """
        Vérifie les permissions d'accès
        
        Args:
            required_role: Rôle requis (vendeur, client)
            
        Returns:
            bool: True si l'accès est autorisé
        """
        if not self.is_authenticated():
            return False
        
        if required_role is None:
            return True
        
        current_role = self.get_user_role()
        
        if required_role == "vendeur":
            return current_role == "vendeur"
        elif required_role == "client":
            return current_role in ["client", "vendeur"]  # Vendeur peut voir vue client
        
        return False
    
    def require_auth(self):
        """Décorateur pour exiger une authentification"""
        if not self.is_authenticated():
            st.error("🔒 Veuillez vous connecter pour accéder à cette page")
            st.stop()
    
    def require_role(self, role: str):
        """Décorateur pour exiger un rôle spécifique"""
        self.require_auth()
        
        if not self.check_permission(role):
            st.error(f"🚫 Accès refusé. Rôle '{role}' requis.")
            st.stop()