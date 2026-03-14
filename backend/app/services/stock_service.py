from sqlalchemy.orm import Session
from app.models.models import Stock
from app.schemas.schemas import StockCreate


def create_stock(db: Session, stock: StockCreate) -> Stock:
    db_stock = Stock(
        product_id=stock.product_id,
        warehouse_id=stock.warehouse_id,
        quantity=stock.quantity
    )
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock


def get_stock(db: Session, product_id: int, warehouse_id: int) -> Stock:
    return db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.warehouse_id == warehouse_id
    ).first()


def get_all_stock(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Stock).offset(skip).limit(limit).all()


def update_stock_quantity(db: Session, product_id: int, warehouse_id: int, quantity_change: int) -> Stock:
    db_stock = db.query(Stock).filter(
        Stock.product_id == product_id,
        Stock.warehouse_id == warehouse_id
    ).first()
    
    if db_stock:
        db_stock.quantity += quantity_change
        db.commit()
        db.refresh(db_stock)
    else:
        db_stock = Stock(
            product_id=product_id,
            warehouse_id=warehouse_id,
            quantity=quantity_change
        )
        db.add(db_stock)
        db.commit()
        db.refresh(db_stock)
    
    return db_stock
