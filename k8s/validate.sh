#!/bin/bash

echo "🔍 Validation du déploiement Kubernetes"

# Vérifier les pods
echo "📦 État des pods :"
kubectl get pods -n car-dealership

echo ""
echo "🔗 État des services :"
kubectl get services -n car-dealership

echo ""
echo "💾 État des PVC :"
kubectl get pvc -n car-dealership

echo ""
echo "🌐 État de l'ingress :"
kubectl get ingress -n car-dealership

# Test de connectivité
echo ""
echo "🧪 Test de connectivité..."

# Test API
echo "Testing API..."
kubectl port-forward service/api-service 8080:8000 -n car-dealership &
API_PF_PID=$!
sleep 5
curl -f http://localhost:8080/health && echo "✅ API OK" || echo "❌ API KO"
kill $API_PF_PID

# Test Frontend
echo "Testing Frontend..."
kubectl port-forward service/frontend-service 8081:8501 -n car-dealership &
FRONT_PF_PID=$!
sleep 5
curl -f http://localhost:8081/_stcore/health && echo "✅ Frontend OK" || echo "❌ Frontend KO"
kill $FRONT_PF_PID

echo ""
echo "🎯 Accès direct aux services :"
echo "Frontend: kubectl port-forward service/frontend-service 8501:8501 -n car-dealership"
echo "API: kubectl port-forward service/api-service 8000:8000 -n car-dealership"
echo "phpMyAdmin: kubectl port-forward service/phpmyadmin-service 8080:80 -n car-dealership"