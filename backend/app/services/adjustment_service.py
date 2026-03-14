from sqlalchemy.orm import Session
from app.models.models import StockAdjustment, Stock
from app.schemas.schemas import StockAdjustmentCreate
from app.services.stock_ledger_service import create_ledger_entry
from app.schemas.schemas import StockLedgerCreate


def create_adjustment(db: Session, adjustment: StockAdjustmentCreate) -> StockAdjustment:
    # Get current stock
    db_stock = db.query(Stock).filter(
        Stock.product_id == adjustment.product_id,
        Stock.warehouse_id == adjustment.warehouse_id
    ).first()
    
    previous_quantity = db_stock.quantity if db_stock else 0
    difference = adjustment.counted_quantity - previous_quantity
    
    # Create adjustment record
    db_adjustment = StockAdjustment(
        product_id=adjustment.product_id,
        warehouse_id=adjustment.warehouse_id,
        counted_quantity=adjustment.counted_quantity,
        previous_quantity=previous_quantity,
        difference=difference,
        reason=adjustment.reason
    )
    db.add(db_adjustment)
    db.commit()
    db.refresh(db_adjustment)
    
    # Update stock quantity
    if db_stock:
        db_stock.quantity = adjustment.counted_quantity
    else:
        db_stock = Stock(
            product_id=adjustment.product_id,
            warehouse_id=adjustment.warehouse_id,
            quantity=adjustment.counted_quantity
        )
        db.add(db_stock)
    
    db.commit()
    
    # Create ledger entry
    ledger_entry = StockLedgerCreate(
        product_id=adjustment.product_id,
        warehouse_id=adjustment.warehouse_id,
        movement_type="adjustment",
        quantity=difference,
        reference_id=db_adjustment.id,
        reference_type="adjustment",
        balance_after=adjustment.counted_quantity
    )
    create_ledger_entry(db, ledger_entry)
    
    return db_adjustment


def get_adjustments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(StockAdjustment).order_by(
        StockAdjustment.created_at.desc()
    ).offset(skip).limit(limit).all()


def get_adjustments_by_product(db: Session, product_id: int, skip: int = 0, limit: int = 100):
    return db.query(StockAdjustment).filter(
        StockAdjustment.product_id == product_id
    ).order_by(StockAdjustment.created_at.desc()).offset(skip).limit(limit).all()


def get_adjustments_by_warehouse(db: Session, warehouse_id: int, skip: int = 0, limit: int = 100):
    return db.query(StockAdjustment).filter(
        StockAdjustment.warehouse_id == warehouse_id
    ).order_by(StockAdjustment.created_at.desc()).offset(skip).limit(limit).all()
