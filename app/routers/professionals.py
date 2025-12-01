from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import List
import csv
import io
import logging

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_professional_or_404(db: Session, professional_id: int) -> models.Professional:
    """Fetch professional or raise 404."""
    professional = (
        db.query(models.Professional)
        .filter(models.Professional.id == professional_id)
        .first()
    )
    if not professional:
        logger.warning(f"Professional not found: id={professional_id}")
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    return professional


@router.post("/professionals/", response_model=schemas.Professional)
def create_professional(
    professional: schemas.ProfessionalCreate, db: Session = Depends(get_db)
):
    """Create a new professional"""
    logger.info(
        f"Creating professional: pid={professional.pid}, name={professional.name}"
    )
    db_professional = models.Professional(
        pid=professional.pid,
        name=professional.name,
        role=professional.role,
        level=professional.level,
        is_template=professional.is_template,
        hourly_cost=professional.hourly_cost,
    )
    db.add(db_professional)
    db.commit()
    db.refresh(db_professional)
    logger.info(
        f"Professional created successfully: id={db_professional.id}, pid={db_professional.pid}"
    )
    return db_professional


@router.get("/professionals/", response_model=List[schemas.Professional])
def read_professionals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all professionals with pagination"""
    professionals = (
        db.query(models.Professional)
        .order_by(func.lower(models.Professional.name))
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.debug(
        f"Retrieved {len(professionals)} professionals (skip={skip}, limit={limit})"
    )
    return professionals


@router.get("/professionals/{professional_id}", response_model=schemas.Professional)
def get_professional(professional_id: int, db: Session = Depends(get_db)):
    """Get a single professional by ID"""
    logger.debug(f"Fetching professional: id={professional_id}")
    return _get_professional_or_404(db, professional_id)


@router.patch("/professionals/{professional_id}", response_model=schemas.Professional)
def update_professional(
    professional_id: int,
    professional: schemas.ProfessionalUpdate,
    db: Session = Depends(get_db),
):
    """Update a professional's details"""
    logger.info(f"Updating professional: id={professional_id}")
    db_professional = _get_professional_or_404(db, professional_id)

    update_data = professional.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_professional, key, value)

    db.commit()
    db.refresh(db_professional)
    logger.info(
        f"Professional updated successfully: id={professional_id}, pid={db_professional.pid}"
    )
    return db_professional


@router.delete("/professionals/{professional_id}")
def delete_professional(professional_id: int, db: Session = Depends(get_db)):
    """Delete a professional"""
    logger.info(f"Deleting professional: id={professional_id}")
    db_professional = _get_professional_or_404(db, professional_id)

    try:
        db.delete(db_professional)
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Integrity error deleting professional: id={professional_id} (likely referenced by other records)"
        )
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir este profissional pois ele está associado a projetos ou ofertas.",
        )

    logger.info(
        f"Professional deleted successfully: id={professional_id}, pid={db_professional.pid}"
    )
    return {"message": "Professional deleted successfully"}


@router.post("/professionals/import-csv")
async def import_professionals_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """
    Import professionals from CSV file.
    Expected CSV format: pid,name,role,level,is_template,hourly_cost
    If a professional with the same pid exists, it will be updated.
    Otherwise, a new professional will be created.
    """
    if not file.filename.endswith(".csv"):
        logger.warning(f"Invalid file type for CSV import: {file.filename}")
        raise HTTPException(status_code=400, detail="Arquivo deve ser um CSV")

    logger.info(f"Starting CSV import from file: {file.filename}")
    content = await file.read()
    decoded_content = content.decode("utf-8")
    csv_reader = csv.DictReader(io.StringIO(decoded_content))

    created_count = 0
    updated_count = 0
    error_count = 0
    errors = []

    # Read all rows into a list to allow for re-indexing if needed, though DictReader is used
    rows = list(csv_reader)

    for row_num, row in enumerate(
        rows, start=2
    ):  # Start at 2 for 1-based line numbers in CSV, assuming header is line 1
        try:
            if (
                not row.get("pid")
                or not row.get("name")
                or not row.get("role")
                or not row.get("level")
            ):
                errors.append(
                    f"Linha {row_num}: Campos obrigatórios faltando (pid, name, role, level)"
                )
                error_count += 1
                continue

            pid = row["pid"].strip()
            name = row["name"].strip()
            role = row["role"].strip()
            level = row["level"].strip()

            # Parse is_template (default to False if not provided or invalid)
            is_template_str = row.get("is_template", "false").strip().lower()
            is_template = is_template_str in ["true", "1", "yes", "sim", "verdadeiro"]

            # Parse hourly_cost (default to 0.0 if not provided or invalid)
            try:
                hourly_cost = float(row.get("hourly_cost", "0.0").strip())
            except ValueError:
                hourly_cost = 0.0

            existing_prof = (
                db.query(models.Professional)
                .filter(models.Professional.pid == pid)
                .first()
            )

            if existing_prof:
                existing_prof.name = name
                existing_prof.role = role
                existing_prof.level = level
                existing_prof.is_template = is_template
                existing_prof.hourly_cost = hourly_cost
                updated_count += 1
            else:
                new_prof = models.Professional(
                    pid=pid,
                    name=name,
                    role=role,
                    level=level,
                    is_template=is_template,
                    hourly_cost=hourly_cost,
                )
                db.add(new_prof)
                created_count += 1

        except Exception as e:
            errors.append(f"Linha {row_num}: {str(e)}")
            error_count += 1

    try:
        db.commit()
        logger.info(
            f"CSV import completed: created={created_count}, updated={updated_count}, errors={error_count}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"CSV import failed during commit: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro ao salvar no banco de dados: {str(e)}"
        )

    if error_count > 0:
        logger.warning(f"CSV import had {error_count} errors")

    return {
        "message": "Importação concluída",
        "created": created_count,
        "updated": updated_count,
        "errors": error_count,
        "error_details": errors,
    }
