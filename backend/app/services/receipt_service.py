from sqlalchemy.orm import Session
from app.models.models import Receipt
from app.schemas.schemas import ReceiptCreate
from app.services.stock_service import update_stock_quantity


def create_receipt(db: Session, receipt: ReceiptCreate) -> Receipt:
    db_receipt = Receipt(
        product_id=receipt.product_id,
        warehouse_id=receipt.warehouse_id,
        quantity=receipt.quantity
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    
    # Update stock quantity
    update_stock_quantity(db, receipt.product_id, receipt.warehouse_id, receipt.quantity)
    
    return db_receipt


def get_receipts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Receipt).offset(skip).limit(limit).all()
