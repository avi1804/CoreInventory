from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.schemas.schemas import ReceiptCreate, ReceiptUpdate, ReceiptResponse, MessageResponse
from app.services import receipt_service

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


@router.post("/add", response_model=MessageResponse)
def add_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db)):
    try:
        receipt_service.create_receipt(db, receipt)
        return MessageResponse(message="Receipt Added & Stock Updated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[ReceiptResponse])
def get_receipts(
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = Query(None, description="Filter by status: draft, waiting, ready, done, canceled"),
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse"),
    db: Session = Depends(get_db)
):
    return receipt_service.get_receipts(db, skip=skip, limit=limit, status=status, warehouse_id=warehouse_id)


@router.put("/status/{receipt_id}", response_model=MessageResponse)
def update_receipt_status(receipt_id: int, update: ReceiptUpdate, db: Session = Depends(get_db)):
    """Update receipt status: draft -> waiting -> ready -> done"""
    receipt = receipt_service.update_receipt_status(db, receipt_id, update.status)
    if not receipt:
        raise HTTPException(status_code=400, detail="Invalid status transition or receipt not found")
    return MessageResponse(message=f"Receipt status updated to {update.status}")
