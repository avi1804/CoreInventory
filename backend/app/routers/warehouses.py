from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import WarehouseCreate, WarehouseResponse, MessageResponse
from app.services import warehouse_service

router = APIRouter(prefix="/api/warehouses", tags=["warehouses"])


@router.post("/add", response_model=MessageResponse)
def add_warehouse(warehouse: WarehouseCreate, db: Session = Depends(get_db)):
    try:
        warehouse_service.create_warehouse(db, warehouse)
        return MessageResponse(message="Warehouse Added")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[WarehouseResponse])
def get_warehouses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return warehouse_service.get_warehouses(db, skip=skip, limit=limit)
