from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import WarehouseCreate, WarehouseUpdate, WarehouseResponse, MessageResponse
from app.services import warehouse_service, auth_service
from app.models.models import User

router = APIRouter(prefix="/api/warehouses", tags=["warehouses"])


@router.post("/add", response_model=MessageResponse)
def add_warehouse(
    warehouse: WarehouseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Add a new warehouse - requires authentication"""
    try:
        warehouse_service.create_warehouse(db, warehouse)
        return MessageResponse(message="Warehouse Added")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[WarehouseResponse])
def get_warehouses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get all warehouses - requires authentication"""
    return warehouse_service.get_warehouses(db, skip=skip, limit=limit)


@router.put("/update/{warehouse_id}", response_model=MessageResponse)
def update_warehouse(
    warehouse_id: int,
    warehouse: WarehouseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update a warehouse - requires authentication"""
    updated = warehouse_service.update_warehouse(db, warehouse_id, warehouse)
    if not updated:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return MessageResponse(message="Warehouse Updated")


@router.delete("/delete/{warehouse_id}", response_model=MessageResponse)
def delete_warehouse(
    warehouse_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Delete a warehouse - requires authentication"""
    deleted = warehouse_service.delete_warehouse(db, warehouse_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return MessageResponse(message="Warehouse Deleted")
