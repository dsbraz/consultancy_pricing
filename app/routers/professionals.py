from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import csv
import io

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/professionals/", response_model=schemas.Professional)
def create_professional(professional: schemas.ProfessionalCreate, db: Session = Depends(get_db)):
    db_professional = models.Professional(
        pid=professional.pid,
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

@router.put("/professionals/{professional_id:int}", response_model=schemas.Professional)
def update_professional(professional_id: int, professional: schemas.ProfessionalUpdate, db: Session = Depends(get_db)):
    db_professional = db.query(models.Professional).filter(models.Professional.id == professional_id).first()
    if not db_professional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    
    # Update only provided fields
    update_data = professional.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_professional, key, value)
    
    db.commit()
    db.refresh(db_professional)
    return db_professional

@router.delete("/professionals/{professional_id:int}")
def delete_professional(professional_id: int, db: Session = Depends(get_db)):
    db_professional = db.query(models.Professional).filter(models.Professional.id == professional_id).first()
    if not db_professional:
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    
    db.delete(db_professional)
    db.commit()
    return {"message": "Professional deleted successfully"}

@router.post("/professionals/import-csv")
async def import_professionals_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Import professionals from CSV file.
    Import professionals from CSV file.
    Expected CSV format: pid,name,role,level,is_vacancy,hourly_cost
    If a professional with the same pid exists, it will be updated.
    Otherwise, a new professional will be created.
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")
    
    # Read file content
    content = await file.read()
    decoded_content = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded_content))
    
    created_count = 0
    updated_count = 0
    error_count = 0
    errors = []
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 to account for header
        try:
            # Validate required fields
            if not row.get('pid') or not row.get('name') or not row.get('role') or not row.get('level'):
                errors.append(f"Linha {row_num}: Campos obrigatórios faltando (pid, name, role, level)")
                error_count += 1
                continue
            
            # Parse fields
            pid = row['pid'].strip()
            name = row['name'].strip()
            role = row['role'].strip()
            level = row['level'].strip()
            
            # Parse is_vacancy (default to False if not provided or invalid)
            is_vacancy_str = row.get('is_vacancy', 'false').strip().lower()
            is_vacancy = is_vacancy_str in ['true', '1', 'yes', 'sim', 'verdadeiro']
            
            # Parse hourly_cost (default to 0.0 if not provided or invalid)
            try:
                hourly_cost = float(row.get('hourly_cost', '0.0').strip())
            except ValueError:
                hourly_cost = 0.0
            
            # Check if professional exists (by pid)
            existing_prof = db.query(models.Professional).filter(
                models.Professional.pid == pid
            ).first()
            
            if existing_prof:
                # Update existing professional
                existing_prof.name = name
                existing_prof.role = role
                existing_prof.level = level
                existing_prof.is_vacancy = is_vacancy
                existing_prof.hourly_cost = hourly_cost
                updated_count += 1
            else:
                # Create new professional
                new_prof = models.Professional(
                    pid=pid,
                    name=name,
                    role=role,
                    level=level,
                    is_vacancy=is_vacancy,
                    hourly_cost=hourly_cost
                )
                db.add(new_prof)
                created_count += 1
            
        except Exception as e:
            errors.append(f"Linha {row_num}: {str(e)}")
            error_count += 1
    
    # Commit all changes
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {str(e)}")
    
    return {
        "message": "Importação concluída",
        "created": created_count,
        "updated": updated_count,
        "errors": error_count,
        "error_details": errors
    }
