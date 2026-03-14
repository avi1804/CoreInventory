from sqlalchemy.orm import Session
from app.models.models import Transfer
from app.schemas.schemas import TransferCreate, StockLedgerCreate
from app.services.stock_service import update_stock_quantity
from app.services.stock_ledger_service import create_ledger_entry


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
        reference_id=db_transfer.id,
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
        reference_id=db_transfer.id,
        reference_type="transfer",
        balance_after=to_stock.quantity
    )
    create_ledger_entry(db, ledger_in)
    
    return db_transfer


def get_transfers(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transfer).offset(skip).limit(limit).all()
