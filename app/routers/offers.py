from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()

@router.post("/offers/", response_model=schemas.Offer)
def create_offer(offer: schemas.OfferCreate, db: Session = Depends(get_db)):
    db_offer = models.Offer(name=offer.name)
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    
    for item in offer.items:
        db_item = models.OfferItem(
            offer_id=db_offer.id,
            role=item.role,
            level=item.level,
            quantity=item.quantity,
            allocation_percentage=item.allocation_percentage,
            professional_id=item.professional_id
        )
        db.add(db_item)
        
    db.commit()
    db.refresh(db_offer)
    return db_offer

@router.get("/offers/", response_model=List[schemas.Offer])
def read_offers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offers = db.query(models.Offer).offset(skip).limit(limit).all()
    return offers

@router.put("/offers/{offer_id}", response_model=schemas.Offer)
def update_offer(offer_id: int, offer: schemas.OfferUpdate, db: Session = Depends(get_db)):
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    
    # Update name if provided
    if offer.name is not None:
        db_offer.name = offer.name
    
    # Update items if provided
    if offer.items is not None:
        # Delete existing items
        db.query(models.OfferItem).filter(models.OfferItem.offer_id == offer_id).delete()
        
        # Add new items
        for item in offer.items:
            db_item = models.OfferItem(
                offer_id=db_offer.id,
                role=item.role,
                level=item.level,
                quantity=item.quantity,
                allocation_percentage=item.allocation_percentage,
                professional_id=item.professional_id
            )
            db.add(db_item)
    
    db.commit()
    db.refresh(db_offer)
    return db_offer

@router.delete("/offers/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not db_offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    
    # Delete offer items first (cascade should handle this, but being explicit)
    db.query(models.OfferItem).filter(models.OfferItem.offer_id == offer_id).delete()
    
    db.delete(db_offer)
    db.commit()
    return {"message": "Offer deleted successfully"}
