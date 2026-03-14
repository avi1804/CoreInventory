from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import ReceiptCreate, ReceiptResponse, MessageResponse
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
def get_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return receipt_service.get_receipts(db, skip=skip, limit=limit)
