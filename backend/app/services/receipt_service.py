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


def get_receipts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Receipt).offset(skip).limit(limit).all()
