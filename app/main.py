from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.routers import professionals, projects, offers, auth
from app.dependencies import get_current_user
import os
import logging
import sys

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

logger.info("Starting Consultancy Pricing API")

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified successfully")
except Exception as e:
    logger.error(f"Failed to create database tables: {str(e)}")
    raise

app = FastAPI(title="Consultancy Pricing API")

# CORS configuration based on environment
cors_origins = os.environ.get("CORS_ORIGINS", "*")
if cors_origins == "*":
    origins_list = ["*"]
    logger.info("CORS configured to allow all origins (development mode)")
else:
    origins_list = [origin.strip() for origin in cors_origins.split(",")]
    logger.info(f"CORS configured for specific origins: {origins_list}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware for Auth
DEFAULT_SECRET_KEY = "default-insecure-secret-key"
SECRET_KEY = os.environ.get("SECRET_KEY", DEFAULT_SECRET_KEY)
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080")
SESSION_COOKIE_HTTPS_ONLY = BASE_URL.startswith("https://")

if not SECRET_KEY or SECRET_KEY == DEFAULT_SECRET_KEY:
    error_message = (
        "SECRET_KEY environment variable must be set to a secure, non-default value"
    )
    logger.error(error_message)
    raise RuntimeError(error_message)

logger.info(
    "Session middleware configured (https_only=%s, same_site=lax, BASE_URL=%s)",
    SESSION_COOKIE_HTTPS_ONLY,
    BASE_URL,
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=SESSION_COOKIE_HTTPS_ONLY,
    same_site="lax",
)

app.include_router(auth.router, tags=["Authentication"])
app.include_router(
    professionals.router,
    tags=["Professionals"],
    dependencies=[Depends(get_current_user)],
)
app.include_router(
    offers.router, tags=["Offers"],
    dependencies=[Depends(get_current_user)]
)
app.include_router(
    projects.router, tags=["Projects"],
    dependencies=[Depends(get_current_user)]
)
logger.info("API routers registered successfully")

frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")
logger.info(f"Frontend static files mounted from: {frontend_dir}")


@app.get("/")
def read_root():
    """Root endpoint for API verification"""
    logger.debug("Root endpoint accessed")
    return {"message": "Welcome to Consultancy Pricing API"}


@app.get("/health")
def health_check():
    """
    Health check endpoint for Docker and monitoring systems.
    Verifies API is running and database is accessible.
    """
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()

        logger.debug("Health check passed")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
