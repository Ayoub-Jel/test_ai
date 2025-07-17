# streamlit_app/Dockerfile

FROM python:3.11-slim

# Métadonnées
LABEL maintainer="car-dealership-team"
LABEL description="Car Dealership Frontend - Streamlit Application"
LABEL version="1.0.0"

# Optimisations d'environnement
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_HEADLESS=true

# Répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Création d'un utilisateur non-root
RUN groupadd -r streamlituser && useradd -r -g streamlituser streamlituser

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copie du code source
COPY . .

# Création des dossiers nécessaires et permissions
RUN mkdir -p /app/.streamlit /app/assets && \
    chown -R streamlituser:streamlituser /app

# Copier la configuration Streamlit
COPY config.toml /app/.streamlit/config.toml

# Switch to non-root user
USER streamlituser

# Port d'exposition
EXPOSE 8501

# Health check pour vérifier que Streamlit fonctionne
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Point d'entrée
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]