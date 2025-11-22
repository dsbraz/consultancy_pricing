from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.routers import professionals, projects, offers
import os

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Consultancy Pricing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development, allow all. In prod, specify origin.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(professionals.router, tags=["Professionals"])
app.include_router(offers.router, tags=["Offers"])
app.include_router(projects.router, tags=["Projects"])

frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/frontend", StaticFiles(directory=frontend_dir, html=True), name="frontend")

@app.get("/")
def read_root():
    return {"message": "Welcome to Consultancy Pricing API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint for Docker and monitoring systems.
    Verifies API is running and database is accessible.
    """
    try:
        # Check database connectivity
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
