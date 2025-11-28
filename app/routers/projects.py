from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import List

import logging

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.pricing_service import PricingService
from app.services.calendar_service import CalendarService
from app.services.excel_service import ExcelExportService
from app.services.png_export_service import PNGExportService
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# Helper functions to reduce code duplication


def get_project_with_allocations(db: Session, project_id: int) -> models.Project:
    """Get project with all allocations and related data for exports"""
    project = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.allocations).joinedload(
                models.ProjectAllocation.professional
            ),
            joinedload(models.Project.allocations).joinedload(
                models.ProjectAllocation.weekly_allocations
            ),
        )
        .filter(models.Project.id == project_id)
        .first()
    )
    if not project:
        logger.warning(f"Project not found: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project


def generate_export_filename(
    project_name: str, extension: str, prefix: str = ""
) -> str:
    """Generate standardized export filename with timestamp"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_name = project_name.replace(" ", "_")
    if prefix:
        return f"{prefix}_{clean_name}_{timestamp}.{extension}"
    return f"{clean_name}_{timestamp}.{extension}"


@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    if project.from_project_id:
        return _clone_project_logic(project, db)

    logger.info(
        f"Creating project: name={project.name}, duration={project.duration_months} months, allocations={len(project.allocations)}"
    )
    db_project = models.Project(
        name=project.name,
        start_date=project.start_date,
        duration_months=project.duration_months,
        tax_rate=project.tax_rate,
        margin_rate=project.margin_rate,
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    for allocation in project.allocations:
        db_allocation = models.ProjectAllocation(
            project_id=db_project.id,
            professional_id=allocation.professional_id,
            hours_per_month=allocation.hours_per_month,
        )
        db.add(db_allocation)

    db.commit()
    db.refresh(db_project)
    logger.info(
        f"Project created successfully: id={db_project.id}, name={db_project.name}"
    )
    return db_project


def _clone_project_logic(project: schemas.ProjectCreate, db: Session) -> models.Project:
    """Clone project from existing project"""
    logger.info(f"Cloning project from id={project.from_project_id}")

    original = (
        db.query(models.Project)
        .options(
            joinedload(models.Project.allocations).joinedload(
                models.ProjectAllocation.weekly_allocations
            )
        )
        .filter(models.Project.id == project.from_project_id)
        .first()
    )

    if not original:
        raise HTTPException(status_code=404, detail="Projeto original não encontrado")

    new_project = models.Project(
        name=project.name,
        start_date=project.start_date,
        duration_months=project.duration_months,
        tax_rate=project.tax_rate,
        margin_rate=project.margin_rate,
    )
    db.add(new_project)
    db.flush()

    for orig_alloc in original.allocations:
        new_alloc = models.ProjectAllocation(
            project_id=new_project.id,
            professional_id=orig_alloc.professional_id,
            selling_hourly_rate=orig_alloc.selling_hourly_rate,
        )
        db.add(new_alloc)
        db.flush()

        for orig_weekly in orig_alloc.weekly_allocations:
            new_weekly = models.WeeklyAllocation(
                allocation_id=new_alloc.id,
                week_number=orig_weekly.week_number,
                hours_allocated=orig_weekly.hours_allocated,
                available_hours=orig_weekly.available_hours,
            )
            db.add(new_weekly)

    db.commit()
    db.refresh(new_project)
    logger.info(
        f"Project cloned: original_id={project.from_project_id}, new_id={new_project.id}"
    )
    return new_project


@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = (
        db.query(models.Project)
        .order_by(func.lower(models.Project.name))
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.debug(f"Retrieved {len(projects)} projects (skip={skip}, limit={limit})")
    return projects


@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project


@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    logger.info(f"Updating project: id={project_id}")

    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if not db_project:
        logger.warning(f"Project not found for update: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    duration_changed = (
        project.duration_months is not None
        and project.duration_months != db_project.duration_months
    )
    start_date_changed = (
        project.start_date is not None and project.start_date != db_project.start_date
    )

    update_data = project.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)

    db.commit()

    if duration_changed or start_date_changed:
        calendar_service = CalendarService(country_code="BR")
        new_weeks = calendar_service.get_weekly_breakdown(
            db_project.start_date, db_project.duration_months
        )

        new_weeks_map = {w["week_number"]: w for w in new_weeks}

        allocations = (
            db.query(models.ProjectAllocation)
            .filter(models.ProjectAllocation.project_id == project_id)
            .all()
        )

        for allocation in allocations:
            existing_weeks = {w.week_number: w for w in allocation.weekly_allocations}

            new_week_numbers = set(new_weeks_map.keys())
            existing_week_numbers = set(existing_weeks.keys())

            weeks_to_update = existing_week_numbers & new_week_numbers
            for week_num in weeks_to_update:
                existing_week = existing_weeks[week_num]
                new_week_data = new_weeks_map[week_num]

                existing_week.available_hours = new_week_data["available_hours"]

            weeks_to_remove = existing_week_numbers - new_week_numbers
            for week_num in weeks_to_remove:
                db.delete(existing_weeks[week_num])

            weeks_to_add = new_week_numbers - existing_week_numbers
            for week_num in weeks_to_add:
                week = new_weeks_map[week_num]
                new_weekly_alloc = models.WeeklyAllocation(
                    allocation_id=allocation.id,
                    week_number=week["week_number"],
                    hours_allocated=0.0,  # Default to 0, user can adjust manually
                    available_hours=week["available_hours"],
                )
                db.add(new_weekly_alloc)

        db.commit()
        logger.info(
            f"Project allocation dates updated: project_id={project_id}, weeks_adjusted={len(new_weeks)}"
        )

    db.refresh(db_project)
    logger.info(f"Project updated successfully: id={project_id}")
    return db_project


@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting project: id={project_id}")
    db_project = (
        db.query(models.Project).filter(models.Project.id == project_id).first()
    )
    if not db_project:
        logger.warning(f"Project not found for deletion: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    try:
        # 1. Find all allocations for this project
        allocations = (
            db.query(models.ProjectAllocation)
            .filter(models.ProjectAllocation.project_id == project_id)
            .all()
        )
        allocation_ids = [a.id for a in allocations]

        if allocation_ids:
            # 2. Delete all weekly allocations associated with these allocations
            db.query(models.WeeklyAllocation).filter(
                models.WeeklyAllocation.allocation_id.in_(allocation_ids)
            ).delete(synchronize_session=False)

            # 3. Delete the allocations themselves
            db.query(models.ProjectAllocation).filter(
                models.ProjectAllocation.project_id == project_id
            ).delete(synchronize_session=False)

        # 4. Finally delete the project
        db.delete(db_project)
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Integrity error deleting project: id={project_id} (likely referenced by other records)"
        )
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir este projeto pois ele possui dependências.",
        )

    logger.info(f"Project deleted successfully: id={project_id}")
    return {"message": "Project deleted successfully"}


@router.post("/projects/{project_id}/offers")
def apply_offer_to_project(
    project_id: int, request: schemas.ApplyOfferRequest, db: Session = Depends(get_db)
):
    logger.info(
        f"Applying offer to project: project_id={project_id}, offer_id={request.offer_id}"
    )

    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    offer = (
        db.query(models.Offer)
        .options(joinedload(models.Offer.items))
        .filter(models.Offer.id == request.offer_id)
        .first()
    )

    if not project or not offer:
        logger.warning(
            f"Project or offer not found: project_id={project_id}, offer_id={request.offer_id}"
        )
        raise HTTPException(status_code=404, detail="Projeto ou Oferta não encontrado")

    calendar_service = CalendarService(country_code="BR")
    weeks = calendar_service.get_weekly_breakdown(
        project.start_date, project.duration_months
    )

    allocations_added = []

    for item in offer.items:
        professionals_to_allocate = []

        prof = (
            db.query(models.Professional)
            .filter(models.Professional.id == item.professional_id)
            .first()
        )
        if not prof:
            logger.warning(
                f"Professional {item.professional_id} not found for offer item"
            )
            continue

        professionals_to_allocate.append(prof)

        for professional in professionals_to_allocate:
            existing = (
                db.query(models.ProjectAllocation)
                .filter(
                    models.ProjectAllocation.project_id == project.id,
                    models.ProjectAllocation.professional_id == professional.id,
                )
                .first()
            )

            if existing:
                continue

            margin_rate = (
                project.margin_rate / 100.0
                if project.margin_rate > 1
                else project.margin_rate
            )
            divisor = 1 - margin_rate
            if divisor <= 0:
                selling_rate = professional.hourly_cost
            else:
                selling_rate = professional.hourly_cost / divisor

            db_alloc = models.ProjectAllocation(
                project_id=project.id,
                professional_id=professional.id,
                selling_hourly_rate=selling_rate,
            )
            db.add(db_alloc)
            db.flush()
            for week in weeks:
                weekly_alloc = models.WeeklyAllocation(
                    allocation_id=db_alloc.id,
                    week_number=week["week_number"],
                    hours_allocated=week["available_hours"]
                    * (item.allocation_percentage / 100.0),
                    available_hours=week["available_hours"],
                )
                db.add(weekly_alloc)

            allocations_added.append(professional.name)

    db.commit()
    logger.info(
        f"Offer applied successfully: project_id={project_id}, professionals_added={len(allocations_added)}, weeks={len(weeks)}"
    )
    return {
        "message": "Offer applied",
        "allocations": allocations_added,
        "weeks_count": len(weeks),
    }


@router.get("/projects/{project_id}/pricing", response_model=schemas.ProjectPricing)
def get_project_pricing(project_id: int, db: Session = Depends(get_db)):
    logger.info(f"Calculating price for project: id={project_id}")
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        logger.warning(f"Project not found for pricing: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    pricing_service = PricingService(db)

    try:
        result = pricing_service.calculate_project_pricing(project)
        logger.info(
            f"Price calculated: project_id={project_id}, total_cost={result['total_cost']:.2f}, final_price={result['final_price']:.2f}"
        )
        return result
    except ValueError as e:
        logger.error(f"Price calculation failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/projects/{project_id}/timeline")
def get_project_timeline(project_id: int, db: Session = Depends(get_db)):
    """
    Get the weekly timeline breakdown for a project.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    calendar_service = CalendarService(country_code="BR")
    weeks = calendar_service.get_weekly_breakdown(
        project.start_date, project.duration_months
    )
    return weeks


@router.get(
    "/projects/{project_id}/allocations", response_model=List[schemas.ProjectAllocation]
)
def get_project_allocations(project_id: int, db: Session = Depends(get_db)):
    """
    Get all allocations for a project, including professional details and weekly breakdown.
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    allocations = (
        db.query(models.ProjectAllocation)
        .options(
            joinedload(models.ProjectAllocation.professional),
            joinedload(models.ProjectAllocation.weekly_allocations),
        )
        .filter(models.ProjectAllocation.project_id == project_id)
        .all()
    )
    return allocations


@router.put("/projects/{project_id}/allocations")
def update_allocations(
    project_id: int, updates: List[dict], db: Session = Depends(get_db)
):
    """
    Bulk update allocations and weekly hours.
    Expected format: [
        {
            "allocation_id": 1,  # For updating selling rate
            "selling_hourly_rate": 150.0
        },
        {
            "weekly_allocation_id": 1,  # For updating hours
            "hours_allocated": 35.0
        },
        ...
    ]
    """
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    updated_count = 0
    for update in updates:
        allocation_id = update.get("allocation_id")
        if allocation_id:
            selling_rate = update.get("selling_hourly_rate")
            if selling_rate is not None:
                allocation = (
                    db.query(models.ProjectAllocation)
                    .filter(models.ProjectAllocation.id == allocation_id)
                    .first()
                )
                if allocation:
                    allocation.selling_hourly_rate = selling_rate
                    updated_count += 1

        # Handle weekly allocation updates
        weekly_alloc_id = update.get("weekly_allocation_id")
        if weekly_alloc_id:
            hours = update.get("hours_allocated")
            if hours is not None:
                weekly_alloc = (
                    db.query(models.WeeklyAllocation)
                    .filter(models.WeeklyAllocation.id == weekly_alloc_id)
                    .first()
                )

                if weekly_alloc:
                    # Validate hours don't exceed available
                    if hours > weekly_alloc.available_hours:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Horas ({hours}) excedem as horas disponíveis ({weekly_alloc.available_hours}) para a semana {weekly_alloc.week_number}",
                        )
                    weekly_alloc.hours_allocated = hours
                    updated_count += 1

    db.commit()
    logger.info(
        f"Allocations updated: project_id={project_id}, items_updated={updated_count}"
    )
    return {"message": f"Updated {updated_count} items", "updated_count": updated_count}


@router.post("/projects/{project_id}/allocations/")
def add_professional_to_project(
    project_id: int,
    professional_id: int,
    selling_hourly_rate: float = None,
    db: Session = Depends(get_db),
):
    """
    Manually add a professional to a project.
    Creates ProjectAllocation and WeeklyAllocations for all project weeks.
    """
    logger.info(
        f"Adding professional to project: project_id={project_id}, professional_id={professional_id}"
    )

    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        logger.warning(f"Project not found: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")

    professional = (
        db.query(models.Professional)
        .filter(models.Professional.id == professional_id)
        .first()
    )
    if not professional:
        logger.warning(f"Professional not found: id={professional_id}")
        raise HTTPException(status_code=404, detail="Profissional não encontrado")

    if selling_hourly_rate is None:
        margin_rate = (
            project.margin_rate / 100.0
            if project.margin_rate > 1
            else project.margin_rate
        )
        divisor = 1 - margin_rate
        if divisor <= 0:
            selling_hourly_rate = professional.hourly_cost
        else:
            selling_hourly_rate = professional.hourly_cost / divisor

    allocation = models.ProjectAllocation(
        project_id=project_id,
        professional_id=professional_id,
        selling_hourly_rate=selling_hourly_rate,
    )
    db.add(allocation)
    db.flush()

    calendar_service = CalendarService(country_code="BR")
    weeks = calendar_service.get_weekly_breakdown(
        project.start_date, project.duration_months
    )

    for week in weeks:
        weekly_alloc = models.WeeklyAllocation(
            allocation_id=allocation.id,
            week_number=week["week_number"],
            hours_allocated=0.0,  # User will fill in hours manually
            available_hours=week["available_hours"],
        )
        db.add(weekly_alloc)

    db.commit()
    db.refresh(allocation)

    logger.info(
        f"Professional added to project: project_id={project_id}, professional_id={professional_id}, weeks={len(weeks)}"
    )

    return {
        "message": "Professional added to project",
        "allocation_id": allocation.id,
        "professional_name": professional.name,
        "selling_hourly_rate": selling_hourly_rate,
        "weeks_created": len(weeks),
    }


@router.delete("/projects/{project_id}/allocations/{allocation_id}")
def remove_professional_from_project(
    project_id: int, allocation_id: int, db: Session = Depends(get_db)
):
    """
    Remove a professional allocation from a project.
    Deletes the ProjectAllocation and all associated WeeklyAllocations (cascade).
    """
    logger.info(
        f"Removing professional from project: project_id={project_id}, allocation_id={allocation_id}"
    )
    allocation = (
        db.query(models.ProjectAllocation)
        .filter(
            models.ProjectAllocation.id == allocation_id,
            models.ProjectAllocation.project_id == project_id,
        )
        .first()
    )

    if not allocation:
        logger.warning(
            f"Allocation not found for removal: project_id={project_id}, allocation_id={allocation_id}"
        )
        raise HTTPException(status_code=404, detail="Alocação não encontrada")

    professional_name = allocation.professional.name

    db.delete(allocation)
    db.commit()

    logger.info(
        f"Professional removed from project: {professional_name}, allocation_id={allocation_id}"
    )

    return {
        "message": f"Professional {professional_name} removed from project",
        "allocation_id": allocation_id,
    }


@router.get("/projects/{project_id}/export")
def export_project(
    project_id: int, format: str = "xlsx", db: Session = Depends(get_db)
):
    """
    Exporta um projeto completo para arquivo Excel ou PNG.

    Args:
        project_id: ID do projeto
        format: Formato de exportação ('xlsx' ou 'png')

    Returns:
        Arquivo Excel (.xlsx) ou PNG (.png) para download
    """
    logger.info(f"Exporting project: id={project_id}, format={format}")

    project = get_project_with_allocations(db, project_id)

    if format == "xlsx":
        excel_service = ExcelExportService(db)
        file = excel_service.export_project_to_excel(project)
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        filename = generate_export_filename(project.name, "xlsx", prefix="projeto")
    elif format == "png":
        png_service = PNGExportService(db)
        file = png_service.export_project_to_png(project)
        media_type = "image/png"
        filename = generate_export_filename(project.name, "png")
    else:
        raise HTTPException(
            status_code=400, detail="Formato inválido. Use 'xlsx' ou 'png'."
        )

    logger.info(
        f"Export successful: project_id={project_id}, format={format}, filename={filename}"
    )
    return StreamingResponse(
        file,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
