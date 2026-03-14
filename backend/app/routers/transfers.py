from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import TransferCreate, TransferResponse, MessageResponse
from app.services import transfer_service

router = APIRouter(prefix="/api/transfers", tags=["transfers"])


@router.post("/transfer", response_model=MessageResponse)
def transfer_stock(transfer: TransferCreate, db: Session = Depends(get_db)):
    try:
        transfer_service.create_transfer(db, transfer)
        return MessageResponse(message="Stock Transferred Successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[TransferResponse])
def get_transfers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return transfer_service.get_transfers(db, skip=skip, limit=limit)
