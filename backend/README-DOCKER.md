# 🐳 Car Dealership - Guide Docker

Ce guide explique comment déployer et utiliser l'application Car Dealership avec Docker.

## 📋 Prérequis

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** pour cloner le projet
- **curl** pour les tests (optionnel)

### Vérification des prérequis

```bash
# Vérifier Docker
docker --version
docker-compose --version

# Vérifier que Docker est en cours d'exécution
docker info
```

## 🏗️ Architecture Docker

Le projet utilise une architecture multi-conteneurs :

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Base MySQL    │
│   (Futur)       │◄──►│   FastAPI       │◄──►│   + Scripts     │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 3306    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   phpMyAdmin    │    │   Redis Cache   │
                       │   Port: 8080    │    │   Port: 6379    │
                       └─────────────────┘    └─────────────────┘
```

## 🚀 Démarrage rapide

### 1. Cloner le projet

```bash
git clone <url-du-projet>
cd car-dealership
```

### 2. Lancer avec le script automatique

```bash
# Rendre le script exécutable
chmod +x scripts/docker-start.sh

# Démarrer tous les services
./scripts/docker-start.sh start
```

### 3. Vérifier le déploiement

```bash
# Validation automatique
python scripts/validate-docker.py

# Ou manuellement
curl http://localhost:8000/health
```

## 📦 Services disponibles

| Service | URL | Description |
|---------|-----|-------------|
| **API Backend** | http://localhost:8000 | API REST FastAPI |
| **Documentation** | http://localhost:8000/docs | Swagger UI |
| **phpMyAdmin** | http://localhost:8080 | Interface MySQL |
| **MySQL** | localhost:3306 | Base de données |
| **Redis** | localhost:6379 | Cache (optionnel) |

## 🔐 Comptes de test

Le système est livré avec des comptes de démonstration :

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| **Admin** | admin@cardealership.com | password123 |
| **Vendeur** | vendeur@test.com | password123 |
| **Client** | client@test.com | password123 |

## 📂 Structure des fichiers

```
car-dealership/
├── docker-compose.yml              # Configuration principale
├── docker-compose.override.yml     # Configuration développement
├── Dockerfile                      # Image backend
├── .dockerignore                   # Fichiers ignorés
├── requirements.txt                # Dépendances Python
├── scripts/
│   ├── docker-start.sh            # Script de démarrage
│   ├── validate-docker.py         # Script de validation
│   ├── 01-setup.sql               # Initialisation DB
│   └── 02-sample-data.sql         # Données de test
└── app/                           # Code source FastAPI
```

## 🛠️ Commandes utiles

### Gestion des services

```bash
# Démarrer tous les services
docker-compose up -d

# Arrêter tous les services
docker-compose down

# Redémarrer un service
docker-compose restart api

# Voir les logs
docker-compose logs -f api

# Voir le statut
docker-compose ps
```

### Accès aux conteneurs

```bash
# Shell dans le conteneur API
docker-compose exec api bash

# MySQL CLI
docker-compose exec mysql mysql -u car_user -p car_dealership

# Redis CLI
docker-compose exec redis redis-cli
```

### Gestion des données

```bash
# Sauvegarder la base de données
docker-compose exec mysql mysqldump -u car_user -p car_dealership > backup.sql

# Restaurer la base de données
docker-compose exec -T mysql mysql -u car_user -p car_dealership < backup.sql

# Réinitialiser les données
docker-compose down -v
docker-compose up -d
```

## 🔧 Configuration

### Variables d'environnement

Principales variables configurables dans `docker-compose.yml` :

```yaml
environment:
  DATABASE_URL: mysql+pymysql://car_user:car_password@mysql:3306/car_dealership
  SECRET_KEY: your-secret-key-here
  DEBUG: "true"
  CORS_ORIGINS: '["http://localhost:3000"]'
```

### Volumes persistants

- `mysql_data` : Données MySQL
- `redis_data` : Données Redis
- `api_logs` : Logs de l'API
- `api_uploads` : Fichiers uploadés

## 🧪 Tests et développement

### Mode développement

Le fichier `docker-compose.override.yml` active :
- Hot reload pour l'API
- Montage des sources en temps réel
- Logs détaillés
- Port debugger (5678)

### Exécuter les tests

```bash
# Tests automatiques
docker-compose --profile testing run test

# Tests manuels
python scripts/validate-docker.py
```

### Surveillance

```bash
# Logs en temps réel
docker-compose logs -f

# Métriques des conteneurs
docker stats

# Santé des services
docker-compose ps
```

## 🚨 Dépannage

### Problèmes courants

#### 1. Port déjà utilisé

```bash
# Vérifier les ports utilisés
netstat -tlnp | grep :8000

# Changer le port dans docker-compose.yml
ports:
  - "8001:8000"  # Utiliser 8001 au lieu de 8000
```

#### 2. Erreur de connexion MySQL

```bash
# Vérifier les logs MySQL
docker-compose logs mysql

# Réinitialiser MySQL
docker-compose down
docker volume rm car_dealership_mysql_data
docker-compose up -d
```

#### 3. API ne démarre pas

```bash
# Vérifier les logs
docker-compose logs api

# Reconstruire l'image
docker-compose build --no-cache api
docker-compose up -d
```

#### 4. Problèmes de permissions

```bash
# Fixer les permissions
sudo chown -R $USER:$USER .
chmod +x scripts/docker-start.sh
```

### Scripts de diagnostic

```bash
# Vérification complète
python scripts/validate-docker.py

# Santé des services
./scripts/docker-start.sh health

# Nettoyage complet
./scripts/docker-start.sh clean
```

## 🔄 Mise à jour

### Mettre à jour l'application

```bash
# Arrêter les services
docker-compose down

# Mettre à jour le code
git pull origin main

# Reconstruire et redémarrer
docker-compose build --no-cache
docker-compose up -d
```

### Sauvegarder avant mise à jour

```bash
# Sauvegarder la base
docker-compose exec mysql mysqldump -u car_user -p car_dealership > backup-$(date +%Y%m%d).sql

# Sauvegarder les volumes
docker run --rm -v car_dealership_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/volumes-backup.tar.gz /data
```

## 📊 Monitoring

### Métriques disponibles

```bash
# Utilisation des ressources
docker stats

# Espace disque des volumes
docker system df

# Santé des conteneurs
docker-compose ps --format table
```

### Logs centralisés

```bash
# Tous les logs
docker-compose logs -f

# Logs spécifiques
docker-compose logs -f api mysql
```

## 🔒 Sécurité

### Recommandations de production

1. **Changer les mots de passe par défaut**
2. **Utiliser HTTPS** avec reverse proxy
3. **Limiter les ports exposés**
4. **Utiliser des secrets Docker**
5. **Mettre à jour régulièrement**

### Variables sensibles

```bash
# Créer un fichier .env
cp .env.example .env

# Modifier les valeurs sensibles
SECRET_KEY=your-super-secret-key
MYSQL_ROOT_PASSWORD=strong-root-password
MYSQL_PASSWORD=strong-user-password
```

## 🆘 Support

### Ressources utiles

- **Documentation FastAPI** : https://fastapi.tiangolo.com/
- **Documentation Docker** : https://docs.docker.com/
- **Documentation MySQL** : https://dev.mysql.com/doc/

### Commandes d'urgence

```bash
# Arrêt d'urgence
docker-compose down --remove-orphans

# Nettoyage total
docker system prune -a --volumes

# Redémarrage complet
./scripts/docker-start.sh clean
./scripts/docker-start.sh start
```

---

## 🎯 Prochaines étapes

Une fois le setup Docker fonctionnel, vous pouvez :

1. **Développer le frontend** (React/Vue.js)
2. **Configurer Kubernetes** pour la production
3. **Mettre en place CI/CD**
4. **Ajouter monitoring avancé**
5. **Implémenter les notifications**

---

*Ce guide est maintenu et mis à jour régulièrement. N'hésitez pas à contribuer !*