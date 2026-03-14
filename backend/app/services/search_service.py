from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, func, desc, text
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.models.models import Product, Stock, Receipt, Delivery, Transfer, StockAdjustment, StockLedger, Warehouse


def search_products(
    db: Session, 
    query: str = None, 
    category: str = None, 
    low_stock: bool = None,
    min_stock_level: int = None,
    skip: int = 0, 
    limit: int = 100,
    sort_by: str = "name",
    sort_order: str = "asc"
) -> List[Product]:
    """
    Advanced product search with multiple filters
    
    Args:
        query: Search term for name, SKU, or category
        category: Filter by exact category
        low_stock: Filter for low stock items
        min_stock_level: Filter by minimum stock level threshold
        skip: Pagination offset
        limit: Pagination limit
        sort_by: Field to sort by (name, sku, category, created_at)
        sort_order: Sort direction (asc, desc)
    """
    db_query = db.query(Product).filter(Product.is_active == True)
    
    # Text search across multiple fields
    if query:
        search_term = f"%{query}%"
        search_filter = or_(
            Product.name.ilike(search_term),
            Product.sku.ilike(search_term),
            Product.category.ilike(search_term),
            Product.description.ilike(search_term) if hasattr(Product, 'description') else False
        )
        db_query = db_query.filter(search_filter)
    
    # Category filter
    if category:
        db_query = db_query.filter(Product.category.ilike(f"%{category}%"))
    
    # Low stock filter
    if low_stock:
        db_query = db_query.join(Stock).filter(
            Stock.quantity <= Product.reorder_point
        )
    
    # Minimum stock level filter
    if min_stock_level is not None:
        db_query = db_query.join(Stock).filter(Stock.quantity >= min_stock_level)
    
    # Sorting
    sort_column = getattr(Product, sort_by, Product.name)
    if sort_order.lower() == "desc":
        db_query = db_query.order_by(desc(sort_column))
    else:
        db_query = db_query.order_by(sort_column)
    
    return db_query.offset(skip).limit(limit).all()


def advanced_product_search(
    db: Session,
    name: Optional[str] = None,
    sku: Optional[str] = None,
    category: Optional[str] = None,
    warehouse_id: Optional[int] = None,
    min_quantity: Optional[int] = None,
    max_quantity: Optional[int] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Advanced product search with stock information
    
    Returns products with their stock levels across warehouses
    """
    # Build base query with stock aggregation
    query = db.query(
        Product,
        func.coalesce(func.sum(Stock.quantity), 0).label('total_stock'),
        func.count(Stock.warehouse_id).label('warehouse_count')
    ).outerjoin(
        Stock, Product.id == Stock.product_id
    ).filter(
        Product.is_active == True
    )
    
    # Apply filters
    if name:
        query = query.filter(Product.name.ilike(f"%{name}%"))
    if sku:
        query = query.filter(Product.sku.ilike(f"%{sku}%"))
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if warehouse_id:
        query = query.filter(Stock.warehouse_id == warehouse_id)
    if min_quantity is not None:
        query = query.having(func.coalesce(func.sum(Stock.quantity), 0) >= min_quantity)
    if max_quantity is not None:
        query = query.having(func.coalesce(func.sum(Stock.quantity), 0) <= max_quantity)
    if created_after:
        query = query.filter(Product.created_at >= created_after)
    if created_before:
        query = query.filter(Product.created_at <= created_before)
    
    # Group by product
    query = query.group_by(Product.id)
    
    # Order by name
    query = query.order_by(Product.name)
    
    results = query.offset(skip).limit(limit).all()
    
    # Format results
    formatted_results = []
    for product, total_stock, warehouse_count in results:
        formatted_results.append({
            "id": product.id,
            "name": product.name,
            "sku": product.sku,
            "category": product.category,
            "unit": product.unit,
            "total_stock": int(total_stock),
            "warehouse_count": warehouse_count,
            "reorder_point": product.reorder_point,
            "min_stock_level": product.min_stock_level,
            "max_stock_level": product.max_stock_level,
            "is_low_stock": int(total_stock) <= product.reorder_point
        })
    
    return formatted_results


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


def get_categories(db: Session, include_count: bool = False) -> List[Any]:
    """
    Get all unique product categories
    
    Args:
        db: Database session
        include_count: If True, returns categories with product counts
    
    Returns:
        List of category names or dicts with name and count
    """
    if include_count:
        results = db.query(
            Product.category,
            func.count(Product.id).label('product_count')
        ).filter(
            Product.is_active == True
        ).group_by(Product.category).all()
        return [{"category": c[0], "product_count": c[1]} for c in results]
    else:
        categories = db.query(Product.category).distinct().all()
        return [c[0] for c in categories]


def search_operations(
    db: Session,
    operation_type: Optional[str] = None,  # receipt, delivery, transfer
    status: Optional[str] = None,
    warehouse_id: Optional[int] = None,
    product_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Advanced search across all operation types
    
    Returns operations with unified format
    """
    results = {
        "receipts": [],
        "deliveries": [],
        "transfers": [],
        "total_count": 0
    }
    
    # Search receipts
    if operation_type is None or operation_type == "receipt":
        receipt_query = db.query(Receipt)
        if status:
            receipt_query = receipt_query.filter(Receipt.status == status)
        if warehouse_id:
            receipt_query = receipt_query.filter(Receipt.warehouse_id == warehouse_id)
        if product_id:
            receipt_query = receipt_query.filter(Receipt.product_id == product_id)
        if start_date:
            receipt_query = receipt_query.filter(Receipt.created_at >= start_date)
        if end_date:
            receipt_query = receipt_query.filter(Receipt.created_at <= end_date)
        
        receipts = receipt_query.order_by(desc(Receipt.created_at)).offset(skip).limit(limit).all()
        results["receipts"] = [{"type": "receipt", "id": r.id, "status": r.status, 
                               "product_id": r.product_id, "warehouse_id": r.warehouse_id,
                               "quantity": r.quantity, "created_at": r.created_at} for r in receipts]
    
    # Search deliveries
    if operation_type is None or operation_type == "delivery":
        delivery_query = db.query(Delivery)
        if status:
            delivery_query = delivery_query.filter(Delivery.status == status)
        if warehouse_id:
            delivery_query = delivery_query.filter(Delivery.warehouse_id == warehouse_id)
        if product_id:
            delivery_query = delivery_query.filter(Delivery.product_id == product_id)
        if start_date:
            delivery_query = delivery_query.filter(Delivery.created_at >= start_date)
        if end_date:
            delivery_query = delivery_query.filter(Delivery.created_at <= end_date)
        
        deliveries = delivery_query.order_by(desc(Delivery.created_at)).offset(skip).limit(limit).all()
        results["deliveries"] = [{"type": "delivery", "id": d.id, "status": d.status,
                                 "product_id": d.product_id, "warehouse_id": d.warehouse_id,
                                 "quantity": d.quantity, "created_at": d.created_at} for d in deliveries]
    
    # Search transfers
    if operation_type is None or operation_type == "transfer":
        transfer_query = db.query(Transfer)
        if status:
            transfer_query = transfer_query.filter(Transfer.status == status)
        if warehouse_id:
            transfer_query = transfer_query.filter(
                or_(Transfer.from_warehouse == warehouse_id, Transfer.to_warehouse == warehouse_id)
            )
        if product_id:
            transfer_query = transfer_query.filter(Transfer.product_id == product_id)
        if start_date:
            transfer_query = transfer_query.filter(Transfer.created_at >= start_date)
        if end_date:
            transfer_query = transfer_query.filter(Transfer.created_at <= end_date)
        
        transfers = transfer_query.order_by(desc(Transfer.created_at)).offset(skip).limit(limit).all()
        results["transfers"] = [{"type": "transfer", "id": t.id, "status": t.status,
                                "product_id": t.product_id, "from_warehouse": t.from_warehouse,
                                "to_warehouse": t.to_warehouse, "quantity": t.quantity,
                                "created_at": t.created_at} for t in transfers]
    
    results["total_count"] = len(results["receipts"]) + len(results["deliveries"]) + len(results["transfers"])
    return results
