from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import StockAdjustmentCreate, StockAdjustmentResponse, MessageResponse
from app.services import adjustment_service

router = APIRouter(prefix="/api/adjustments", tags=["adjustments"])


@router.post("/add", response_model=MessageResponse)
def add_adjustment(adjustment: StockAdjustmentCreate, db: Session = Depends(get_db)):
    try:
        adjustment_service.create_adjustment(db, adjustment)
        return MessageResponse(message="Stock Adjustment Created & Stock Updated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[StockAdjustmentResponse])
def get_adjustments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return adjustment_service.get_adjustments(db, skip=skip, limit=limit)


@router.get("/product/{product_id}", response_model=list[StockAdjustmentResponse])
def get_adjustments_by_product(product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return adjustment_service.get_adjustments_by_product(db, product_id, skip=skip, limit=limit)


@router.get("/warehouse/{warehouse_id}", response_model=list[StockAdjustmentResponse])
def get_adjustments_by_warehouse(warehouse_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return adjustment_service.get_adjustments_by_warehouse(db, warehouse_id, skip=skip, limit=limit)
