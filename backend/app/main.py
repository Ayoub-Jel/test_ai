# app/main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import time
import logging
from contextlib import asynccontextmanager

from routers import auth_router, cars_router
from configs.settings import settings
from configs.database import create_tables
from routers import reservations_router

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Gestionnaire de cycle de vie de l'application
#     """
#     # Startup
#     logger.info("Démarrage de l'application...")
#     try:
#         logger.info("Test de connexion à la base de données...")
        
#         # Test de connexion basique avant create_tables
#         from app.configs.database import engine
#         from sqlalchemy import text
        
#         with engine.connect() as connection:
#             result = connection.execute(text("SELECT 1"))
#             logger.info("✅ Connexion à la base de données réussie")
        
#         # Créer les tables de base de données
#         logger.info("Création des tables...")
#         create_tables()
#         logger.info("✅ Tables de base de données créées/vérifiées avec succès")
        
#     except Exception as e:
#         logger.error(f"❌ Erreur lors du démarrage: {e}")
#         logger.error(f"Type d'erreur: {type(e)}")
#         import traceback
#         logger.error(f"Traceback: {traceback.format_exc()}")
        
#         # NE PAS faire crash l'app, juste logger l'erreur
#         logger.warning("⚠️ Démarrage sans base de données - Mode dégradé")
    
#     yield
    
#     # Shutdown
#     logger.info("Arrêt de l'application...")
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestionnaire de cycle de vie de l'application - VERSION DEBUG
    """
    # Startup
    logger.info("Démarrage de l'application en mode debug...")
    
    # Temporairement désactivé pour debug
    # try:
    #     create_tables()
    #     logger.info("Tables de base de données créées/vérifiées avec succès")
    # except Exception as e:
    #     logger.error(f"Erreur lors de la création des tables: {e}")
    #     raise
    
    logger.info("✅ Démarrage terminé (sans DB pour debug)")
    yield
    
    # Shutdown
    logger.info("Arrêt de l'application...")

def create_app() -> FastAPI:
    """
    Factory pour créer l'application FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="API REST pour la gestion d'un concessionnaire automobile",
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
        lifespan=lifespan
    )
    
    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    # Middleware de sécurité pour les hosts de confiance
    if not settings.DEBUG:
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"]
        )
    
    # Middleware pour mesurer le temps de réponse
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    # Gestionnaires d'exceptions personnalisés
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """
        Gestionnaire pour les erreurs de validation Pydantic
        """
        logger.warning(f"Erreur de validation sur {request.url}: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Erreur de validation des données",
                "errors": exc.errors(),
                "message": "Veuillez vérifier les données envoyées"
            }
        )
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """
        Gestionnaire pour les exceptions HTTP
        """
        logger.warning(f"Exception HTTP {exc.status_code} sur {request.url}: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "status_code": exc.status_code
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Gestionnaire pour les exceptions générales
        """
        logger.error(f"Erreur inattendue sur {request.url}: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Erreur interne du serveur",
                "message": "Une erreur inattendue s'est produite"
            }
        )
    
    # Routes de base
    @app.get("/", tags=["Root"])
    async def root():
        """
        Point d'entrée de l'API
        """
        return {
            "message": "Bienvenue sur l'API du Concessionnaire Automobile",
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "status": "online"
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Vérification de l'état de santé de l'API
        """
        return {
            "status": "healthy",
            "timestamp": time.time(),
            "version": settings.APP_VERSION
        }
    
    # Inclusion des routeurs
    app.include_router(auth_router.router)
    app.include_router(cars_router.router)
    app.include_router(reservations_router.router)
    
    return app


# Création de l'instance de l'application
app = create_app()

# Log du démarrage
logger.info(f"Application {settings.APP_NAME} v{settings.APP_VERSION} initialisée")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )