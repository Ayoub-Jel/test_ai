# run.py
import uvicorn
import os
import sys
from pathlib import Path

# Ajouter le répertoire racine au path Python
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from app.configs.settings import settings

def main():
    """
    Point d'entrée principal pour lancer l'application
    """
    # Configuration pour le développement
    config = {
        "app": "app.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "reload": settings.DEBUG,
        "log_level": "info" if settings.DEBUG else "warning",
        "access_log": settings.DEBUG,
    }
    
    # Configuration supplémentaire pour la production
    if not settings.DEBUG:
        config.update({
            "workers": 4,
            "loop": "uvloop",
            "http": "httptools"
        })
    
    print(f"🚗 Démarrage de {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"🌐 Mode: {'Développement' if settings.DEBUG else 'Production'}")
    print(f"📡 Serveur: http://{config['host']}:{config['port']}")
    print(f"📚 Documentation: http://{config['host']}:{config['port']}/docs")
    print("-" * 50)
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du serveur...")
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()