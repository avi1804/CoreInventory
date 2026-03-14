from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import DeliveryCreate, DeliveryResponse, MessageResponse
from app.services import delivery_service

router = APIRouter(prefix="/api/deliveries", tags=["deliveries"])


@router.post("/add", response_model=MessageResponse)
def add_delivery(delivery: DeliveryCreate, db: Session = Depends(get_db)):
    try:
        delivery_service.create_delivery(db, delivery)
        return MessageResponse(message="Delivery Added & Stock Updated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[DeliveryResponse])
def get_deliveries(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return delivery_service.get_deliveries(db, skip=skip, limit=limit)
