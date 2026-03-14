from sqlalchemy.orm import Session
from app.models.models import Delivery
from app.schemas.schemas import DeliveryCreate, StockLedgerCreate
from app.services.stock_service import update_stock_quantity
from app.services.stock_ledger_service import create_ledger_entry


def create_delivery(db: Session, delivery: DeliveryCreate) -> Delivery:
    """Create delivery in draft status - stock updated only on validation"""
    db_delivery = Delivery(
        product_id=delivery.product_id,
        warehouse_id=delivery.warehouse_id,
        quantity=delivery.quantity,
        customer=delivery.customer,
        status="draft"
    )
    db.add(db_delivery)
    db.commit()
    db.refresh(db_delivery)
    return db_delivery


def validate_delivery(db: Session, delivery_id: int) -> Delivery:
    """Validate delivery and update stock - only called when status moves to 'done'"""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        return None
    
    if delivery.status == "done":
        return delivery  # Already validated
    
    # Update stock quantity (decrease)
    updated_stock = update_stock_quantity(db, delivery.product_id, delivery.warehouse_id, -delivery.quantity)
    
    # Create ledger entry
    ledger_entry = StockLedgerCreate(
        product_id=delivery.product_id,
        warehouse_id=delivery.warehouse_id,
        movement_type="delivery",
        quantity=-delivery.quantity,
        reference_id=delivery.id,
        reference_type="delivery",
        balance_after=updated_stock.quantity
    )
    create_ledger_entry(db, ledger_entry)
    
    delivery.status = "done"
    db.commit()
    db.refresh(delivery)
    return delivery


def get_deliveries(db: Session, skip: int = 0, limit: int = 100, status: str = None, warehouse_id: int = None):
    query = db.query(Delivery)
    if status:
        query = query.filter(Delivery.status == status)
    if warehouse_id:
        query = query.filter(Delivery.warehouse_id == warehouse_id)
    return query.order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()


def update_delivery_status(db: Session, delivery_id: int, new_status: str) -> Delivery:
    """Update delivery status with workflow validation"""
    valid_statuses = ["draft", "waiting", "ready", "done", "canceled"]
    if new_status not in valid_statuses:
        return None
    
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    if not delivery:
        return None
    
    current_status = delivery.status
    
    if new_status == "canceled" and current_status == "done":
        return None
    
    # When transitioning to done, validate and update stock
    if new_status == "done":
        if current_status != "ready":
            return None
        return validate_delivery(db, delivery_id)
    
    delivery.status = new_status
    db.commit()
    db.refresh(delivery)
    return delivery
