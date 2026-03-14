from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Union
from app.database.connection import get_db
from app.schemas.schemas import ProductResponse, StockResponse, ReceiptResponse, DeliveryResponse, TransferResponse, StockAdjustmentResponse
from app.services import search_service, auth_service
from app.models.models import User

router = APIRouter(prefix="/api/search", tags=["search"])


@router.get("/products", response_model=list[ProductResponse])
def search_products(
    q: Optional[str] = Query(None, description="Search query for name, SKU, or category"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Search products by name, SKU, or category - requires authentication"""
    return search_service.search_products(db, query=q, category=category, skip=skip, limit=limit)


@router.get("/stock", response_model=list[StockResponse])
def filter_stock(
    warehouse_id: Optional[int] = Query(None, description="Filter by warehouse ID"),
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Filter stock by warehouse and/or product - requires authentication"""
    return search_service.filter_stock_by_warehouse(db, warehouse_id, product_id, skip, limit)


@router.get("/movements/{movement_type}")
def get_movements_by_type(
    movement_type: str,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get movements by type: receipt, delivery, transfer, adjustment - requires authentication"""
    valid_types = ["receipt", "delivery", "transfer", "adjustment"]
    if movement_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid type. Must be one of: {valid_types}")

    return search_service.get_movements_by_type(db, movement_type, skip, limit)


@router.get("/categories", response_model=list[str])
def get_categories(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get all unique product categories - requires authentication"""
    return search_service.get_categories(db)


@router.get("/product-stock/{product_id}", response_model=list[StockResponse])
def get_product_stock_by_warehouse(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get stock of a product across all warehouses - requires authentication"""
    return search_service.get_product_stock_by_warehouse(db, product_id)
