from collections import Counter

from fastapi import FastAPI, HTTPException, Query

from database import Product, Order, OrderItem, db
from schemas import OrderRequest, OrderResponse, ProductResponse, ProductsResponse
from settings import settings

app = FastAPI()


@app.get("/products", response_model=ProductsResponse)
def get_products(page: int = Query(1, ge=1), per_page: int = Query(10, ge=1)):
    total_products = Product.select().count()
    products = list(Product.select().paginate(page, per_page))
    return ProductsResponse(
        products=[ProductResponse.model_validate(product) for product in products],
        has_next=page * per_page < total_products,
        has_prev=(page > 1)
    )


@app.post("/orders", response_model=OrderResponse)
def create_order(order_request: OrderRequest):
    with db.atomic():
        order = Order.create(user_id=order_request.user_id)

        counter = Counter(item.product_id for item in order_request.items)

        order_items = []
        for product_id, count in counter.items():
            try:
                product = Product.get(Product.id == product_id)
            except Product.DoesNotExist:
                raise HTTPException(status_code=404, detail=f"Product {product_id} not found")

            order_item = OrderItem.create(
                order=order,
                product=product,
                cost=product.cost,
                count=count
            )
            order_items.append(order_item)

        response = OrderResponse(
            id=order.id,
            user_id=order.user_id,
            created_at=order.created_at,
        )
        return response


if __name__ == '__main__':
    import uvicorn

    uvicorn.run('main:app', reload=True, port=settings.PORT)
