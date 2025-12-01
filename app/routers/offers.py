from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from typing import List
import logging

from app.database import get_db
from app.models import models
from app.schemas import schemas

router = APIRouter()
logger = logging.getLogger(__name__)


def _get_offer_or_404(db: Session, offer_id: int) -> models.Offer:
    """Fetch offer or raise 404."""
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


def _get_offer_item_or_404(
    db: Session, offer_id: int, item_id: int
) -> models.OfferItem:
    """Fetch offer item scoped to offer or raise 404."""
    item = (
        db.query(models.OfferItem)
        .filter(models.OfferItem.id == item_id, models.OfferItem.offer_id == offer_id)
        .first()
    )
    if not item:
        logger.warning(f"Offer item not found: offer_id={offer_id}, item_id={item_id}")
        raise HTTPException(status_code=404, detail="Item não encontrado")
    return item


@router.post(
    "/offers/",
    response_model=schemas.Offer,
    responses={400: {"model": schemas.ErrorResponse}},
)
def create_offer(offer: schemas.OfferCreate, db: Session = Depends(get_db)):
    """Create a new offer template"""
    logger.info(f"Creating offer: name={offer.name}, items_count={len(offer.items)}")
    try:
        db_offer = models.Offer(name=offer.name)
        db.add(db_offer)
        db.flush()  # Flush to get ID

        for item in offer.items:
            # Ensure referenced professional exists
            _get_professional_or_404(db, item.professional_id)

            db_item = models.OfferItem(
                offer_id=db_offer.id,
                allocation_percentage=item.allocation_percentage,
                professional_id=item.professional_id,
            )
            db.add(db_item)

        db.commit()
        db.refresh(db_offer)
        # Ensure items are loaded for the response payload
        _ = db_offer.items
        logger.info(
            f"Offer created successfully: id={db_offer.id}, name={db_offer.name}"
        )
        return db_offer
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating offer: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Erro ao criar oferta: {str(e)}")


@router.get("/offers/", response_model=List[schemas.Offer])
def read_offers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all offer templates"""
    offers = (
        db.query(models.Offer)
        .options(joinedload(models.Offer.items))
        .order_by(func.lower(models.Offer.name))
        .offset(skip)
        .limit(limit)
        .all()
    )
    logger.debug(f"Retrieved {len(offers)} offers (skip={skip}, limit={limit})")
    return offers


@router.get(
    "/offers/{offer_id}",
    response_model=schemas.Offer,
    responses={404: {"model": schemas.ErrorResponse}},
)
def read_offer(offer_id: int, db: Session = Depends(get_db)):
    """Get a single offer template by ID"""
    return _get_offer_or_404(db, offer_id)


@router.patch(
    "/offers/{offer_id}",
    response_model=schemas.Offer,
    responses={404: {"model": schemas.ErrorResponse}},
)
def update_offer(
    offer_id: int, offer: schemas.OfferUpdate, db: Session = Depends(get_db)
):
    """Update an offer template's details"""
    logger.info(f"Updating offer: id={offer_id}")
    db_offer = _get_offer_or_404(db, offer_id)

    if offer.name is not None:
        db_offer.name = offer.name

    db.commit()
    db.refresh(db_offer)
    # Ensure items relationship is available in the serialized response
    _ = db_offer.items
    logger.info(f"Offer updated successfully: id={offer_id}")
    return db_offer


@router.post(
    "/offers/{offer_id}/items",
    response_model=schemas.OfferItem,
    responses={404: {"model": schemas.ErrorResponse}},
)
def add_item_to_offer(
    offer_id: int, item: schemas.OfferItemCreate, db: Session = Depends(get_db)
):
    """Add a new item to an offer"""
    _get_offer_or_404(db, offer_id)

    # Ensure referenced professional exists
    _get_professional_or_404(db, item.professional_id)

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


@router.patch(
    "/offers/{offer_id}/items/{item_id}",
    response_model=schemas.OfferItem,
    responses={404: {"model": schemas.ErrorResponse}},
)
def update_offer_item(
    offer_id: int,
    item_id: int,
    item: schemas.OfferItemUpdate,
    db: Session = Depends(get_db),
):
    """Update a specific item in an offer"""
    db_item = _get_offer_item_or_404(db, offer_id, item_id)

    if item.professional_id is not None:
        _get_professional_or_404(db, item.professional_id)
        db_item.professional_id = item.professional_id
    if item.allocation_percentage is not None:
        db_item.allocation_percentage = item.allocation_percentage

    db.commit()
    db.refresh(db_item)
    logger.info(f"Item updated: offer_id={offer_id}, item_id={item_id}")
    return db_item


@router.delete(
    "/offers/{offer_id}/items/{item_id}",
    responses={404: {"model": schemas.ErrorResponse}},
)
def delete_offer_item(offer_id: int, item_id: int, db: Session = Depends(get_db)):
    """Remove a specific item from an offer"""
    db_item = _get_offer_item_or_404(db, offer_id, item_id)
    db.delete(db_item)
    db.commit()
    logger.info(f"Item deleted: offer_id={offer_id}, item_id={item_id}")
    return {"message": "Item excluído com sucesso", "item_id": item_id}


@router.delete(
    "/offers/{offer_id}",
    responses={
        404: {"model": schemas.ErrorResponse},
        409: {"model": schemas.ErrorResponse},
    },
)
def delete_offer(offer_id: int, db: Session = Depends(get_db)):
    """Delete an offer template"""
    logger.info(f"Deleting offer: id={offer_id}")
    db_offer = _get_offer_or_404(db, offer_id)

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
            status_code=409,
            detail="Não é possível excluir esta oferta pois ela está sendo usada.",
        )

    logger.info(f"Offer deleted successfully: id={offer_id}")
    return {"message": "Oferta excluída com sucesso", "offer_id": offer_id}
