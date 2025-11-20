from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/templates/", response_model=schemas.Template)
def create_template(template: schemas.TemplateCreate, db: Session = Depends(get_db)):
    db_template = models.Template(name=template.name)
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    
    for item in template.items:
        db_item = models.TemplateItem(
            template_id=db_template.id,
            role=item.role,
            level=item.level,
            quantity=item.quantity,
            allocation_percentage=item.allocation_percentage,
            professional_id=item.professional_id
        )
        db.add(db_item)
        
    db.commit()
    db.refresh(db_template)
    return db_template

@router.get("/templates/", response_model=List[schemas.Template])
def read_templates(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    templates = db.query(models.Template).offset(skip).limit(limit).all()
    return templates

@router.put("/templates/{template_id}", response_model=schemas.Template)
def update_template(template_id: int, template: schemas.TemplateUpdate, db: Session = Depends(get_db)):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Update name if provided
    if template.name is not None:
        db_template.name = template.name
    
    # Update items if provided
    if template.items is not None:
        # Delete existing items
        db.query(models.TemplateItem).filter(models.TemplateItem.template_id == template_id).delete()
        
        # Add new items
        for item in template.items:
            db_item = models.TemplateItem(
                template_id=db_template.id,
                role=item.role,
                level=item.level,
                quantity=item.quantity,
                allocation_percentage=item.allocation_percentage,
                professional_id=item.professional_id
            )
            db.add(db_item)
    
    db.commit()
    db.refresh(db_template)
    return db_template

@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    db_template = db.query(models.Template).filter(models.Template.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Delete template items first (cascade should handle this, but being explicit)
    db.query(models.TemplateItem).filter(models.TemplateItem.template_id == template_id).delete()
    
    db.delete(db_template)
    db.commit()
    return {"message": "Template deleted successfully"}
