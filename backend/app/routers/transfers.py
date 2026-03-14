from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.schemas.schemas import TransferCreate, TransferUpdate, TransferResponse, MessageResponse
from app.services import transfer_service, auth_service
from app.models.models import User

router = APIRouter(prefix="/api/transfers", tags=["transfers"])


@router.post("/transfer", response_model=MessageResponse)
def transfer_stock(
    transfer: TransferCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Create a transfer - requires authentication"""
    try:
        transfer_service.create_transfer(db, transfer)
        return MessageResponse(message="Transfer Created")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[TransferResponse])
def get_transfers(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, description="Filter by status: draft, waiting, ready, done, canceled"),
    from_warehouse: Optional[int] = Query(None, description="Filter by source warehouse"),
    to_warehouse: Optional[int] = Query(None, description="Filter by destination warehouse"),
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get all transfers - requires authentication"""
    return transfer_service.get_transfers(db, skip=skip, limit=limit, status=status, from_warehouse=from_warehouse, to_warehouse=to_warehouse)


@router.put("/status/{transfer_id}", response_model=MessageResponse)
def update_transfer_status(
    transfer_id: int,
    update: TransferUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update transfer status: draft -> waiting -> ready -> done - requires authentication"""
    transfer = transfer_service.update_transfer_status(db, transfer_id, update.status)
    if not transfer:
        raise HTTPException(status_code=400, detail="Invalid status transition or transfer not found")
    return MessageResponse(message=f"Transfer status updated to {update.status}")


@router.post("/validate/{transfer_id}", response_model=MessageResponse)
def validate_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Validate transfer and update stock - transitions from ready -> done - requires authentication"""
    transfer = transfer_service.validate_transfer(db, transfer_id)
    if not transfer:
        raise HTTPException(status_code=400, detail="Transfer not found or already validated")
    return MessageResponse(message="Transfer validated and stock updated")
