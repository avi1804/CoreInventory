"""
Audit Logging Service
Tracks all changes to entities for compliance and debugging
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import AuditLog


class AuditService:
    """Service for creating and querying audit logs"""
    
    @staticmethod
    def log_action(
        db: Session,
        action: str,  # CREATE, UPDATE, DELETE, VALIDATE, LOGIN, LOGOUT
        entity_type: str,  # product, warehouse, receipt, delivery, transfer, etc.
        entity_id: int,
        user_id: Optional[int] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry
        
        Args:
            db: Database session
            action: Type of action performed
            entity_type: Type of entity affected
            entity_id: ID of the entity
            user_id: ID of the user who performed the action
            old_values: Dictionary of old values (for UPDATE/DELETE)
            new_values: Dictionary of new values (for CREATE/UPDATE)
            ip_address: Client IP address
            user_agent: Client user agent string
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action.upper(),
            entity_type=entity_type.lower(),
            entity_id=entity_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
            ip_address=ip_address,
            user_agent=user_agent[:500] if user_agent else None
        )
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        return audit_log
    
    @staticmethod
    def get_entity_history(
        db: Session,
        entity_type: str,
        entity_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """Get audit history for a specific entity"""
        return db.query(AuditLog).filter(
            AuditLog.entity_type == entity_type.lower(),
            AuditLog.entity_id == entity_id
        ).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_user_actions(
        db: Session,
        user_id: int,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """Get audit logs for a specific user"""
        query = db.query(AuditLog).filter(AuditLog.user_id == user_id)
        if action:
            query = query.filter(AuditLog.action == action.upper())
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_recent_actions(
        db: Session,
        entity_type: Optional[str] = None,
        action: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> list:
        """Get recent audit logs with optional filtering"""
        query = db.query(AuditLog)
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type.lower())
        if action:
            query = query.filter(AuditLog.action == action.upper())
        return query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def parse_audit_values(audit_log: AuditLog) -> Dict[str, Any]:
        """Parse JSON values from audit log"""
        result = {
            "id": audit_log.id,
            "user_id": audit_log.user_id,
            "action": audit_log.action,
            "entity_type": audit_log.entity_type,
            "entity_id": audit_log.entity_id,
            "created_at": audit_log.created_at.isoformat() if audit_log.created_at else None,
            "ip_address": audit_log.ip_address,
            "old_values": json.loads(audit_log.old_values) if audit_log.old_values else None,
            "new_values": json.loads(audit_log.new_values) if audit_log.new_values else None
        }
        return result


# Decorator for automatic audit logging
def audit_action(action: str, entity_type: str, get_entity_id=None, get_old_values=None):
    """
    Decorator to automatically log actions
    
    Usage:
        @audit_action(action="UPDATE", entity_type="product", 
                      get_entity_id=lambda args: args[1])
        def update_product(db, product_id, data):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Extract db session (usually first arg after self)
            db = args[1] if len(args) > 1 else kwargs.get('db')
            
            # Get entity ID
            entity_id = get_entity_id(args) if get_entity_id else None
            
            # Get old values before operation
            old_values = get_old_values(args, kwargs) if get_old_values else None
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log the action
            if db and entity_id:
                AuditService.log_action(
                    db=db,
                    action=action,
                    entity_type=entity_type,
                    entity_id=entity_id,
                    old_values=old_values,
                    new_values=result.__dict__ if hasattr(result, '__dict__') else None
                )
            
            return result
        return wrapper
    return decorator
