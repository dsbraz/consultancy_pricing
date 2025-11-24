from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import logging

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/offers/", response_model=schemas.Offer)
def create_offer(offer: schemas.OfferCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating offer: name={offer.name}, items_count={len(offer.items)}")
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
    logger.info(f"Offer created successfully: id={db_offer.id}, name={db_offer.name}")
    return db_offer

@router.get("/offers/", response_model=List[schemas.Offer])
def read_offers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offers = db.query(models.Offer).order_by(models.Offer.name).offset(skip).limit(limit).all()
    logger.debug(f"Retrieved {len(offers)} offers (skip={skip}, limit={limit})")
    return offers

@router.put("/offers/{offer_id}", response_model=schemas.Offer)
def update_offer(offer_id: int, offer: schemas.OfferUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating offer: id={offer_id}")
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not db_offer:
        logger.warning(f"Offer not found for update: id={offer_id}")
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    
    if offer.name is not None:
        db_offer.name = offer.name
    
    if offer.items is not None:
        db.query(models.OfferItem).filter(models.OfferItem.offer_id == offer_id).delete()
        
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
    logger.info(f"Offer updated successfully: id={offer_id}, items_count={len(db_offer.items)}")
    return db_offer

@router.delete("/offers/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting offer: id={offer_id}")
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not db_offer:
        logger.warning(f"Offer not found for deletion: id={offer_id}")
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    
    db.query(models.OfferItem).filter(models.OfferItem.offer_id == offer_id).delete()
    
    db.delete(db_offer)
    db.commit()
    logger.info(f"Offer deleted successfully: id={offer_id}")
    return {"message": "Offer deleted successfully"}
