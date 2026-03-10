from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# -----------------------------
# Product Database
# -----------------------------

products = [
    {"id": 1, "name": "Wireless Mouse", "price": 499, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "USB Hub", "price": 799, "category": "Electronics", "in_stock": False},
    {"id": 4, "name": "Pen Set", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 5, "name": "Laptop Stand", "price": 200, "category": "Electronics", "in_stock": False},
    {"id": 6, "name": "Mechanical Keyboard", "price": 800, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1500, "category": "Electronics", "in_stock": True},
]

# -----------------------------
# Home
# -----------------------------

@app.get("/")
def home():
    return {"message": "Welcome to our E-commerce API"}

# -----------------------------
# Get All Products
# -----------------------------

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

# -----------------------------
# In Stock Products
# -----------------------------

@app.get("/products/instocks")
def products_instock():

    list_instock = []

    for product in products:
        if product["in_stock"]:
            list_instock.append(product)

    return {
        "In stock Products": list_instock,
        "Total Instock": len(list_instock)
    }

# -----------------------------
# Cheapest & Most Expensive
# -----------------------------

@app.get("/products/deals")
def get_deals():

    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])

    return {
        "best_deal": cheapest,
        "premium_pick": expensive
    }

# -----------------------------
# Search Product
# -----------------------------

@app.get("/products/search/{keyword}")
def get_search_products(keyword: str):

    list_products = []

    for product in products:
        if keyword.lower() in product["name"].lower():
            list_products.append(product)

    if list_products:
        return {
            "Keyword": keyword,
            "Results": list_products,
            "Total Matches": len(list_products)
        }

    return {"Message": "No products matched in search"}

# -----------------------------
# Category Products
# -----------------------------

@app.get("/products/category/{category}")
def get_product_category(category: str):

    list_category = []

    for product in products:
        if product["category"].lower() == category.lower():
            list_category.append(product)

    if list_category:
        return {
            "Category": category,
            "Products": list_category,
            "Total": len(list_category)
        }

    return {"Error": "Product of that Category not there"}

# -----------------------------
# Filter Products (Query Params)
# -----------------------------

@app.get("/products/filter")
def filter_products(
    category: str = None,
    max_price: int = None,
    min_price: int = None
):

    filtered = []

    for product in products:

        if category and product["category"] != category:
            continue

        if max_price and product["price"] > max_price:
            continue

        if min_price and product["price"] < min_price:
            continue

        filtered.append(product)

    return filtered

# -----------------------------
# Product Summary
# -----------------------------

@app.get("/products/summary")
def product_summary():

    total_products = len(products)

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    most_expensive = max(products, key=lambda x: x["price"])
    cheapest = min(products, key=lambda x: x["price"])

    categories = list(set(p["category"] for p in products))

    return {
        "total_products": total_products,
        "in_stock_count": len(in_stock),
        "out_of_stock_count": len(out_stock),
        "most_expensive": {
            "name": most_expensive["name"],
            "price": most_expensive["price"]
        },
        "cheapest": {
            "name": cheapest["name"],
            "price": cheapest["price"]
        },
        "categories": categories
    }

# -----------------------------
# Get Only Price of Product
# -----------------------------

@app.get("/products/{product_id}/price")
def get_product_price(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {
                "name": product["name"],
                "price": product["price"]
            }

    return {"error": "Product not found"}

# -----------------------------
# Get Product by ID
# -----------------------------

@app.get("/products/{product_id}")
def get_product(product_id: int):

    for product in products:
        if product["id"] == product_id:
            return {"product": product}

    return {"error": "Product not found"}

# -----------------------------
# Customer Feedback
# -----------------------------

feedback = []

class CustomerFeedback(BaseModel):
    customer_name: str = Field(..., min_length=2)
    product_id: int = Field(..., gt=0)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=300)

@app.post("/feedback")
def submit_feedback(data: CustomerFeedback):

    feedback.append(data)

    return {
        "message": "Feedback submitted successfully",
        "feedback": data,
        "total_feedback": len(feedback)
    }

# -----------------------------
# Bulk Order System
# -----------------------------

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., ge=1, le=50)

class BulkOrder(BaseModel):
    company_name: str = Field(..., min_length=2)
    contact_email: str = Field(..., min_length=5)
    items: List[OrderItem]

@app.post("/orders/bulk")
def place_bulk_order(order: BulkOrder):

    confirmed = []
    failed = []
    grand_total = 0

    for item in order.items:

        product = next((p for p in products if p["id"] == item.product_id), None)

        if not product:
            failed.append({
                "product_id": item.product_id,
                "reason": "Product not found"
            })
            continue

        if not product["in_stock"]:
            failed.append({
                "product_id": item.product_id,
                "reason": f"{product['name']} is out of stock"
            })
            continue

        subtotal = product["price"] * item.quantity
        grand_total += subtotal

        confirmed.append({
            "product": product["name"],
            "qty": item.quantity,
            "subtotal": subtotal
        })

    return {
        "company": order.company_name,
        "confirmed": confirmed,
        "failed": failed,
        "grand_total": grand_total
    }

# -----------------------------
# BONUS - Order Tracking
# -----------------------------

orders = []

@app.post("/orders")
def create_order(order: BulkOrder):

    order_id = len(orders) + 1

    new_order = {
        "id": order_id,
        "company": order.company_name,
        "items": order.items,
        "status": "pending"
    }

    orders.append(new_order)

    return new_order

@app.get("/orders/{order_id}")
def get_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            return order

    return {"error": "Order not found"}

@app.patch("/orders/{order_id}/confirm")
def confirm_order(order_id: int):

    for order in orders:
        if order["id"] == order_id:
            order["status"] = "confirmed"
            return order

    return {"error": "Order not found"}