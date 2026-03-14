from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database.connection import get_db
from app.schemas.schemas import StockLedgerResponse
from app.services import stock_ledger_service, auth_service
from app.models.models import User

router = APIRouter(prefix="/api/ledger", tags=["ledger"])


@router.get("/all", response_model=list[StockLedgerResponse])
def get_ledger_entries(
    product_id: Optional[int] = Query(None),
    warehouse_id: Optional[int] = Query(None),
    movement_type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get stock ledger entries with optional filters - requires authentication"""
    return stock_ledger_service.get_ledger_entries(
        db, product_id=product_id, warehouse_id=warehouse_id,
        movement_type=movement_type, skip=skip, limit=limit
    )


@router.get("/product/{product_id}", response_model=list[StockLedgerResponse])
def get_product_ledger(
    product_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get stock ledger for a specific product - requires authentication"""
    return stock_ledger_service.get_product_ledger(db, product_id, skip=skip, limit=limit)


@router.get("/warehouse/{warehouse_id}", response_model=list[StockLedgerResponse])
def get_warehouse_ledger(
    warehouse_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get stock ledger for a specific warehouse - requires authentication"""
    return stock_ledger_service.get_warehouse_ledger(db, warehouse_id, skip=skip, limit=limit)
