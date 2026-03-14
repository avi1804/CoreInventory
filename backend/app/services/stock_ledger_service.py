from sqlalchemy.orm import Session
from app.models.models import StockLedger
from app.schemas.schemas import StockLedgerCreate


def create_ledger_entry(db: Session, ledger: StockLedgerCreate) -> StockLedger:
    db_ledger = StockLedger(
        product_id=ledger.product_id,
        warehouse_id=ledger.warehouse_id,
        movement_type=ledger.movement_type,
        quantity=ledger.quantity,
        reference_id=ledger.reference_id,
        reference_type=ledger.reference_type,
        balance_after=ledger.balance_after
    )
    db.add(db_ledger)
    db.commit()
    db.refresh(db_ledger)
    return db_ledger


def get_ledger_entries(
    db: Session, 
    product_id: int = None, 
    warehouse_id: int = None,
    movement_type: str = None,
    skip: int = 0, 
    limit: int = 100
):
    query = db.query(StockLedger)
    
    if product_id:
        query = query.filter(StockLedger.product_id == product_id)
    if warehouse_id:
        query = query.filter(StockLedger.warehouse_id == warehouse_id)
    if movement_type:
        query = query.filter(StockLedger.movement_type == movement_type)
    
    return query.order_by(StockLedger.created_at.desc()).offset(skip).limit(limit).all()


def get_product_ledger(db: Session, product_id: int, skip: int = 0, limit: int = 100):
    return db.query(StockLedger).filter(
        StockLedger.product_id == product_id
    ).order_by(StockLedger.created_at.desc()).offset(skip).limit(limit).all()


def get_warehouse_ledger(db: Session, warehouse_id: int, skip: int = 0, limit: int = 100):
    return db.query(StockLedger).filter(
        StockLedger.warehouse_id == warehouse_id
    ).order_by(StockLedger.created_at.desc()).offset(skip).limit(limit).all()
