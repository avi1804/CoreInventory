from sqlalchemy.orm import Session
from app.models.models import Delivery
from app.schemas.schemas import DeliveryCreate, StockLedgerCreate
from app.services.stock_service import update_stock_quantity
from app.services.stock_ledger_service import create_ledger_entry


def create_delivery(db: Session, delivery: DeliveryCreate) -> Delivery:
    db_delivery = Delivery(
        product_id=delivery.product_id,
        warehouse_id=delivery.warehouse_id,
        quantity=delivery.quantity
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    
    # Update stock quantity (decrease)
    updated_stock = update_stock_quantity(db, delivery.product_id, delivery.warehouse_id, -delivery.quantity)
    
    # Create ledger entry
    ledger_entry = StockLedgerCreate(
        product_id=delivery.product_id,
        warehouse_id=delivery.warehouse_id,
        movement_type="delivery",
        quantity=-delivery.quantity,
        reference_id=db_delivery.id,
        reference_type="delivery",
        balance_after=updated_stock.quantity
    )
    create_ledger_entry(db, ledger_entry)
    
    return db_delivery


def get_deliveries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Delivery).offset(skip).limit(limit).all()
