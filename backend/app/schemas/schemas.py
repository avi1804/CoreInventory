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


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptResponse(ReceiptBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Delivery Schemas
class DeliveryBase(BaseModel):
    product_id: int
    warehouse_id: int
    quantity: int


class DeliveryCreate(DeliveryBase):
    pass


class DeliveryResponse(DeliveryBase):
    id: int
    created_at: Optional[datetime] = None
    
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


class TransferResponse(TransferBase):
    id: int
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# Message Response
class MessageResponse(BaseModel):
    message: str
