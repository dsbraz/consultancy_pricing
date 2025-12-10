from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import StaleDataError
from typing import List

import logging

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.pricing_service import PricingService
from app.services.excel_service import ExcelExportService
from app.services.png_export_service import PNGExportService
from app.services.project_allocation_service import ProjectAllocationService
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)


# Helper functions to reduce code duplication
def _get_project_or_404(db: Session, project_id: int) -> models.Project:
    """Fetch project with allocations or raise 404."""
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


def _get_offer_or_404(db: Session, offer_id: int) -> models.Offer:
    offer = (
        db.query(models.Offer)
        .options(joinedload(models.Offer.items))
        .filter(models.Offer.id == offer_id)
        .first()
    )
    if not offer:
        logger.warning(f"Offer not found: id={offer_id}")
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    return offer


def _get_allocation_or_404(
    db: Session, project_id: int, allocation_id: int
) -> models.ProjectAllocation:
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
            f"Allocation not found: project_id={project_id}, allocation_id={allocation_id}"
        )
        raise HTTPException(status_code=404, detail="Alocação não encontrada")
    return allocation


def _get_weekly_allocation_or_404(
    db: Session, project_id: int, weekly_allocation_id: int
) -> models.WeeklyAllocation:
    weekly_alloc = (
        db.query(models.WeeklyAllocation)
        .join(
            models.ProjectAllocation,
            models.ProjectAllocation.id == models.WeeklyAllocation.allocation_id,
        )
        .filter(
            models.WeeklyAllocation.id == weekly_allocation_id,
            models.ProjectAllocation.project_id == project_id,
        )
        .first()
    )
    if not weekly_alloc:
        logger.warning(
            f"Weekly allocation not found: project_id={project_id}, weekly_allocation_id={weekly_allocation_id}"
        )
        raise HTTPException(
            status_code=404,
            detail="Alocação semanal não pertence a este projeto ou não existe",
        )
    return weekly_alloc


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
    """Create a new project"""
    if project.from_project_id:
        return _clone_project_logic(project, db)

    logger.info(
        f"Creating project: name={project.name}, duration={project.duration_months} months, allocations={len(project.allocations)}"
    )
    try:
        allocation_service = ProjectAllocationService(db)
        db_project = models.Project(
            name=project.name,
            start_date=project.start_date,
            duration_months=project.duration_months,
            tax_rate=project.tax_rate,
            margin_rate=project.margin_rate,
        )
        db.add(db_project)
        db.flush()  # Flush to get ID, but don't commit yet

        # Generate weeks structure
        weeks = allocation_service.get_project_weeks(db_project)

        for allocation in project.allocations:
            prof = _get_professional_or_404(db, allocation.professional_id)

            selling_rate = allocation_service.calculate_selling_rate(
                db_project, prof, allocation.selling_hourly_rate
            )
            allocation_service.create_allocation(
                project=db_project,
                professional=prof,
                selling_hourly_rate=selling_rate,
                allocation_percentage=0.0,
                weeks=weeks,
            )

        db.commit()
        db.refresh(db_project)
        # Ensure allocations and related data are loaded for the response
        _ = db_project.allocations
        logger.info(
            f"Project created successfully: id={db_project.id}, name={db_project.name}"
        )
        return db_project
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating project: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao criar projeto: {str(e)}")


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

    allocation_service = ProjectAllocationService(db)
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
        allocation_service.clone_allocation(
            original=orig_alloc, target_project=new_project
        )

    db.commit()
    db.refresh(new_project)
    # Ensure allocations and related data are loaded for the response
    _ = new_project.allocations
    logger.info(
        f"Project cloned: original_id={project.from_project_id}, new_id={new_project.id}"
    )
    return new_project


@router.get("/projects/", response_model=schemas.PaginatedResponse[schemas.Project])
def read_projects(
    skip: int = 0,
    limit: int = 100,
    search: str = None,
    db: Session = Depends(get_db),
):
    """
    List all projects with pagination.

    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        search: Optional search term to filter projects by name

    Returns:
        PaginatedResponse[Project]: {"items": List[Project], "total": int}
    """
    # Base query
    base_query = db.query(models.Project)

    # Aplicar filtro de busca se fornecido
    if search:
        base_query = base_query.filter(models.Project.name.ilike(f"%{search}%"))

    # Calcula total antes de aplicar offset/limit (considerando filtro de busca)
    total_count = base_query.count()

    # Busca projetos sem alocações (otimização)
    projects = (
        base_query
        .order_by(func.lower(models.Project.name))
        .offset(skip)
        .limit(limit)
        .all()
    )

    logger.debug(
        "Retrieved %s projects (skip=%s, limit=%s, total=%s, search=%s)",
        len(projects),
        skip,
        limit,
        total_count,
        search,
    )
    return schemas.PaginatedResponse(items=projects, total=total_count)


@router.get(
    "/projects/{project_id}",
    response_model=schemas.Project,
    responses={404: {"model": schemas.ErrorResponse}},
)
def read_project(project_id: int, db: Session = Depends(get_db)):
    """Get a single project by ID"""
    return _get_project_or_404(db, project_id)


@router.patch("/projects/{project_id}", response_model=schemas.Project)
def update_project(
    project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)
):
    """Update a project's details"""
    logger.info(f"Updating project: id={project_id}")

    db_project = _get_project_or_404(db, project_id)
    allocation_service = ProjectAllocationService(db)

    duration_changed = (
        project.duration_months is not None
        and project.duration_months != db_project.duration_months
    )
    start_date_changed = (
        project.start_date is not None and project.start_date != db_project.start_date
    )

    try:
        update_data = project.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_project, key, value)

        if duration_changed or start_date_changed:
            weeks_adjusted = allocation_service.sync_project_weeks(db_project)
            logger.info(
                f"Project allocation dates updated: project_id={project_id}, weeks_adjusted={weeks_adjusted}"
            )

        db.commit()
        db.refresh(db_project)
        logger.info(f"Project updated successfully: id={project_id}")
        return db_project
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating project: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Erro ao atualizar projeto: {str(e)}"
        )


@router.delete(
    "/projects/{project_id}",
    responses={
        404: {"model": schemas.ErrorResponse},
        409: {"model": schemas.ErrorResponse},
    },
)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project and its allocations"""
    logger.info(f"Deleting project: id={project_id}")
    db_project = _get_project_or_404(db, project_id)

    try:
        # Delete allocations and their weekly allocations individually
        # This uses the objects already loaded by _get_project_or_404, avoiding StaleDataError
        if db_project.allocations:
            for allocation in db_project.allocations:
                # Delete weekly allocations first (cascade will handle this, but being explicit)
                if allocation.weekly_allocations:
                    for weekly in allocation.weekly_allocations:
                        db.delete(weekly)
                # Delete the allocation itself
                db.delete(allocation)

        # Finally delete the project
        db.delete(db_project)
        db.commit()
    except StaleDataError as e:
        db.rollback()
        logger.error(
            f"StaleDataError deleting project: id={project_id}, error={str(e)}. "
            "This may occur if objects were modified by another transaction."
        )
        raise HTTPException(
            status_code=409,
            detail="O projeto foi modificado por outra operação. Por favor, recarregue a página e tente novamente.",
        )
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Integrity error deleting project: id={project_id} (likely referenced by other records)"
        )
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir este projeto pois ele possui dependências.",
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting project: id={project_id}, error={str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao excluir projeto: {str(e)}",
        )

    logger.info(f"Project deleted successfully: id={project_id}")
    return {"message": "Project deleted successfully"}


@router.post(
    "/projects/{project_id}/offers",
    responses={
        404: {"model": schemas.ErrorResponse},
        409: {"model": schemas.ErrorResponse},
    },
)
def apply_offer_to_project(
    project_id: int, request: schemas.ApplyOfferRequest, db: Session = Depends(get_db)
):
    """Apply an offer template to a project"""
    logger.info(
        f"Applying offer to project: project_id={project_id}, offer_id={request.offer_id}"
    )

    project = _get_project_or_404(db, project_id)
    offer = _get_offer_or_404(db, request.offer_id)
    allocation_service = ProjectAllocationService(db)
    weeks = allocation_service.get_project_weeks(project)

    allocations_added = []

    try:
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

                allocation_service.create_allocation(
                    project=project,
                    professional=professional,
                    allocation_percentage=item.allocation_percentage,
                    weeks=weeks,
                )

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
    except Exception as e:
        db.rollback()
        logger.error(f"Error applying offer: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao aplicar oferta: {str(e)}")


@router.get(
    "/projects/{project_id}/pricing",
    response_model=schemas.ProjectPricing,
    responses={
        404: {"model": schemas.ErrorResponse},
        400: {"model": schemas.ErrorResponse},
    },
)
def get_project_pricing(project_id: int, db: Session = Depends(get_db)):
    """Calculate and retrieve project pricing details"""
    logger.info(f"Calculating price for project: id={project_id}")
    project = _get_project_or_404(db, project_id)

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
    project = _get_project_or_404(db, project_id)
    allocation_service = ProjectAllocationService(db)
    return allocation_service.get_project_weeks(project)


@router.patch(
    "/projects/{project_id}/allocations",
    responses={
        404: {"model": schemas.ErrorResponse},
        400: {"model": schemas.ErrorResponse},
    },
)
def update_allocations(
    project_id: int,
    updates: List[schemas.AllocationUpdateItem],
    db: Session = Depends(get_db),
):
    """
    Bulk update allocations and weekly hours.
    Expected format:
        [
            {"allocation_id": 1, "selling_hourly_rate": 150.0},
            {"weekly_allocation_id": 1, "hours_allocated": 35.0},
            ...
        ]
    """
    _get_project_or_404(db, project_id)

    updated_count = 0
    for update in updates:
        if update.allocation_id is not None:
            allocation = _get_allocation_or_404(db, project_id, update.allocation_id)
            allocation.selling_hourly_rate = update.selling_hourly_rate
            updated_count += 1

        if update.weekly_allocation_id is not None:
            weekly_alloc = _get_weekly_allocation_or_404(
                db, project_id, update.weekly_allocation_id
            )

            hours = update.hours_allocated
            if hours is None:
                raise HTTPException(
                    status_code=400,
                    detail="hours_allocated é obrigatório para atualizar alocações semanais",
                )

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

    project = _get_project_or_404(db, project_id)
    professional = _get_professional_or_404(db, professional_id)
    allocation_service = ProjectAllocationService(db)

    if selling_hourly_rate is None:
        selling_hourly_rate = allocation_service.calculate_selling_rate(
            project, professional
        )

    try:
        weeks = allocation_service.get_project_weeks(project)
        allocation = allocation_service.create_allocation(
            project=project,
            professional=professional,
            selling_hourly_rate=selling_hourly_rate,
            allocation_percentage=100.0,
            weeks=weeks,
        )

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
    except Exception as e:
        db.rollback()
        logger.error(f"Error adding professional to project: {str(e)}")
        raise HTTPException(
            status_code=400, detail=f"Erro ao adicionar profissional: {str(e)}"
        )


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
    allocation = _get_allocation_or_404(db, project_id, allocation_id)
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
    Export a complete project to an Excel or PNG file.

    Args:
        project_id: Project ID
        format: Export format ('xlsx' or 'png')

    Returns:
        Excel (.xlsx) or PNG (.png) file for download
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
