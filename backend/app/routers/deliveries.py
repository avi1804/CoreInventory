from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.schemas.schemas import DeliveryCreate, DeliveryUpdate, DeliveryResponse, MessageResponse
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
def get_deliveries(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = Query(None, description="Filter by status: draft, waiting, ready, done, canceled"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    db: Session = Depends(get_db)
):
    return delivery_service.get_deliveries(db, skip=skip, limit=limit, status=status, warehouse_id=warehouse_id)


@router.put("/status/{delivery_id}", response_model=MessageResponse)
def update_delivery_status(delivery_id: int, update: DeliveryUpdate, db: Session = Depends(get_db)):
    """Update delivery status: draft -> waiting -> ready -> done"""
    delivery = delivery_service.update_delivery_status(db, delivery_id, update.status)
    if not delivery:
        raise HTTPException(status_code=400, detail="Invalid status transition or delivery not found")
    return MessageResponse(message=f"Delivery status updated to {update.status}")
