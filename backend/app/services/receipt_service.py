from sqlalchemy.orm import Session
from app.models.models import Receipt
from app.schemas.schemas import ReceiptCreate, StockLedgerCreate
from app.services.stock_service import update_stock_quantity
from app.services.stock_ledger_service import create_ledger_entry


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
    updated_stock = update_stock_quantity(db, receipt.product_id, receipt.warehouse_id, receipt.quantity)
    
    # Create ledger entry
    ledger_entry = StockLedgerCreate(
        product_id=receipt.product_id,
        warehouse_id=receipt.warehouse_id,
        movement_type="receipt",
        quantity=receipt.quantity,
        reference_id=db_receipt.id,
        reference_type="receipt",
        balance_after=updated_stock.quantity
    )
    create_ledger_entry(db, ledger_entry)
    
    return db_receipt


def get_receipts(db: Session, skip: int = 0, limit: int = 100, status: str = None, warehouse_id: int = None):
    query = db.query(Receipt)
    if status:
        query = query.filter(Receipt.status == status)
    if warehouse_id:
        query = query.filter(Receipt.warehouse_id == warehouse_id)
    return query.order_by(Receipt.created_at.desc()).offset(skip).limit(limit).all()


def update_receipt_status(db: Session, receipt_id: int, new_status: str) -> Receipt:
    """Update receipt status with workflow validation"""
    valid_statuses = ["draft", "waiting", "ready", "done", "canceled"]
    if new_status not in valid_statuses:
        return None
    
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        return None
    
    # Workflow: draft -> waiting -> ready -> done
    # Can cancel from any status except done
    current_status = receipt.status
    
    if new_status == "canceled" and current_status == "done":
        return None  # Cannot cancel completed receipts
    
    if new_status == "done" and current_status != "ready":
        return None  # Can only mark as done from ready
    
    receipt.status = new_status
    db.commit()
    db.refresh(receipt)
    return receipt
