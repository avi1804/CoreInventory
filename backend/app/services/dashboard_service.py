from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Product, Stock, Receipt, Delivery, Transfer, Warehouse


def get_dashboard_kpis(db: Session):
    # Total products
    total_products = db.query(Product).count()
    
    # Total stock quantity across all warehouses
    total_stock = db.query(func.sum(Stock.quantity)).scalar() or 0
    
    # Low stock items (less than 10)
    low_stock_items = db.query(Product).join(Stock).filter(Stock.quantity < 10).filter(Stock.quantity > 0).count()
    
    # Out of stock items
    out_of_stock = db.query(Product).outerjoin(Stock).filter(
        (Stock.quantity == 0) | (Stock.quantity.is_(None))
    ).count()
    
    # Pending receipts (last 7 days)
    from datetime import datetime, timedelta
    week_ago = datetime.now() - timedelta(days=7)
    pending_receipts = db.query(Receipt).filter(Receipt.created_at >= week_ago).count()
    
    # Pending deliveries (last 7 days)
    pending_deliveries = db.query(Delivery).filter(Delivery.created_at >= week_ago).count()
    
    # Scheduled transfers (last 7 days)
    scheduled_transfers = db.query(Transfer).filter(Transfer.created_at >= week_ago).count()
    
    # Total warehouses
    total_warehouses = db.query(Warehouse).count()
    
    return {
        "total_products": total_products,
        "total_stock_quantity": total_stock,
        "low_stock_items": low_stock_items,
        "out_of_stock_items": out_of_stock,
        "pending_receipts": pending_receipts,
        "pending_deliveries": pending_deliveries,
        "scheduled_transfers": scheduled_transfers,
        "total_warehouses": total_warehouses
    }


def get_low_stock_products(db: Session, threshold: int = 10, skip: int = 0, limit: int = 100):
    """Get products with stock below threshold"""
    return db.query(Product, Stock).join(Stock).filter(
        Stock.quantity <= threshold
    ).offset(skip).limit(limit).all()


def get_out_of_stock_products(db: Session, skip: int = 0, limit: int = 100):
    """Get products with zero stock"""
    return db.query(Product).outerjoin(Stock).filter(
        (Stock.quantity == 0) | (Stock.quantity.is_(None))
    ).offset(skip).limit(limit).all()
