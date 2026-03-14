"""
Database Transaction Utilities
Provides decorators and context managers for safe database operations
"""
import functools
import logging
from contextlib import contextmanager
from typing import Callable, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from fastapi import HTTPException

logger = logging.getLogger(__name__)


@contextmanager
def transaction_scope(db: Session):
    """
    Context manager for database transactions.
    Automatically commits on success or rolls back on exception.
    
    Usage:
        with transaction_scope(db) as session:
            session.add(some_object)
            # Automatically committed if no exception
    """
    try:
        yield db
        db.commit()
        logger.debug("Transaction committed successfully")
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error in transaction: {str(e)}")
        raise HTTPException(status_code=409, detail="Data integrity conflict")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in transaction: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


def transactional(func: Callable) -> Callable:
    """
    Decorator that wraps a function in a database transaction.
    The function must accept a 'db' parameter as the first argument.
    
    Usage:
        @transactional
        def create_order(db: Session, order_data: dict) -> Order:
            # Operations here are wrapped in a transaction
            order = Order(**order_data)
            db.add(order)
            return order
    """
    @functools.wraps(func)
    def wrapper(db: Session, *args, **kwargs):
        try:
            result = func(db, *args, **kwargs)
            db.commit()
            logger.debug(f"Transaction committed for {func.__name__}")
            return result
        except IntegrityError as e:
            db.rollback()
            logger.error(f"Integrity error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=409, detail="Data integrity conflict")
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="Database operation failed")
        except HTTPException:
            db.rollback()
            raise
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred")
    return wrapper


def atomic_operation(db: Session, operation: Callable, *args, **kwargs) -> Any:
    """
    Execute an operation atomically within a transaction.
    
    Args:
        db: Database session
        operation: Function to execute
        *args, **kwargs: Arguments to pass to the operation
    
    Returns:
        Result of the operation
    
    Raises:
        HTTPException: If transaction fails
    """
    try:
        result = operation(db, *args, **kwargs)
        db.commit()
        return result
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Integrity error in atomic operation: {str(e)}")
        raise HTTPException(status_code=409, detail="Data integrity conflict")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Database error in atomic operation: {str(e)}")
        raise HTTPException(status_code=500, detail="Database operation failed")
    except Exception as e:
        db.rollback()
        logger.error(f"Unexpected error in atomic operation: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


class TransactionManager:
    """
    Class-based transaction manager for complex scenarios
    """
    
    def __init__(self, db: Session):
        self.db = db
        self._savepoint = None
    
    def __enter__(self):
        """Start transaction"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Commit or rollback on exit"""
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        return False
    
    def commit(self):
        """Commit the transaction"""
        try:
            self.db.commit()
            logger.debug("Transaction committed")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error committing transaction: {str(e)}")
            raise
    
    def rollback(self):
        """Rollback the transaction"""
        try:
            self.db.rollback()
            logger.debug("Transaction rolled back")
        except Exception as e:
            logger.error(f"Error rolling back transaction: {str(e)}")
            raise
    
    def create_savepoint(self, name: str = None):
        """Create a savepoint for partial rollback"""
        # Note: Savepoints require database support
        # This is a placeholder for future implementation
        pass
