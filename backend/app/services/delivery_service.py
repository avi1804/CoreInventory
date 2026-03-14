from sqlalchemy.orm import Session
from app.models.models import Delivery
from app.schemas.schemas import DeliveryCreate
from app.services.stock_service import update_stock_quantity


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
    update_stock_quantity(db, delivery.product_id, delivery.warehouse_id, -delivery.quantity)
    
    return db_delivery


def get_deliveries(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Delivery).offset(skip).limit(limit).all()
