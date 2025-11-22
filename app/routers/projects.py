from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from typing import List
import uuid
import logging

from app.database import get_db
from app.models import models
from app.schemas import schemas
from app.services.pricing_service import PricingService
from app.services.calendar_service import CalendarService
from app.services.excel_service import ExcelExportService
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating project: name={project.name}, duration={project.duration_months} months, allocations={len(project.allocations)}")
    db_project = models.Project(
        name=project.name,
        start_date=project.start_date,
        duration_months=project.duration_months,
        tax_rate=project.tax_rate,
        margin_rate=project.margin_rate
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    for allocation in project.allocations:
        db_allocation = models.ProjectAllocation(
            project_id=db_project.id,
            professional_id=allocation.professional_id,
            hours_per_month=allocation.hours_per_month
        )
        db.add(db_allocation)
        
    db.commit()
    db.refresh(db_project)
    logger.info(f"Project created successfully: id={db_project.id}, name={db_project.name}")
    return db_project

@router.get("/projects/", response_model=List[schemas.Project])
def read_projects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    projects = db.query(models.Project).offset(skip).limit(limit).all()
    logger.debug(f"Retrieved {len(projects)} projects (skip={skip}, limit={limit})")
    return projects

@router.get("/projects/{project_id}", response_model=schemas.Project)
def read_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    return project

@router.put("/projects/{project_id}", response_model=schemas.Project)
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating project: id={project_id}")
    
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        logger.warning(f"Project not found for update: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    duration_changed = project.duration_months is not None and project.duration_months != db_project.duration_months
    start_date_changed = project.start_date is not None and project.start_date != db_project.start_date
    
    update_data = project.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_project, key, value)
    
    db.commit()
    
    if duration_changed or start_date_changed:
        calendar_service = CalendarService(country_code='BR')
        new_weeks = calendar_service.get_weekly_breakdown(db_project.start_date, db_project.duration_months)
        
        new_weeks_map = {w['week_number']: w for w in new_weeks}
        
        allocations = db.query(models.ProjectAllocation).filter(
            models.ProjectAllocation.project_id == project_id
        ).all()
        
        for allocation in allocations:
            existing_weeks = {w.week_number: w for w in allocation.weekly_allocations}
            
            new_week_numbers = set(new_weeks_map.keys())
            existing_week_numbers = set(existing_weeks.keys())
            
            weeks_to_update = existing_week_numbers & new_week_numbers
            for week_num in weeks_to_update:
                existing_week = existing_weeks[week_num]
                new_week_data = new_weeks_map[week_num]
                
                existing_week.week_start_date = datetime.fromisoformat(new_week_data['week_start']).date()
                existing_week.available_hours = new_week_data['available_hours']
            
            weeks_to_remove = existing_week_numbers - new_week_numbers
            for week_num in weeks_to_remove:
                db.delete(existing_weeks[week_num])
            

            weeks_to_add = new_week_numbers - existing_week_numbers
            for week_num in weeks_to_add:
                week = new_weeks_map[week_num]
                new_weekly_alloc = models.WeeklyAllocation(
                    allocation_id=allocation.id,
                    week_number=week['week_number'],
                    week_start_date=datetime.fromisoformat(week['week_start']).date(),
                    hours_allocated=0.0,  # Default to 0, user can adjust manually
                    available_hours=week['available_hours']
                )
                db.add(new_weekly_alloc)
        
        db.commit()
        logger.info(f"Project allocation dates updated: project_id={project_id}, weeks_adjusted={len(new_weeks)}")
    
    db.refresh(db_project)
    logger.info(f"Project updated successfully: id={project_id}")
    return db_project

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting project: id={project_id}")
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        logger.warning(f"Project not found for deletion: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    db.query(models.ProjectAllocation).filter(models.ProjectAllocation.project_id == project_id).delete()
    
    db.delete(db_project)
    db.commit()
    logger.info(f"Project deleted successfully: id={project_id}")
    return {"message": "Project deleted successfully"}

@router.post("/projects/{project_id}/apply_offer/{offer_id}")
def apply_offer(project_id: int, offer_id: int, db: Session = Depends(get_db)):
    logger.info(f"Applying offer to project: project_id={project_id}, offer_id={offer_id}")
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    offer = db.query(models.Offer).options(
        joinedload(models.Offer.items)
    ).filter(models.Offer.id == offer_id).first()
    
    if not project or not offer:
        logger.warning(f"Project or offer not found: project_id={project_id}, offer_id={offer_id}")
        raise HTTPException(status_code=404, detail="Projeto ou Oferta não encontrado")
    
    calendar_service = CalendarService(country_code='BR')
    weeks = calendar_service.get_weekly_breakdown(project.start_date, project.duration_months)
    
    allocations_added = []
    
    for item in offer.items:
        professionals_to_allocate = []
        
        if item.professional_id:
            prof = db.query(models.Professional).filter(models.Professional.id == item.professional_id).first()
            if prof:
                professionals_to_allocate.append(prof)
        else:
            vacancies = db.query(models.Professional).filter(
                models.Professional.role == item.role,
                models.Professional.level == item.level,
                models.Professional.is_vacancy == True
            ).limit(item.quantity).all()
            
            needed = item.quantity
            current = len(vacancies)
            
            if current < needed:
                for i in range(needed - current):
                    new_vacancy = models.Professional(
                        pid=f"VAC-{uuid.uuid4().hex[:8].upper()}",
                        name=f"Vaga {item.role} {item.level} {i+1}",
                        role=item.role,
                        level=item.level,
                        is_vacancy=True,
                        hourly_cost=100.0  # Default cost
                    )
                    db.add(new_vacancy)
                    db.flush()
                    vacancies.append(new_vacancy)
            
            professionals_to_allocate.extend(vacancies[:needed])
        
        for professional in professionals_to_allocate:
            existing = db.query(models.ProjectAllocation).filter(
                models.ProjectAllocation.project_id == project.id,
                models.ProjectAllocation.professional_id == professional.id
            ).first()
            
            if existing:
                continue
            
            margin_rate = project.margin_rate / 100.0 if project.margin_rate > 1 else project.margin_rate
            divisor = 1 - margin_rate
            if divisor <= 0:
                selling_rate = professional.hourly_cost
            else:
                selling_rate = professional.hourly_cost / divisor
            
            db_alloc = models.ProjectAllocation(
                project_id=project.id,
                professional_id=professional.id,
                selling_hourly_rate=selling_rate
            )
            db.add(db_alloc)
            db.flush()
            for week in weeks:
                weekly_alloc = models.WeeklyAllocation(
                    allocation_id=db_alloc.id,
                    week_number=week['week_number'],
                    week_start_date=datetime.fromisoformat(week['week_start']).date(),
                    hours_allocated=week['available_hours'] * (item.allocation_percentage / 100.0),
                    available_hours=week['available_hours']
                )
                db.add(weekly_alloc)
            
            allocations_added.append(professional.name)
    
    db.commit()
    logger.info(f"Offer applied successfully: project_id={project_id}, professionals_added={len(allocations_added)}, weeks={len(weeks)}")
    return {"message": "Offer applied", "allocations": allocations_added, "weeks_count": len(weeks)}

@router.get("/projects/{project_id}/calculate_price", response_model=schemas.ProjectPricing)
def calculate_project_price(project_id: int, db: Session = Depends(get_db)):
    logger.info(f"Calculating price for project: id={project_id}")
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        logger.warning(f"Project not found for pricing: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
    pricing_service = PricingService(db)
    try:
        result = pricing_service.calculate_project_pricing(project)
        logger.info(f"Price calculated: project_id={project_id}, total_cost={result['total_cost']:.2f}, final_price={result['final_price']:.2f}")
        return result
    except ValueError as e:
        logger.error(f"Price calculation failed for project {project_id}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/projects/{project_id}/allocation_table")
def get_allocation_table(project_id: int, db: Session = Depends(get_db)):

    
    project = db.query(models.Project).options(
        joinedload(models.Project.allocations)
        .joinedload(models.ProjectAllocation.professional),
        joinedload(models.Project.allocations)
        .joinedload(models.ProjectAllocation.weekly_allocations)
    ).filter(models.Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Get weekly breakdown
    calendar_service = CalendarService(country_code='BR')
    weeks = calendar_service.get_weekly_breakdown(project.start_date, project.duration_months)
    
    # Format allocations
    allocations_data = []
    for allocation in project.allocations:
        weekly_data = {}
        for weekly_alloc in allocation.weekly_allocations:
            weekly_data[weekly_alloc.week_number] = {
                "id": weekly_alloc.id,
                "hours_allocated": weekly_alloc.hours_allocated,
                "available_hours": weekly_alloc.available_hours
            }
        
        allocations_data.append({
            "allocation_id": allocation.id,
            "professional": {
                "id": allocation.professional.id,
                "name": allocation.professional.name,
                "role": allocation.professional.role,
                "level": allocation.professional.level,
                "hourly_cost": allocation.professional.hourly_cost
            },
            "selling_hourly_rate": allocation.selling_hourly_rate,
            "weekly_hours": weekly_data
        })
    
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "start_date": project.start_date.isoformat(),
            "duration_months": project.duration_months
        },
        "weeks": weeks,
        "allocations": allocations_data
    }

@router.put("/projects/{project_id}/allocations")
def update_allocations(project_id: int, updates: List[dict], db: Session = Depends(get_db)):
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
        # Handle allocation-level updates (selling rate)
        allocation_id = update.get("allocation_id")
        if allocation_id:
            selling_rate = update.get("selling_hourly_rate")
            if selling_rate is not None:
                allocation = db.query(models.ProjectAllocation).filter(
                    models.ProjectAllocation.id == allocation_id
                ).first()
                if allocation:
                    allocation.selling_hourly_rate = selling_rate
                    updated_count += 1
        
        # Handle weekly allocation updates (hours)
        weekly_alloc_id = update.get("weekly_allocation_id")
        if weekly_alloc_id:
            hours = update.get("hours_allocated")
            if hours is not None:
                weekly_alloc = db.query(models.WeeklyAllocation).filter(
                    models.WeeklyAllocation.id == weekly_alloc_id
                ).first()
                
                if weekly_alloc:
                    # Validate hours don't exceed available
                    if hours > weekly_alloc.available_hours:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Horas ({hours}) excedem as horas disponíveis ({weekly_alloc.available_hours}) para a semana {weekly_alloc.week_number}"
                        )
                    weekly_alloc.hours_allocated = hours
                    updated_count += 1
    
    db.commit()
    logger.info(f"Allocations updated: project_id={project_id}, items_updated={updated_count}")
    return {"message": f"Updated {updated_count} items", "updated_count": updated_count}


@router.post("/projects/{project_id}/allocations/")
def add_professional_to_project(
    project_id: int, 
    professional_id: int, 
    selling_hourly_rate: float = None,
    db: Session = Depends(get_db)
):
    """
    Manually add a professional to a project.
    Creates ProjectAllocation and WeeklyAllocations for all project weeks.
    """
    logger.info(f"Adding professional to project: project_id={project_id}, professional_id={professional_id}")
    
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        logger.warning(f"Project not found: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    professional = db.query(models.Professional).filter(
        models.Professional.id == professional_id
    ).first()
    if not professional:
        logger.warning(f"Professional not found: id={professional_id}")
        raise HTTPException(status_code=404, detail="Profissional não encontrado")
    
    # Check if already allocated
    existing = db.query(models.ProjectAllocation).filter(
        models.ProjectAllocation.project_id == project_id,
        models.ProjectAllocation.professional_id == professional_id
    ).first()
    if existing:
        logger.warning(f"Professional already allocated: project_id={project_id}, professional_id={professional_id}")
        raise HTTPException(status_code=400, detail="Profissional já alocado neste projeto")
    
    # Calculate selling rate if not provided
    if selling_hourly_rate is None:
        margin_rate = project.margin_rate / 100.0 if project.margin_rate > 1 else project.margin_rate
        divisor = 1 - margin_rate
        if divisor <= 0:
            selling_hourly_rate = professional.hourly_cost
        else:
            selling_hourly_rate = professional.hourly_cost / divisor
    
    # Create allocation
    allocation = models.ProjectAllocation(
        project_id=project_id,
        professional_id=professional_id,
        selling_hourly_rate=selling_hourly_rate
    )
    db.add(allocation)
    db.flush()
    
    # Get weekly breakdown for the project
    calendar_service = CalendarService(country_code='BR')
    weeks = calendar_service.get_weekly_breakdown(project.start_date, project.duration_months)
    
    # Create weekly allocations with 0 hours by default
    for week in weeks:
        weekly_alloc = models.WeeklyAllocation(
            allocation_id=allocation.id,
            week_number=week['week_number'],
            week_start_date=datetime.fromisoformat(week['week_start']).date(),
            hours_allocated=0.0,  # User will fill in hours manually
            available_hours=week['available_hours']
        )
        db.add(weekly_alloc)
    
    db.commit()
    db.refresh(allocation)
    
    logger.info(f"Professional added to project: project_id={project_id}, professional_id={professional_id}, weeks={len(weeks)}")
    
    return {
        "message": "Professional added to project",
        "allocation_id": allocation.id,
        "professional_name": professional.name,
        "selling_hourly_rate": selling_hourly_rate,
        "weeks_created": len(weeks)
    }


@router.delete("/projects/{project_id}/allocations/{allocation_id}")
def remove_professional_from_project(
    project_id: int, 
    allocation_id: int, 
    db: Session = Depends(get_db)
):
    """
    Remove a professional allocation from a project.
    Deletes the ProjectAllocation and all associated WeeklyAllocations (cascade).
    """
    logger.info(f"Removing professional from project: project_id={project_id}, allocation_id={allocation_id}")
    allocation = db.query(models.ProjectAllocation).filter(
        models.ProjectAllocation.id == allocation_id,
        models.ProjectAllocation.project_id == project_id
    ).first()
    
    if not allocation:
        logger.warning(f"Allocation not found for removal: project_id={project_id}, allocation_id={allocation_id}")
        raise HTTPException(status_code=404, detail="Alocação não encontrada")
    
    professional_name = allocation.professional.name
    
    # Delete allocation (weekly allocations will be deleted by cascade)
    db.delete(allocation)
    db.commit()
    
    logger.info(f"Professional removed from project: {professional_name}, allocation_id={allocation_id}")
    
    return {
        "message": f"Professional {professional_name} removed from project",
        "allocation_id": allocation_id
    }


@router.get("/projects/{project_id}/export_excel")
def export_project_excel(project_id: int, db: Session = Depends(get_db)):
    """
    Exporta um projeto completo para arquivo Excel.
    Retorna arquivo .xlsx com informações do projeto, resumo financeiro e tabela de alocação.
    """
    logger.info(f"Exporting project to Excel: id={project_id}")
    # Buscar projeto
    project = db.query(models.Project).options(
        joinedload(models.Project.allocations)
        .joinedload(models.ProjectAllocation.professional),
        joinedload(models.Project.allocations)
        .joinedload(models.ProjectAllocation.weekly_allocations)
    ).filter(models.Project.id == project_id).first()
    
    if not project:
        logger.warning(f"Project not found for Excel export: id={project_id}")
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    # Gerar Excel
    excel_service = ExcelExportService(db)
    excel_file = excel_service.export_project_to_excel(project)
    
    # Criar nome do arquivo com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"projeto_{project.name.replace(' ', '_')}_{timestamp}.xlsx"
    
    # Retornar como download
    logger.info(f"Excel export successful: project_id={project_id}, filename={filename}")
    return StreamingResponse(
        excel_file,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
