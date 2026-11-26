
from decimal import Decimal

from app import db
from app.models.user import User
from app.models.product import Product
from app.models.orders import Order, OrderItem


def create_order(
    salesman_id,
    customer_name,
    customer_state,
    product_sku,
    quantity,
    order_number
):
    try:
        # Validate customer details
        customer_name = customer_name.strip()
        customer_state = customer_state.strip()
        product_sku = product_sku.strip().upper()
        quantity = int(quantity)

        if not customer_name:
            return None, "Customer name is required."

        if not customer_state:
            return None, "Customer state is required."

        if quantity <= 0:
            return None, "Quantity must be greater than zero."

        # Validate salesman
        salesman = User.query.filter_by(
            id=salesman_id,
            role="Salesman"
        ).first()

        if not salesman:
            return None, "Invalid salesman selected."

        # Validate product
        product = Product.query.filter_by(
            sku=product_sku
        ).first()

        if not product:
            return None, "Product not found."

        # Prevent duplicate order numbers
        existing_order = Order.query.filter_by(
            order_number=order_number
        ).first()

        if existing_order:
            return None, "Order number already exists."

        # Calculate order amount
        unit_price = Decimal(str(product.selling_price))

        line_total = unit_price * quantity

        # Create sales order
        order = Order(
            order_number=order_number,
            customer_name=customer_name,
            customer_state=customer_state,
            salesman_id=salesman_id,
            status="Pending",
            total_amount=line_total
        )

        db.session.add(order)

        # Obtain order ID before creating order items
        db.session.flush()

        # Create order item
        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=quantity,
            unit_price=unit_price,
            line_total=line_total
        )

        db.session.add(order_item)

        # Save order and item
        db.session.commit()

        return order, "Sales order created successfully!"

    except Exception as e:
        db.session.rollback()

        return None, f"Order creation failed: {str(e)}"
