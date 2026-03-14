from sqlalchemy.orm import Session
from app.models.models import Warehouse
from app.schemas.schemas import WarehouseCreate, WarehouseUpdate


def create_warehouse(db: Session, warehouse: WarehouseCreate) -> Warehouse:
    db_warehouse = Warehouse(
        name=warehouse.name,
        location=warehouse.location
    )
    db.add(db_warehouse)
    db.commit()
    db.refresh(db_warehouse)
    return db_warehouse


def get_warehouse(db: Session, warehouse_id: int) -> Warehouse:
    return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()


def get_warehouses(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Warehouse).offset(skip).limit(limit).all()


def update_warehouse(db: Session, warehouse_id: int, warehouse: WarehouseUpdate) -> Warehouse:
    db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if db_warehouse:
        db_warehouse.name = warehouse.name
        db_warehouse.location = warehouse.location
        db.commit()
        db.refresh(db_warehouse)
    return db_warehouse


def delete_warehouse(db: Session, warehouse_id: int) -> bool:
    db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if db_warehouse:
        db.delete(db_warehouse)
        db.commit()
        return True
    return False
