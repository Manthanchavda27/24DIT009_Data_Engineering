dataset/ecommerce_schema.md
CUSTOMERS
---------
customer_id (PK)
first_name
last_name
email
phone
address

PRODUCTS
--------
product_id (PK)
product_name
category
brand
price
stock_quantity

ORDERS
------
order_id (PK)
customer_id (FK)
order_date
payment_status
order_status
total_amount

ORDER_ITEMS
-----------
order_item_id (PK)
order_id (FK)
product_id (FK)
quantity
unit_price

PAYMENTS
--------
payment_id (PK)
order_id (FK)
payment_method
payment_date
payment_status

INVENTORY
---------
inventory_id (PK)
product_id (FK)
warehouse
available_stock
last_updated