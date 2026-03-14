from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductResponse, MessageResponse
from app.services import product_service, auth_service
from app.models.models import User

router = APIRouter(prefix="/api/products", tags=["products"])


@router.post("/add", response_model=MessageResponse)
def add_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Add a new product - requires authentication"""
    try:
        product_service.create_product(db, product)
        return MessageResponse(message="Product Added")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all", response_model=list[ProductResponse])
def get_products(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get all products - requires authentication"""
    return product_service.get_products(db, skip=skip, limit=limit)


@router.put("/update/{product_id}", response_model=MessageResponse)
def update_product(
    product_id: int,
    product: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update a product - requires authentication"""
    updated = product_service.update_product(db, product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return MessageResponse(message="Product Updated")


@router.delete("/delete/{product_id}", response_model=MessageResponse)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    """Delete a product - requires authentication"""
    deleted = product_service.delete_product(db, product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return MessageResponse(message="Product Deleted")
