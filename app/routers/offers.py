from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
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
            allocation_percentage=item.allocation_percentage,
            professional_id=item.professional_id,
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_offer)
    logger.info(f"Offer created successfully: id={db_offer.id}, name={db_offer.name}")
    return db_offer


@router.get("/offers/", response_model=List[schemas.Offer])
def read_offers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    offers = (
        db.query(models.Offer)
        .order_by(func.lower(models.Offer.name))
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.debug(f"Retrieved {len(offers)} offers (skip={skip}, limit={limit})")
    return offers


@router.get("/offers/{offer_id}", response_model=schemas.Offer)
def read_offer(offer_id: int, db: Session = Depends(get_db)):
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")
    return offer


@router.put("/offers/{offer_id}", response_model=schemas.Offer)
def update_offer(
    offer_id: int, offer: schemas.OfferUpdate, db: Session = Depends(get_db)
):
    logger.info(f"Updating offer: id={offer_id}")
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not db_offer:
        logger.warning(f"Offer not found for update: id={offer_id}")
        raise HTTPException(status_code=404, detail="Oferta não encontrada")

    if offer.name is not None:
        db_offer.name = offer.name

    db.commit()
    db.refresh(db_offer)
    logger.info(f"Offer updated successfully: id={offer_id}")
    return db_offer


@router.get("/offers/{offer_id}/items", response_model=List[schemas.OfferItem])
def get_offer_items(offer_id: int, db: Session = Depends(get_db)):
    """Get all items from an offer"""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")

    return offer.items


@router.post("/offers/{offer_id}/items", response_model=schemas.OfferItem)
def add_item_to_offer(
    offer_id: int, item: schemas.OfferItemCreate, db: Session = Depends(get_db)
):
    """Add a new item to an offer"""
    offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not offer:
        raise HTTPException(status_code=404, detail="Oferta não encontrada")

    db_item = models.OfferItem(
        offer_id=offer_id,
        allocation_percentage=item.allocation_percentage,
        professional_id=item.professional_id,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    logger.info(f"Item added to offer: offer_id={offer_id}, item_id={db_item.id}")
    return db_item


@router.put("/offers/{offer_id}/items/{item_id}", response_model=schemas.OfferItem)
def update_offer_item(
    offer_id: int,
    item_id: int,
    item: schemas.OfferItemUpdate,
    db: Session = Depends(get_db),
):
    """Update a specific item in an offer"""
    db_item = (
        db.query(models.OfferItem)
        .filter(models.OfferItem.id == item_id, models.OfferItem.offer_id == offer_id)
        .first()
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    if item.professional_id is not None:
        db_item.professional_id = item.professional_id
    if item.allocation_percentage is not None:
        db_item.allocation_percentage = item.allocation_percentage

    db.commit()
    db.refresh(db_item)
    logger.info(f"Item updated: offer_id={offer_id}, item_id={item_id}")
    return db_item


@router.delete("/offers/{offer_id}/items/{item_id}")
def delete_offer_item(offer_id: int, item_id: int, db: Session = Depends(get_db)):
    """Remove a specific item from an offer"""
    db_item = (
        db.query(models.OfferItem)
        .filter(models.OfferItem.id == item_id, models.OfferItem.offer_id == offer_id)
        .first()
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Item não encontrado")

    db.delete(db_item)
    db.commit()
    logger.info(f"Item deleted: offer_id={offer_id}, item_id={item_id}")
    return {"message": "Item deleted successfully"}


@router.delete("/offers/{offer_id}")
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting offer: id={offer_id}")
    db_offer = db.query(models.Offer).filter(models.Offer.id == offer_id).first()
    if not db_offer:
        logger.warning(f"Offer not found for deletion: id={offer_id}")
        raise HTTPException(status_code=404, detail="Oferta não encontrada")

    try:
        db.query(models.OfferItem).filter(
            models.OfferItem.offer_id == offer_id
        ).delete()

        db.delete(db_offer)
        db.commit()
    except IntegrityError:
        db.rollback()
        logger.warning(
            f"Integrity error deleting offer: id={offer_id} (likely referenced by other records)"
        )
        raise HTTPException(
            status_code=400,
            detail="Não é possível excluir esta oferta pois ela está sendo usada.",
        )

    logger.info(f"Offer deleted successfully: id={offer_id}")
    return {"message": "Offer deleted successfully"}
