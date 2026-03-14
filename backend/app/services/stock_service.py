from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.models import Stock
from app.schemas.schemas import StockCreate
import logging

logger = logging.getLogger(__name__)


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


def update_stock_quantity(
    db: Session, 
    product_id: int, 
    warehouse_id: int, 
    quantity_change: int, 
    allow_negative: bool = False,
    reference_id: int = None,
    reference_type: str = None
) -> Stock:
    """Update stock quantity with negative stock guard and transaction safety
    
    Args:
        db: Database session
        product_id: Product ID
        warehouse_id: Warehouse ID
        quantity_change: Amount to change (positive or negative)
        allow_negative: If False, raises HTTPException when stock would go below 0
        reference_id: ID of the operation causing the change
        reference_type: Type of operation (receipt, delivery, transfer, adjustment)
    
    Returns:
        Updated Stock object
    
    Raises:
        HTTPException: If stock would go negative and allow_negative is False
        SQLAlchemyError: If database transaction fails
    """
    try:
        # Use SELECT FOR UPDATE to prevent race conditions
        db_stock = db.query(Stock).filter(
            Stock.product_id == product_id,
            Stock.warehouse_id == warehouse_id
        ).with_for_update().first()
        
        old_quantity = db_stock.quantity if db_stock else 0
        
        if db_stock:
            new_quantity = db_stock.quantity + quantity_change
            # Negative stock guard
            if not allow_negative and new_quantity < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {db_stock.quantity}, Requested: {abs(quantity_change)}"
                )
            db_stock.quantity = new_quantity
        else:
            # Negative stock guard for new stock entries
            if not allow_negative and quantity_change < 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: 0, Requested: {abs(quantity_change)}"
                )
            db_stock = Stock(
                product_id=product_id,
                warehouse_id=warehouse_id,
                quantity=quantity_change
            )
            db.add(db_stock)
        
        db.commit()
        db.refresh(db_stock)
        
        # Log the stock change
        logger.info(
            f"Stock updated: product={product_id}, warehouse={warehouse_id}, "
            f"change={quantity_change}, old={old_quantity}, new={db_stock.quantity}, "
            f"ref={reference_type}:{reference_id}"
        )
        
        return db_stock
        
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error updating stock: {str(e)}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error updating stock: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
