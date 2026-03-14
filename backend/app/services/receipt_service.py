from sqlalchemy.orm import Session
from app.models.models import Receipt
from app.schemas.schemas import ReceiptCreate, StockLedgerCreate
from app.services.stock_service import update_stock_quantity
from app.services.stock_ledger_service import create_ledger_entry


def create_receipt(db: Session, receipt: ReceiptCreate) -> Receipt:
    """Create receipt in draft status - stock updated only on validation"""
    db_receipt = Receipt(
        product_id=receipt.product_id,
        warehouse_id=receipt.warehouse_id,
        quantity=receipt.quantity,
        supplier=receipt.supplier,
        status="draft"
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return db_receipt


def validate_receipt(db: Session, receipt_id: int) -> Receipt:
    """Validate receipt and update stock - only called when status moves to 'done'"""
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        return None
    
    if receipt.status == "done":
        return receipt  # Already validated
    
    # Update stock quantity
    updated_stock = update_stock_quantity(db, receipt.product_id, receipt.warehouse_id, receipt.quantity)
    
    # Create ledger entry
    ledger_entry = StockLedgerCreate(
        product_id=receipt.product_id,
        warehouse_id=receipt.warehouse_id,
        movement_type="receipt",
        quantity=receipt.quantity,
        reference_id=receipt.id,
        reference_type="receipt",
        balance_after=updated_stock.quantity
    )
    create_ledger_entry(db, ledger_entry)
    
    receipt.status = "done"
    db.commit()
    db.refresh(receipt)
    return receipt


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
    
    # When transitioning to done, validate and update stock
    if new_status == "done":
        if current_status != "ready":
            return None  # Can only mark as done from ready
        return validate_receipt(db, receipt_id)
    
    receipt.status = new_status
    db.commit()
    db.refresh(receipt)
    return receipt
