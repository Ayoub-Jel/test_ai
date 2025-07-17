# Dockerfile (à la racine du backend)

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="car-dealership-team"
LABEL description="Car Dealership API - FastAPI Backend"
LABEL version="1.0.0"

# Optimisations d’environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copie du code source
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY run.py .

# Création des dossiers nécessaires
RUN mkdir -p /app/logs /app/uploads && \
    chown -R appuser:appuser /app

USER appuser

# Port exposé
EXPOSE 8000

# Healthcheck (optionnel car présent dans docker-compose)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Entrée du programme
ENTRYPOINT ["python", "run.py"]



