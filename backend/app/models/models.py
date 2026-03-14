from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Index, Boolean, Text, Numeric
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database.connection import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    # OTP fields for password reset
    otp = Column(String(10), nullable=True)
    otp_expiry = Column(DateTime, nullable=True)
    # Audit fields
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
    )


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="warehouse", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="warehouse")
    deliveries = relationship("Delivery", back_populates="warehouse")
    
    __table_args__ = (
        Index('idx_warehouse_name_active', 'name', 'is_active'),
    )


class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    sku = Column(String(255), nullable=False, unique=True, index=True)
    category = Column(String(255), nullable=False, index=True)
    unit = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    # Reordering rules
    min_stock_level = Column(Integer, default=10, nullable=False)
    max_stock_level = Column(Integer, default=100, nullable=False)
    reorder_point = Column(Integer, default=20, nullable=False)
    # Soft delete
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    stock = relationship("Stock", back_populates="product", cascade="all, delete-orphan")
    receipts = relationship("Receipt", back_populates="product")
    deliveries = relationship("Delivery", back_populates="product")
    
    __table_args__ = (
        Index('idx_product_sku_active', 'sku', 'is_active'),
        Index('idx_product_category_active', 'category', 'is_active'),
        Index('idx_product_name', 'name'),  # For search
    )


class Stock(Base):
    __tablename__ = "stock"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, default=0, nullable=False)
    reserved_quantity = Column(Integer, default=0, nullable=False)  # For pending orders
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="stock")
    warehouse = relationship("Warehouse", back_populates="stock")
    
    __table_args__ = (
        Index('idx_stock_product_warehouse', 'product_id', 'warehouse_id', unique=True),
        Index('idx_stock_warehouse', 'warehouse_id'),
        Index('idx_stock_quantity', 'quantity'),  # For low stock queries
    )


class Receipt(Base):
    __tablename__ = "receipts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="draft", nullable=False, index=True)
    supplier = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="receipts")
    warehouse = relationship("Warehouse", back_populates="receipts")
    creator = relationship("User", foreign_keys=[created_by])
    validator = relationship("User", foreign_keys=[validated_by])
    
    __table_args__ = (
        Index('idx_receipt_status', 'status'),
        Index('idx_receipt_warehouse_status', 'warehouse_id', 'status'),
        Index('idx_receipt_product', 'product_id'),
        Index('idx_receipt_created', 'created_at'),
    )


class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="draft", nullable=False, index=True)
    customer = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    product = relationship("Product", back_populates="deliveries")
    warehouse = relationship("Warehouse", back_populates="deliveries")
    creator = relationship("User", foreign_keys=[created_by])
    validator = relationship("User", foreign_keys=[validated_by])
    
    __table_args__ = (
        Index('idx_delivery_status', 'status'),
        Index('idx_delivery_warehouse_status', 'warehouse_id', 'status'),
        Index('idx_delivery_product', 'product_id'),
        Index('idx_delivery_created', 'created_at'),
    )


class Transfer(Base):
    __tablename__ = "transfers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    from_warehouse = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    to_warehouse = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    status = Column(String(20), default="draft", nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    validated_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_transfer_status', 'status'),
        Index('idx_transfer_from_warehouse', 'from_warehouse', 'status'),
        Index('idx_transfer_to_warehouse', 'to_warehouse', 'status'),
        Index('idx_transfer_product', 'product_id'),
        Index('idx_transfer_created', 'created_at'),
    )


class StockAdjustment(Base):
    __tablename__ = "stock_adjustments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    counted_quantity = Column(Integer, nullable=False)
    previous_quantity = Column(Integer, nullable=False)
    difference = Column(Integer, nullable=False)
    reason = Column(String(500), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_adjustment_product', 'product_id'),
        Index('idx_adjustment_warehouse', 'warehouse_id'),
        Index('idx_adjustment_created', 'created_at'),
    )


class StockLedger(Base):
    __tablename__ = "stock_ledger"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    movement_type = Column(String(50), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    reference_id = Column(Integer, nullable=True, index=True)
    reference_type = Column(String(50), nullable=True, index=True)
    balance_after = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    __table_args__ = (
        Index('idx_ledger_product_warehouse', 'product_id', 'warehouse_id'),
        Index('idx_ledger_movement_type', 'movement_type'),
        Index('idx_ledger_reference', 'reference_type', 'reference_id'),
        Index('idx_ledger_created', 'created_at'),
    )


class AuditLog(Base):
    """Audit log for tracking all changes"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(50), nullable=False, index=True)  # CREATE, UPDATE, DELETE, VALIDATE
    entity_type = Column(String(50), nullable=False, index=True)  # product, warehouse, receipt, etc.
    entity_id = Column(Integer, nullable=False, index=True)
    old_values = Column(Text, nullable=True)  # JSON string of old values
    new_values = Column(Text, nullable=True)  # JSON string of new values
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    __table_args__ = (
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_created', 'created_at'),
    )
