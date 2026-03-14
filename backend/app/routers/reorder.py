from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import ReorderAlert, MessageResponse
from app.services import reorder_service

router = APIRouter(prefix="/api/reorder", tags=["reordering"])


@router.get("/alerts", response_model=list[ReorderAlert])
def get_reorder_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get products that need reordering (stock below reorder_point)"""
    return reorder_service.get_reorder_alerts(db, skip=skip, limit=limit)


@router.get("/critical", response_model=list[ReorderAlert])
def get_critical_stock(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get products below minimum stock level (critical)"""
    return reorder_service.get_products_below_min_stock(db, skip=skip, limit=limit)


@router.put("/rules/{product_id}", response_model=MessageResponse)
def update_reorder_rules(
    product_id: int,
    min_stock: int = None,
    max_stock: int = None,
    reorder_point: int = None,
    db: Session = Depends(get_db)
):
    """Update reordering rules for a product"""
    product = reorder_service.update_product_reorder_rules(db, product_id, min_stock, max_stock, reorder_point)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return MessageResponse(message="Reorder rules updated successfully")
