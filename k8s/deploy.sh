#!/bin/bash

echo "🚗 Déploiement Car Dealership sur Kubernetes"

# Générer les certificats TLS
echo "🔐 Génération des certificats TLS..."
chmod +x k8s/generate-tls.sh
./k8s/generate-tls.sh

# Vérifier kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl n'est pas installé"
    exit 1
fi

# Appliquer avec Kustomize
echo "📦 Déploiement avec Kustomize..."
kubectl apply -k k8s/

# Attendre les déploiements
echo "⏳ Attente des déploiements..."
kubectl wait --for=condition=Available deployment --all -n car-dealership --timeout=600s

echo "✅ Déploiement terminé !"
echo ""
echo "🔗 Accès HTTPS (ajoutez à /etc/hosts) :"
echo "127.0.0.1 car-dealership.local"
echo "127.0.0.1 api.car-dealership.local" 
echo "127.0.0.1 admin.car-dealership.local"
echo ""
echo "🌐 URLs :"
echo "Frontend: https://car-dealership.local"
echo "API: https://api.car-dealership.local"
echo "phpMyAdmin: https://admin.car-dealership.local"


# #!/bin/bash

# echo "🚗 Déploiement Car Dealership sur Kubernetes"

# # Vérifier kubectl
# if ! command -v kubectl &> /dev/null; then
#     echo "❌ kubectl n'est pas installé"
#     exit 1
# fi

# # Créer le namespace d'abord
# echo "📁 Création du namespace..."
# kubectl apply -f namespace.yaml

# # Attendre que le namespace soit créé
# kubectl wait --for=condition=Ready namespace/car-dealership --timeout=30s

# # Déployer les secrets et configmaps
# echo "🔐 Déploiement des secrets et configurations..."
# kubectl apply -f secrets.yaml
# kubectl apply -f configmaps.yaml

# # Déployer le stockage
# echo "💾 Déploiement du stockage persistant..."
# kubectl apply -f storage/

# # Déployer MySQL et Redis
# echo "🗄️ Déploiement des bases de données..."
# kubectl apply -f mysql/
# kubectl apply -f redis/

# # Attendre que MySQL et Redis soient prêts
# echo "⏳ Attente des bases de données..."
# kubectl wait --for=condition=Ready pod -l app=mysql -n car-dealership --timeout=300s
# kubectl wait --for=condition=Ready pod -l app=redis -n car-dealership --timeout=300s

# # Déployer l'API
# echo "🚀 Déploiement de l'API..."
# kubectl apply -f api/

# # Attendre que l'API soit prête
# echo "⏳ Attente de l'API..."
# kubectl wait --for=condition=Ready pod -l app=api -n car-dealership --timeout=300s

# # Déployer le frontend
# echo "🖥️ Déploiement du frontend..."
# kubectl apply -f frontend/

# # Déployer phpMyAdmin
# echo "🔧 Déploiement de phpMyAdmin..."
# kubectl apply -f phpmyadmin/

# # Déployer l'ingress
# echo "🌐 Déploiement de l'ingress..."
# kubectl apply -f ingress/

# echo "✅ Déploiement terminé !"
# echo ""
# echo "🔗 Accès aux services :"
# echo "Frontend: http://localhost:30851"
# echo "phpMyAdmin: http://localhost:30808"
# echo ""
# echo "📋 Commandes utiles :"
# echo "kubectl get pods -n car-dealership"
# echo "kubectl get services -n car-dealership"
# echo "kubectl logs -f deployment/api -n car-dealership"