from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import StockCreate, StockResponse, MessageResponse
from app.services import stock_service, auth_service
from app.models.models import User

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.post("/add", response_model=MessageResponse)
def add_stock(
    stock: StockCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Add stock - requires authentication"""
    try:
        stock_service.create_stock(db, stock)
        return MessageResponse(message="Stock Added")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[StockResponse])
def get_stock(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get all stock - requires authentication"""
    return stock_service.get_all_stock(db, skip=skip, limit=limit)
