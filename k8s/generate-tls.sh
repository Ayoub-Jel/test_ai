#!/bin/bash

echo "🔐 Génération des certificats TLS auto-signés"

# Créer le dossier pour les certificats
mkdir -p k8s/certs

# Générer la clé privée
openssl genrsa -out k8s/certs/tls.key 2048

# Créer le fichier de configuration pour le certificat
cat > k8s/certs/cert.conf << EOF
[req]
default_bits = 2048
prompt = no
default_md = sha256
distinguished_name = dn
req_extensions = v3_req

[dn]
CN = car-dealership.local
O = Car Dealership
OU = IT Department
L = Paris
ST = Ile-de-France
C = FR
emailAddress = admin@car-dealership.local

[v3_req]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = car-dealership.local
DNS.2 = api.car-dealership.local
DNS.3 = admin.car-dealership.local
DNS.4 = *.car-dealership.local
DNS.5 = localhost
IP.1 = 127.0.0.1
IP.2 = 192.168.1.100
EOF

# Générer le certificat
openssl req -new -x509 -key k8s/certs/tls.key -out k8s/certs/tls.crt -days 365 -config k8s/certs/cert.conf -extensions v3_req

# Encoder en base64 pour Kubernetes
echo "📝 Encodage des certificats en base64..."
TLS_CRT=$(base64 -w 0 k8s/certs/tls.crt)
TLS_KEY=$(base64 -w 0 k8s/certs/tls.key)

# Créer le fichier secret Kubernetes
cat > k8s/ingress/tls-secret.yaml << EOF
apiVersion: v1
kind: Secret
metadata:
  name: tls-car-dealership
  namespace: car-dealership
  labels:
    app: car-dealership
    component: tls
type: kubernetes.io/tls
data:
  tls.crt: ${TLS_CRT}
  tls.key: ${TLS_KEY}
EOF

echo "✅ Certificats générés avec succès !"
echo "📄 Fichiers créés :"
echo "  - k8s/certs/tls.crt"
echo "  - k8s/certs/tls.key" 
echo "  - k8s/ingress/tls-secret.yaml"
echo ""
echo "🔧 Pour utiliser HTTPS localement, ajoutez à votre /etc/hosts :"
echo "127.0.0.1 car-dealership.local"
echo "127.0.0.1 api.car-dealership.local"
echo "127.0.0.1 admin.car-dealership.local"