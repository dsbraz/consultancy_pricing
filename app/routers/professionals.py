from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

# --- Profiles ---
# --- Professionals ---
@router.post("/professionals/", response_model=schemas.Professional)
def create_professional(professional: schemas.ProfessionalCreate, db: Session = Depends(get_db)):
    db_professional = models.Professional(
        name=professional.name,
        role=professional.role,
        level=professional.level,
        is_vacancy=professional.is_vacancy,
        hourly_cost=professional.hourly_cost
    )
    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)
    return db_professional

@router.get("/professionals/", response_model=List[schemas.Professional])
def read_professionals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    professionals = db.query(models.Professional).offset(skip).limit(limit).all()
    return professionals

@router.put("/professionals/{professional_id}", response_model=schemas.Professional)
def update_professional(professional_id: int, professional: schemas.ProfessionalUpdate, db: Session = Depends(get_db)):
    db_professional = db.query(models.Professional).filter(models.Professional.id == professional_id).first()
    if not db_professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    
    # Update only provided fields
    update_data = professional.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_professional, key, value)
    
    db.commit()
    db.refresh(db_professional)
    return db_professional

@router.delete("/professionals/{professional_id}")
def delete_professional(professional_id: int, db: Session = Depends(get_db)):
    db_professional = db.query(models.Professional).filter(models.Professional.id == professional_id).first()
    if not db_professional:
        raise HTTPException(status_code=404, detail="Professional not found")
    
    db.delete(db_professional)
    db.commit()
    return {"message": "Professional deleted successfully"}
