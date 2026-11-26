from app import create_app
from app.models import Order, OrderItem, InventoryItem
from app.services.order_service import create_retailer_a_order

app = create_app()

with app.app_context():

    order, message = create_retailer_a_order()

    print(message)

    print("\nORDER DETAILS")
    print("-" * 30)

    print("Order Number:", order.order_number)
    print("Customer:", order.customer_name)
    print("State:", order.customer_state)
    print("Salesman ID:", order.salesman_id)
    print("Status:", order.status)
    print("Order Amount: Rs.", order.total_amount)

    order_item = OrderItem.query.filter_by(
        order_id=order.id
    ).first()

    print("\nORDER ITEM")
    print("Quantity:", order_item.quantity)
    print("Unit Price: Rs.", order_item.unit_price)
    print("Line Total: Rs.", order_item.line_total)

    stock = InventoryItem.query.filter_by(
        item_code="FG-MUR200"
    ).first()

    print("\nFinished Goods Stock:", stock.current_stock)