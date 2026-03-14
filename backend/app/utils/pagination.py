"""
Advanced Pagination Utilities
Supports both offset-based and cursor-based pagination
"""
from typing import TypeVar, Generic, List, Optional, Any, Dict
from pydantic import BaseModel
from sqlalchemy.orm import Query
from sqlalchemy import desc, asc
import base64
import json

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    skip: int = 0
    limit: int = 100
    sort_by: Optional[str] = None
    sort_order: str = "asc"  # or "desc"
    
    class Config:
        json_schema_extra = {
            "example": {
                "skip": 0,
                "limit": 100,
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class CursorParams(BaseModel):
    """Cursor-based pagination parameters"""
    cursor: Optional[str] = None
    limit: int = 100
    sort_by: str = "id"
    sort_order: str = "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    """Standard paginated response format"""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    class Config:
        from_attributes = True


class CursorResponse(BaseModel, Generic[T]):
    """Cursor-based paginated response format"""
    items: List[T]
    next_cursor: Optional[str]
    prev_cursor: Optional[str]
    has_more: bool
    total_count: Optional[int]


class PaginationHelper:
    """Helper class for creating paginated responses"""
    
    @staticmethod
    def encode_cursor(data: Dict[str, Any]) -> str:
        """Encode cursor data to base64 string"""
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()
    
    @staticmethod
    def decode_cursor(cursor: str) -> Dict[str, Any]:
        """Decode base64 cursor string to data"""
        try:
            json_str = base64.b64decode(cursor.encode()).decode()
            return json.loads(json_str)
        except:
            return {}
    
    @staticmethod
    def apply_sorting(query: Query, sort_by: str, sort_order: str, model) -> Query:
        """Apply sorting to query"""
        sort_column = getattr(model, sort_by, None)
        if sort_column is None:
            sort_column = getattr(model, 'id')
        
        if sort_order.lower() == "desc":
            return query.order_by(desc(sort_column))
        return query.order_by(asc(sort_column))
    
    @staticmethod
    def paginate_offset(
        query: Query,
        skip: int = 0,
        limit: int = 100,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        model = None
    ) -> Dict[str, Any]:
        """
        Apply offset-based pagination to query
        
        Returns dict with items, total, skip, limit, has_more
        """
        # Get total count before pagination
        total = query.count()
        
        # Apply sorting if specified
        if sort_by and model:
            query = PaginationHelper.apply_sorting(query, sort_by, sort_order, model)
        
        # Apply pagination
        items = query.offset(skip).limit(limit + 1).all()
        
        # Check if there are more items
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]  # Remove the extra item
        
        return {
            "items": items,
            "total": total,
            "skip": skip,
            "limit": limit,
            "has_more": has_more
        }
    
    @staticmethod
    def paginate_cursor(
        query: Query,
        cursor: Optional[str] = None,
        limit: int = 100,
        sort_by: str = "id",
        sort_order: str = "desc",
        model = None
    ) -> Dict[str, Any]:
        """
        Apply cursor-based pagination to query
        
        Returns dict with items, next_cursor, prev_cursor, has_more
        """
        if model is None:
            raise ValueError("Model is required for cursor pagination")
        
        sort_column = getattr(model, sort_by, getattr(model, 'id'))
        
        # Apply cursor filter
        if cursor:
            cursor_data = PaginationHelper.decode_cursor(cursor)
            cursor_value = cursor_data.get('value')
            cursor_id = cursor_data.get('id')
            
            if cursor_value is not None:
                if sort_order.lower() == "desc":
                    query = query.filter(
                        (sort_column < cursor_value) |
                        ((sort_column == cursor_value) & (model.id < cursor_id))
                    )
                else:
                    query = query.filter(
                        (sort_column > cursor_value) |
                        ((sort_column == cursor_value) & (model.id > cursor_id))
                    )
        
        # Apply sorting
        if sort_order.lower() == "desc":
            query = query.order_by(desc(sort_column), desc(model.id))
        else:
            query = query.order_by(asc(sort_column), asc(model.id))
        
        # Get items (fetch one extra to check for more)
        items = query.limit(limit + 1).all()
        
        # Check if there are more items
        has_more = len(items) > limit
        if has_more:
            items = items[:-1]
        
        # Generate next cursor
        next_cursor = None
        if has_more and items:
            last_item = items[-1]
            cursor_value = getattr(last_item, sort_by, None)
            cursor_data = {
                'value': cursor_value,
                'id': last_item.id,
                'sort_by': sort_by,
                'sort_order': sort_order
            }
            next_cursor = PaginationHelper.encode_cursor(cursor_data)
        
        return {
            "items": items,
            "next_cursor": next_cursor,
            "prev_cursor": cursor,  # Previous cursor is the current one
            "has_more": has_more
        }


def create_pagination_links(
    base_url: str,
    skip: int,
    limit: int,
    total: int,
    **additional_params
) -> Dict[str, Optional[str]]:
    """
    Create pagination links (HATEOAS style)
    
    Returns dict with first, prev, next, last links
    """
    links = {
        "first": f"{base_url}?skip=0&limit={limit}",
        "prev": None,
        "next": None,
        "last": None
    }
    
    # Add additional params to URL
    params_str = ""
    for key, value in additional_params.items():
        if value is not None:
            params_str += f"&{key}={value}"
    
    # Previous link
    if skip > 0:
        prev_skip = max(0, skip - limit)
        links["prev"] = f"{base_url}?skip={prev_skip}&limit={limit}{params_str}"
    
    # Next link
    if skip + limit < total:
        next_skip = skip + limit
        links["next"] = f"{base_url}?skip={next_skip}&limit={limit}{params_str}"
    
    # Last link
    if total > 0:
        last_skip = ((total - 1) // limit) * limit
        links["last"] = f"{base_url}?skip={last_skip}&limit={limit}{params_str}"
    
    return links


class PageNumberPagination:
    """
    Page number based pagination (alternative to offset)
    More user-friendly for UI with page numbers
    """
    
    def __init__(self, page: int = 1, per_page: int = 20):
        self.page = max(1, page)
        self.per_page = max(1, min(per_page, 100))  # Max 100 per page
        self.skip = (self.page - 1) * self.per_page
    
    def apply(self, query: Query) -> Query:
        """Apply pagination to query"""
        return query.offset(self.skip).limit(self.per_page)
    
    def get_metadata(self, total: int) -> Dict[str, Any]:
        """Get pagination metadata"""
        total_pages = (total + self.per_page - 1) // self.per_page
        
        return {
            "page": self.page,
            "per_page": self.per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": self.page < total_pages,
            "has_prev": self.page > 1
        }
