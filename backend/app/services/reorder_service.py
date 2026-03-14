from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import Product, Stock
from app.schemas.schemas import ReorderAlert


def get_reorder_alerts(db: Session, skip: int = 0, limit: int = 100):
    """Get products that need reordering (stock below reorder_point)"""
    results = []
    
    # Get all products with their stock levels
    products_with_stock = db.query(Product, func.coalesce(func.sum(Stock.quantity), 0).label('total_stock')).\
        outerjoin(Stock, Product.id == Stock.product_id).\
        group_by(Product.id).all()
    
    for product, total_stock in products_with_stock:
        if total_stock <= product.reorder_point:
            suggested_qty = product.max_stock_level - total_stock
            if suggested_qty < 0:
                suggested_qty = 0
                
            results.append(ReorderAlert(
                product_id=product.id,
                product_name=product.name,
                current_stock=total_stock,
                reorder_point=product.reorder_point,
                min_stock_level=product.min_stock_level,
                suggested_reorder_quantity=suggested_qty
            ))
    
    return results[skip:skip+limit]


def get_products_below_min_stock(db: Session, skip: int = 0, limit: int = 100):
    """Get products below minimum stock level (critical)"""
    results = []
    
    products_with_stock = db.query(Product, func.coalesce(func.sum(Stock.quantity), 0).label('total_stock')).\
        outerjoin(Stock, Product.id == Stock.product_id).\
        group_by(Product.id).all()
    
    for product, total_stock in products_with_stock:
        if total_stock < product.min_stock_level:
            suggested_qty = product.max_stock_level - total_stock
            if suggested_qty < 0:
                suggested_qty = 0
                
            results.append(ReorderAlert(
                product_id=product.id,
                product_name=product.name,
                current_stock=total_stock,
                reorder_point=product.reorder_point,
                min_stock_level=product.min_stock_level,
                suggested_reorder_quantity=suggested_qty
            ))
    
    return results[skip:skip+limit]


def update_product_reorder_rules(db: Session, product_id: int, min_stock: int = None, max_stock: int = None, reorder_point: int = None):
    """Update reordering rules for a product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        return None
    
    if min_stock is not None:
        product.min_stock_level = min_stock
    if max_stock is not None:
        product.max_stock_level = max_stock
    if reorder_point is not None:
        product.reorder_point = reorder_point
    
    db.commit()
    db.refresh(product)
    return product
