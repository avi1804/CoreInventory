from sqlalchemy.orm import Session
from app.models.models import Transfer
from app.schemas.schemas import TransferCreate, StockLedgerCreate
from app.services.stock_service import update_stock_quantity
from app.services.stock_ledger_service import create_ledger_entry


def create_transfer(db: Session, transfer: TransferCreate) -> Transfer:
    """Create transfer in draft status - stock updated only on validation"""
    db_transfer = Transfer(
        product_id=transfer.product_id,
        from_warehouse=transfer.from_warehouse,
        to_warehouse=transfer.to_warehouse,
        quantity=transfer.quantity,
        status="draft"
    )
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer


def validate_transfer(db: Session, transfer_id: int) -> Transfer:
    """Validate transfer and update stock - only called when status moves to 'done'"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        return None
    
    if transfer.status == "done":
        return transfer  # Already validated
    
    # Decrease stock from source warehouse
    from_stock = update_stock_quantity(db, transfer.product_id, transfer.from_warehouse, -transfer.quantity)
    
    # Increase stock to destination warehouse
    to_stock = update_stock_quantity(db, transfer.product_id, transfer.to_warehouse, transfer.quantity)
    
    # Create ledger entries for both warehouses
    # Outgoing from source
    ledger_out = StockLedgerCreate(
        product_id=transfer.product_id,
        warehouse_id=transfer.from_warehouse,
        movement_type="transfer_out",
        quantity=-transfer.quantity,
        reference_id=transfer.id,
        reference_type="transfer",
        balance_after=from_stock.quantity
    )
    create_ledger_entry(db, ledger_out)
    
    # Incoming to destination
    ledger_in = StockLedgerCreate(
        product_id=transfer.product_id,
        warehouse_id=transfer.to_warehouse,
        movement_type="transfer_in",
        quantity=transfer.quantity,
        reference_id=transfer.id,
        reference_type="transfer",
        balance_after=to_stock.quantity
    )
    create_ledger_entry(db, ledger_in)
    
    transfer.status = "done"
    db.commit()
    db.refresh(transfer)
    return transfer


def get_transfers(db: Session, skip: int = 0, limit: int = 100, status: str = None, from_warehouse: int = None, to_warehouse: int = None):
    query = db.query(Transfer)
    if status:
        query = query.filter(Transfer.status == status)
    if from_warehouse:
        query = query.filter(Transfer.from_warehouse == from_warehouse)
    if to_warehouse:
        query = query.filter(Transfer.to_warehouse == to_warehouse)
    return query.order_by(Transfer.created_at.desc()).offset(skip).limit(limit).all()


def update_transfer_status(db: Session, transfer_id: int, new_status: str) -> Transfer:
    """Update transfer status with workflow validation"""
    valid_statuses = ["draft", "waiting", "ready", "done", "canceled"]
    if new_status not in valid_statuses:
        return None
    
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        return None
    
    current_status = transfer.status
    
    if new_status == "canceled" and current_status == "done":
        return None
    
    # When transitioning to done, validate and update stock
    if new_status == "done":
        if current_status != "ready":
            return None
        return validate_transfer(db, transfer_id)
    
    transfer.status = new_status
    db.commit()
    db.refresh(transfer)
    return transfer
