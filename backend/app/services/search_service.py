from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.models import Product, Stock, Receipt, Delivery, Transfer, StockAdjustment, StockLedger


def search_products(db: Session, query: str = None, category: str = None, skip: int = 0, limit: int = 100):
    """Search products by name, SKU, or category"""
    db_query = db.query(Product)
    
    if query:
        search_filter = or_(
            Product.name.ilike(f"%{query}%"),
            Product.sku.ilike(f"%{query}%"),
            Product.category.ilike(f"%{query}%")
        )
        db_query = db_query.filter(search_filter)
    
    if category:
        db_query = db_query.filter(Product.category == category)
    
    return db_query.offset(skip).limit(limit).all()


def filter_stock_by_warehouse(db: Session, warehouse_id: int = None, product_id: int = None, skip: int = 0, limit: int = 100):
    """Filter stock by warehouse and/or product"""
    query = db.query(Stock)
    
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if product_id:
        query = query.filter(Stock.product_id == product_id)
    
    return query.offset(skip).limit(limit).all()


def get_movements_by_type(db: Session, movement_type: str, skip: int = 0, limit: int = 100):
    """Get movements filtered by type: receipt, delivery, transfer, adjustment"""
    if movement_type == "receipt":
        return db.query(Receipt).order_by(Receipt.created_at.desc()).offset(skip).limit(limit).all()
    elif movement_type == "delivery":
        return db.query(Delivery).order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()
    elif movement_type == "transfer":
        return db.query(Transfer).order_by(Transfer.created_at.desc()).offset(skip).limit(limit).all()
    elif movement_type == "adjustment":
        return db.query(StockAdjustment).order_by(StockAdjustment.created_at.desc()).offset(skip).limit(limit).all()
    else:
        return []


def get_product_stock_by_warehouse(db: Session, product_id: int):
    """Get stock of a product across all warehouses"""
    return db.query(Stock).filter(Stock.product_id == product_id).all()


def get_categories(db: Session):
    """Get all unique product categories"""
    categories = db.query(Product.category).distinct().all()
    return [c[0] for c in categories]
