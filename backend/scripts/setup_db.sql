-- =================================================================
-- SETUP BASE DE DONNÉES - CAR DEALERSHIP
-- =================================================================

-- Supprimer et recréer la base (attention en production !)
DROP DATABASE IF EXISTS car_dealership;
CREATE DATABASE car_dealership 
    CHARACTER SET utf8mb4 
    COLLATE utf8mb4_unicode_ci;

-- Créer l'utilisateur dédié
DROP USER IF EXISTS 'car_user'@'localhost';
CREATE USER 'car_user'@'localhost' IDENTIFIED BY 'car_password';

-- Accorder tous les privilèges
GRANT ALL PRIVILEGES ON car_dealership.* TO 'car_user'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, DROP, INDEX, ALTER 
ON car_dealership.* TO 'car_user'@'localhost';

-- Appliquer les changements
FLUSH PRIVILEGES;

-- Utiliser la base
USE car_dealership;

-- Vérifier la connexion
SELECT 'Base de données configurée avec succès !' as message;