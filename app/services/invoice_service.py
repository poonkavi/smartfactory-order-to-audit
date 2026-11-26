
from decimal import Decimal, ROUND_HALF_UP

from app import db
from app.models.orders import Order, OrderItem
from app.models.product import Product
from app.models.accounts import Invoice


# Manufacturer's state
COMPANY_STATE = "Tamil Nadu"

# Decimal rounding to 2 places
MONEY = Decimal("0.01")


def money(value):
    return Decimal(str(value)).quantize(
        MONEY,
        rounding=ROUND_HALF_UP
    )


def generate_invoice_number():
    invoices = Invoice.query.all()

    highest_number = 0

    for invoice in invoices:
        try:
            number = int(invoice.invoice_number.split("-")[-1])
            highest_number = max(highest_number, number)
        except (ValueError, IndexError):
            continue

    return f"INV-{highest_number + 1:04d}"


def generate_invoice(order_id):

    try:
        # Find order
        order = Order.query.get(order_id)

        if not order:
            return None, "Order not found."

        # Pending orders cannot be invoiced
        if order.status == "Pending":
            return None, "Only approved orders can be invoiced."

        # Prevent duplicate invoices for the same order
        existing_invoice = Invoice.query.filter_by(
            order_id=order.id
        ).first()

        if existing_invoice:
            return None, "Invoice already exists for this order."

        # Get order items
        order_items = OrderItem.query.filter_by(
            order_id=order.id
        ).all()

        if not order_items:
            return None, "This order has no items."

        taxable_amount = Decimal("0.00")
        cgst_total = Decimal("0.00")
        sgst_total = Decimal("0.00")
        igst_total = Decimal("0.00")

        # Determine intra-state or inter-state sale
        same_state = (
            order.customer_state.strip().lower()
            == COMPANY_STATE.lower()
        )

        # Calculate GST for each item
        for item in order_items:

            product = Product.query.get(item.product_id)

            if not product:
                raise ValueError(
                    f"Product not found for order item {item.id}"
                )

            line_amount = money(item.line_total)

            gst_rate = Decimal(str(product.gst_rate))

            gst_amount = money(
                line_amount * gst_rate / Decimal("100")
            )

            taxable_amount += line_amount

            if same_state:
                cgst_total += money(gst_amount / Decimal("2"))
                sgst_total += money(gst_amount / Decimal("2"))
            else:
                igst_total += gst_amount

        # Round final amounts
        taxable_amount = money(taxable_amount)
        cgst_total = money(cgst_total)
        sgst_total = money(sgst_total)
        igst_total = money(igst_total)

        total_amount = money(
            taxable_amount
            + cgst_total
            + sgst_total
            + igst_total
        )

        # Create invoice
        invoice = Invoice(
            invoice_number=generate_invoice_number(),
            order_id=order.id,
            taxable_amount=taxable_amount,
            cgst=cgst_total,
            sgst=sgst_total,
            igst=igst_total,
            total_amount=total_amount,
            status="Unpaid"
        )

        db.session.add(invoice)
        db.session.commit()

        return invoice, "Invoice generated successfully!"

    except Exception as e:
        db.session.rollback()

        return None, f"Invoice generation failed: {str(e)}"
