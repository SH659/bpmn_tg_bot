import datetime
from typing import List

from pydantic import BaseModel


class BM(BaseModel):
    class Config:
        from_attributes = True


class ProductResponse(BM):
    id: int
    title: str
    cost: int
    description: str


class ProductsResponse(BM):
    products: List[ProductResponse]
    has_next: bool
    has_prev: bool


class OrderItemRequest(BM):
    product_id: int


class OrderRequest(BM):
    user_id: str
    items: List[OrderItemRequest]


class OrderResponse(BM):
    id: int
    user_id: str
    created_at: datetime.datetime
