from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
import re


# User Schemas
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="User's full name")
    email: str = Field(..., min_length=5, max_length=255, description="User's email address")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Validate email format"""
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and clean name"""
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not re.match(r'^[a-zA-Z\s\-\'\.]+$', v):
            raise ValueError('Name contains invalid characters')
        return v


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        return v


class UserLogin(BaseModel):
    email: str = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Normalize email"""
        return v.lower().strip()


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str
    user: UserResponse
    access_token: str
    token_type: str = "bearer"


# Warehouse Schemas
class WarehouseBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Warehouse name")
    location: str = Field(..., min_length=2, max_length=500, description="Warehouse location address")
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Clean and validate warehouse name"""
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Warehouse name must be at least 2 characters')
        return v


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    """Warehouse update - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    location: Optional[str] = Field(None, min_length=2, max_length=500)


class WarehouseResponse(WarehouseBase):
    id: int
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Product name")
    sku: str = Field(..., min_length=3, max_length=50, description="Stock Keeping Unit")
    category: str = Field(..., min_length=2, max_length=100, description="Product category")
    unit: str = Field(..., min_length=1, max_length=50, description="Unit of measurement")
    min_stock_level: int = Field(default=10, ge=0, le=10000, description="Minimum stock before alert")
    max_stock_level: int = Field(default=100, ge=1, le=100000, description="Maximum stock capacity")
    reorder_point: int = Field(default=20, ge=0, le=50000, description="Point at which to reorder")
    
    @field_validator('sku')
    @classmethod
    def validate_sku(cls, v: str) -> str:
        """Validate SKU format - alphanumeric with dashes/underscores"""
        v = v.strip().upper()
        if not re.match(r'^[A-Z0-9\-_]+$', v):
            raise ValueError('SKU must contain only letters, numbers, dashes, and underscores')
        return v
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Clean and validate product name"""
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Product name must be at least 2 characters')
        return v
    
    @field_validator('max_stock_level')
    @classmethod
    def validate_max_stock(cls, v: int, info) -> int:
        """Ensure max_stock_level is greater than min_stock_level"""
        if v < 1:
            raise ValueError('Max stock level must be at least 1')
        return v


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    """Product update schema - all fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    sku: Optional[str] = Field(None, min_length=3, max_length=50)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    min_stock_level: Optional[int] = Field(None, ge=0, le=10000)
    max_stock_level: Optional[int] = Field(None, ge=1, le=100000)
    reorder_point: Optional[int] = Field(None, ge=0, le=50000)


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    category: str
    unit: str
    stock: int = 0  # Computed from Stock model
    min_stock_level: int = 10
    max_stock_level: int = 100
    reorder_point: int = 20
    
    class Config:
        from_attributes = True


# Stock Schemas
class StockBase(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID")
    warehouse_id: int = Field(..., gt=0, description="Warehouse ID")
    quantity: int = Field(..., ge=0, le=1000000, description="Stock quantity")


class StockCreate(StockBase):
    pass


class StockResponse(StockBase):
    id: int
    
    class Config:
        from_attributes = True


# Receipt Schemas
class ReceiptBase(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID")
    warehouse_id: int = Field(..., gt=0, description="Warehouse ID")
    quantity: int = Field(..., gt=0, le=100000, description="Quantity received")
    supplier: Optional[str] = Field(None, max_length=255, description="Supplier name")
    
    @field_validator('supplier')
    @classmethod
    def validate_supplier(cls, v: Optional[str]) -> Optional[str]:
        """Clean supplier name"""
        if v:
            v = v.strip()
            if len(v) < 1:
                return None
        return v


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    status: str = Field(..., description="Status: draft, waiting, ready, done, canceled")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value"""
        valid_statuses = ["draft", "waiting", "ready", "done", "canceled"]
        v = v.lower().strip()
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class ReceiptResponse(ReceiptBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Delivery Schemas
class DeliveryBase(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID")
    warehouse_id: int = Field(..., gt=0, description="Warehouse ID")
    quantity: int = Field(..., gt=0, le=100000, description="Quantity delivered")
    customer: Optional[str] = Field(None, max_length=255, description="Customer name")
    
    @field_validator('customer')
    @classmethod
    def validate_customer(cls, v: Optional[str]) -> Optional[str]:
        """Clean customer name"""
        if v:
            v = v.strip()
            if len(v) < 1:
                return None
        return v


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    status: str = Field(..., description="Status: draft, waiting, ready, done, canceled")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value"""
        valid_statuses = ["draft", "waiting", "ready", "done", "canceled"]
        v = v.lower().strip()
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class DeliveryResponse(DeliveryBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Transfer Schemas
class TransferBase(BaseModel):
    product_id: int = Field(..., gt=0, description="Product ID")
    from_warehouse: int = Field(..., gt=0, description="Source warehouse ID")
    to_warehouse: int = Field(..., gt=0, description="Destination warehouse ID")
    quantity: int = Field(..., gt=0, le=100000, description="Quantity to transfer")
    
    @field_validator('to_warehouse')
    @classmethod
    def validate_warehouses(cls, v: int, info) -> int:
        """Ensure source and destination warehouses are different"""
        from_wh = info.data.get('from_warehouse')
        if from_wh and v == from_wh:
            raise ValueError('Source and destination warehouses must be different')
        return v


class TransferCreate(TransferBase):
    pass


class TransferUpdate(BaseModel):
    status: str = Field(..., description="Status: draft, waiting, ready, done, canceled")
    
    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status value"""
        valid_statuses = ["draft", "waiting", "ready", "done", "canceled"]
        v = v.lower().strip()
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {", ".join(valid_statuses)}')
        return v


class TransferResponse(TransferBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# OTP Schemas
class OTPRequest(BaseModel):
    email: str


class OTPVerify(BaseModel):
    email: str
    otp: str


class PasswordReset(BaseModel):
    email: str
    otp: str
    new_password: str


# Reordering Rules Schema
class ReorderAlert(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    reorder_point: int
    min_stock_level: int
    suggested_reorder_quantity: int


# Message Response
class MessageResponse(BaseModel):
    message: str


# Stock Adjustment Schemas
class StockAdjustmentBase(BaseModel):
    product_id: int
    warehouse_id: int
    counted_quantity: int
    reason: Optional[str] = None


class StockAdjustmentCreate(StockAdjustmentBase):
    pass


class StockAdjustmentResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    counted_quantity: int
    previous_quantity: int
    difference: int
    reason: Optional[str] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Stock Ledger Schemas
class StockLedgerBase(BaseModel):
    product_id: int
    warehouse_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    balance_after: int


class StockLedgerCreate(StockLedgerBase):
    pass


class StockLedgerResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    movement_type: str
    quantity: int
    reference_id: Optional[int] = None
    reference_type: Optional[str] = None
    balance_after: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Dashboard KPIs Schema
class DashboardKPIs(BaseModel):
    total_products: int
    total_stock_quantity: int
    low_stock_items: int
    out_of_stock_items: int
    pending_receipts: int
    pending_deliveries: int
    scheduled_transfers: int
    total_warehouses: int


# Filter Schemas
class ProductFilter(BaseModel):
    category: Optional[str] = None
    low_stock: Optional[bool] = None
    search: Optional[str] = None


class MovementFilter(BaseModel):
    document_type: Optional[str] = None  # receipt, delivery, transfer, adjustment
    status: Optional[str] = None
    warehouse_id: Optional[int] = None
    product_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


# User Profile Schema
class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None


class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: str
    
    class Config:
        from_attributes = True
