from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import DashboardKPIs, ProductResponse
from app.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/kpis", response_model=DashboardKPIs)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    """Get dashboard KPIs and statistics"""
    try:
        kpis = dashboard_service.get_dashboard_kpis(db)
        return DashboardKPIs(**kpis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/low-stock", response_model=list[ProductResponse])
def get_low_stock_products(threshold: int = 10, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get products with low stock (below threshold)"""
    products = dashboard_service.get_low_stock_products(db, threshold, skip, limit)
    return [p[0] for p in products]  # Extract Product from tuple (Product, Stock)


@router.get("/out-of-stock", response_model=list[ProductResponse])
def get_out_of_stock_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get products that are out of stock"""
    return dashboard_service.get_out_of_stock_products(db, skip, limit)
