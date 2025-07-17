-- =================================================================
-- DONNÉES DE DÉMONSTRATION POUR DOCKER
-- =================================================================

USE car_dealership;

-- Vérifier si des données existent déjà
SET @user_count = (SELECT COUNT(*) FROM users);

-- Insérer des données seulement si la table est vide
-- Mot de passe : password123 (hashé avec bcrypt)
INSERT INTO users (email, password, nom, prenom, telephone, role, is_active, created_at)
SELECT * FROM (
    SELECT 
        'admin@cardealership.com' as email,
        '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M' as password,
        'Administrator' as nom,
        'Super' as prenom,
        '0123456789' as telephone,
        'vendeur' as role,
        1 as is_active,
        NOW() as created_at
    UNION ALL
    SELECT 
        'vendeur@test.com',
        '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M',
        'Durand',
        'Jean',
        '0123456789',
        'vendeur',
        1,
        NOW()
    UNION ALL
    SELECT 
        'client@test.com',
        '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M',
        'Martin',
        'Marie',
        '0987654321',
        'client',
        1,
        NOW()
    UNION ALL
    SELECT 
        'client2@test.com',
        '$2b$12$LQv3c1yqBwcVbKVUGlXbQ.KfJJVzKKXqEfwJ4MzJ4M0J4M0J4M0J4M',
        'Dubois',
        'Pierre',
        '0147258369',
        'client',
        1,
        NOW()
) as tmp
WHERE @user_count = 0;

-- Insérer des voitures de démonstration
INSERT INTO cars (marque, modele, couleur, motorisation, prix, disponibilite, description, kilometrage, annee, is_active, created_at)
SELECT * FROM (
    SELECT 
        'Toyota' as marque,
        'Corolla' as modele,
        'blanc' as couleur,
        'Essence 1.2L' as motorisation,
        22000.00 as prix,
        'disponible' as disponibilite,
        'Berline compacte fiable et économique' as description,
        15000 as kilometrage,
        2021 as annee,
        1 as is_active,
        NOW() as created_at
    UNION ALL
    SELECT 'BMW', 'Série 3', 'noir', 'Diesel 2.0L', 35000.00, 'disponible', 'Berline premium avec finitions haut de gamme', 8000, 2022, 1, NOW()
    UNION ALL
    SELECT 'Renault', 'Clio', 'rouge', 'Essence 1.0L', 18000.00, 'disponible', 'Citadine pratique et moderne', 25000, 2020, 1, NOW()
    UNION ALL
    SELECT 'Mercedes', 'Classe A', 'gris', 'Essence 1.6L', 28000.00, 'loue', 'Compacte premium avec technologie avancée', 12000, 2021, 1, NOW()
    UNION ALL
    SELECT 'Volkswagen', 'Golf', 'bleu', 'Diesel 1.6L', 24000.00, 'vendu', 'Compacte polyvalente et robuste', 18000, 2020, 1, NOW()
    UNION ALL
    SELECT 'Audi', 'A4', 'blanc', 'Diesel 2.0L', 42000.00, 'disponible', 'Berline executive élégante', 5000, 2023, 1, NOW()
    UNION ALL
    SELECT 'Peugeot', '308', 'gris', 'Essence 1.2L', 21000.00, 'disponible', 'Compacte française moderne', 30000, 2019, 1, NOW()
    UNION ALL
    SELECT 'Ford', 'Focus', 'noir', 'Essence 1.0L', 19000.00, 'disponible', 'Compacte dynamique et efficace', 22000, 2020, 1, NOW()
    UNION ALL
    SELECT 'Citroen', 'C3', 'jaune', 'Essence 1.2L', 16000.00, 'disponible', 'Citadine colorée et moderne', 35000, 2019, 1, NOW()
    UNION ALL
    SELECT 'Opel', 'Corsa', 'blanc', 'Essence 1.4L', 17000.00, 'disponible', 'Petite voiture économique', 28000, 2020, 1, NOW()
    UNION ALL
    SELECT 'Nissan', 'Micra', 'rouge', 'Essence 1.0L', 15000.00, 'disponible', 'Citadine compacte et maniable', 40000, 2018, 1, NOW()
    UNION ALL
    SELECT 'Hyundai', 'i30', 'bleu', 'Essence 1.6L', 20000.00, 'disponible', 'Compacte coréenne fiable', 20000, 2021, 1, NOW()
) as tmp
WHERE @user_count = 0;

-- Insérer quelques réservations de test
INSERT INTO reservations (car_id, user_id, type_transaction, date_debut, date_fin, prix_final, statut, notes, created_at)
SELECT * FROM (
    SELECT 
        1 as car_id,
        3 as user_id,
        'location' as type_transaction,
        '2024-02-15 10:00:00' as date_debut,
        '2024-02-20 10:00:00' as date_fin,
        150.00 as prix_final,
        'confirmee' as statut,
        'Location pour voyage professionnel' as notes,
        NOW() as created_at
    UNION ALL
    SELECT 2, 3, 'vente', '2024-02-10 14:00:00', NULL, 35000.00, 'en_attente', 'Intéressé par un financement', NOW()
    UNION ALL
    SELECT 3, 4, 'location', '2024-02-05 09:00:00', '2024-02-12 09:00:00', 120.00, 'terminee', 'Location week-end réussie', NOW()
    UNION ALL
    SELECT 6, 3, 'vente', '2024-02-01 15:30:00', NULL, 42000.00, 'en_attente', 'Demande de reprise en plus', NOW()
    UNION ALL
    SELECT 7, 4, 'location', '2024-02-25 08:00:00', '2024-03-01 08:00:00', 180.00, 'confirmee', 'Location longue durée', NOW()
) as tmp
WHERE @user_count = 0;

-- Afficher un résumé des données insérées
SELECT 
    (SELECT COUNT(*) FROM users) as users_count,
    (SELECT COUNT(*) FROM cars) as cars_count,
    (SELECT COUNT(*) FROM reservations) as reservations_count,
    'Données de démonstration chargées avec succès !' as message;