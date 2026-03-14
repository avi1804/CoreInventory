from sqlalchemy.orm import Session
from app.models.models import Transfer
from app.schemas.schemas import TransferCreate
from app.services.stock_service import update_stock_quantity


def create_transfer(db: Session, transfer: TransferCreate) -> Transfer:
    db_transfer = Transfer(
        product_id=transfer.product_id,
        from_warehouse=transfer.from_warehouse,
        to_warehouse=transfer.to_warehouse,
        quantity=transfer.quantity
    )
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    
    # Decrease stock from source warehouse
    update_stock_quantity(db, transfer.product_id, transfer.from_warehouse, -transfer.quantity)
    
    # Increase stock to destination warehouse
    update_stock_quantity(db, transfer.product_id, transfer.to_warehouse, transfer.quantity)
    
    return db_transfer


def get_transfers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transfer).offset(skip).limit(limit).all()
