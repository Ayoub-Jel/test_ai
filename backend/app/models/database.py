# app/models/database.py
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from configs.database import Base


class User(Base):
    """
    Modèle pour les utilisateurs (clients et vendeurs)
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    telephone = Column(String(20), nullable=False)
    role = Column(String(20), nullable=False)  # 'client' ou 'vendeur'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    reservations = relationship("Reservation", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class Car(Base):
    """
    Modèle pour les voitures
    """
    __tablename__ = "cars"
    
    id = Column(Integer, primary_key=True, index=True)
    marque = Column(String(100), nullable=False, index=True)
    modele = Column(String(100), nullable=False, index=True)
    couleur = Column(String(50), nullable=False)
    motorisation = Column(String(100), nullable=False)
    prix = Column(Float, nullable=False, index=True)
    disponibilite = Column(String(20), nullable=False, default="disponible", index=True)  # 'disponible', 'loue', 'vendu'
    description = Column(Text, nullable=True)
    kilometrage = Column(Integer, nullable=True)
    annee = Column(Integer, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    reservations = relationship("Reservation", back_populates="car", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Car(id={self.id}, marque='{self.marque}', modele='{self.modele}', prix={self.prix})>"


class Reservation(Base):
    """
    Modèle pour les réservations
    """
    __tablename__ = "reservations"
    
    id = Column(Integer, primary_key=True, index=True)
    car_id = Column(Integer, ForeignKey("cars.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type_transaction = Column(String(20), nullable=False)  # 'vente' ou 'location'
    date_debut = Column(DateTime, nullable=False)
    date_fin = Column(DateTime, nullable=True)  # Null pour les ventes
    prix_final = Column(Float, nullable=False)
    statut = Column(String(20), nullable=False, default="en_attente", index=True)  # 'en_attente', 'confirmee', 'annulee', 'terminee'
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    car = relationship("Car", back_populates="reservations")
    user = relationship("User", back_populates="reservations")
    
    def __repr__(self):
        return f"<Reservation(id={self.id}, car_id={self.car_id}, user_id={self.user_id}, statut='{self.statut}')>"


class AuditLog(Base):
    """
    Modèle pour l'audit des actions (optionnel)
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # 'CREATE', 'UPDATE', 'DELETE'
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    old_values = Column(Text, nullable=True)  # JSON des anciennes valeurs
    new_values = Column(Text, nullable=True)  # JSON des nouvelles valeurs
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    user = relationship("User")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', table='{self.table_name}')>"