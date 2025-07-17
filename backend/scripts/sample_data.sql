-- =================================================================
-- DONNÉES DE DÉMONSTRATION
-- =================================================================

USE car_dealership;

-- Insérer des utilisateurs de test
INSERT INTO users (email, password, nom, prenom, telephone, role, is_active, created_at) VALUES
('admin@cardealership.com', '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M', 'Admin', 'Super', '0123456789', 'vendeur', 1, NOW()),
('vendeur@test.com', '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M', 'Durand', 'Jean', '0123456789', 'vendeur', 1, NOW()),
('client@test.com', '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M', 'Martin', 'Marie', '0987654321', 'client', 1, NOW());

-- Insérer des voitures de démonstration
INSERT INTO cars (marque, modele, couleur, motorisation, prix, disponibilite, description, kilometrage, annee, created_at) VALUES
('Toyota', 'Corolla', 'blanc', 'Essence 1.2L', 22000.00, 'disponible', 'Berline compacte fiable et économique', 15000, 2021, NOW()),
('BMW', 'Série 3', 'noir', 'Diesel 2.0L', 35000.00, 'disponible', 'Berline premium avec finitions haut de gamme', 8000, 2022, NOW()),
('Renault', 'Clio', 'rouge', 'Essence 1.0L', 18000.00, 'disponible', 'Citadine pratique et moderne', 25000, 2020, NOW()),
('Mercedes', 'Classe A', 'gris', 'Essence 1.6L', 28000.00, 'loue', 'Compacte premium avec technologie avancée', 12000, 2021, NOW()),
('Volkswagen', 'Golf', 'bleu', 'Diesel 1.6L', 24000.00, 'vendu', 'Compacte polyvalente et robuste', 18000, 2020, NOW()),
('Audi', 'A4', 'blanc', 'Diesel 2.0L', 42000.00, 'disponible', 'Berline executive élégante', 5000, 2023, NOW()),
('Peugeot', '308', 'gris', 'Essence 1.2L', 21000.00, 'disponible', 'Compacte française moderne', 30000, 2019, NOW()),
('Ford', 'Focus', 'noir', 'Essence 1.0L', 19000.00, 'disponible', 'Compacte dynamique et efficace', 22000, 2020, NOW());

-- Insérer quelques réservations de test
INSERT INTO reservations (car_id, user_id, type_transaction, date_debut, date_fin, prix_final, statut, notes, created_at) VALUES
(1, 3, 'location', '2024-02-15 10:00:00', '2024-02-20 10:00:00', 150.00, 'confirmee', 'Location pour voyage professionnel', NOW()),
(2, 3, 'vente', '2024-02-10 14:00:00', NULL, 35000.00, 'en_attente', 'Intéressé par un financement', NOW()),
(3, 3, 'location', '2024-02-05 09:00:00', '2024-02-12 09:00:00', 120.00, 'terminee', 'Location week-end réussie', NOW());