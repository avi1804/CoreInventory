from pydantic import BaseModel
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    name: str
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: int
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    message: str
    user: UserResponse


# Warehouse Schemas
class WarehouseBase(BaseModel):
    name: str
    location: str


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    id: int
    
    class Config:
        from_attributes = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    sku: str
    category: str
    unit: str
    stock: int
    min_stock_level: int = 10
    max_stock_level: int = 100
    reorder_point: int = 20


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int
    
    class Config:
        from_attributes = True


# Stock Schemas
class StockBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int


class StockCreate(StockBase):
    pass


class StockResponse(StockBase):
    id: int
    
    class Config:
        from_attributes = True


# Receipt Schemas
class ReceiptBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    supplier: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    status: str  # draft, waiting, ready, done, canceled


class ReceiptResponse(ReceiptBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Delivery Schemas
class DeliveryBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int
    customer: Optional[str] = None


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryUpdate(BaseModel):
    status: str  # draft, waiting, ready, done, canceled


class DeliveryResponse(DeliveryBase):
    id: int
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Transfer Schemas
class TransferBase(BaseModel):
    product_id: int
    from_warehouse: int
    to_warehouse: int
    quantity: int


class TransferCreate(TransferBase):
    pass


class TransferUpdate(BaseModel):
    status: str  # draft, waiting, ready, done, canceled


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
