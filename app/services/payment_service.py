from decimal import Decimal, ROUND_HALF_UP

from app import db
from app.models.accounts import Invoice, Payment


MONEY = Decimal("0.01")

ALLOWED_PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Bank Transfer"
]


def money(value):
    return Decimal(str(value)).quantize(
        MONEY,
        rounding=ROUND_HALF_UP
    )


def get_total_paid(invoice_id):
    payments = Payment.query.filter_by(
        invoice_id=invoice_id
    ).all()

    total = sum(
        (Decimal(str(payment.amount)) for payment in payments),
        Decimal("0.00")
    )

    return money(total)


def get_outstanding_balance(invoice_id):
    invoice = Invoice.query.get(invoice_id)

    if not invoice:
        return None

    total_paid = get_total_paid(invoice_id)

    balance = (
        Decimal(str(invoice.total_amount))
        - total_paid
    )

    return money(balance)


def record_payment(
    invoice_id,
    amount,
    payment_method,
    reference_number=None
):
    try:

        # Find invoice
        invoice = Invoice.query.get(invoice_id)

        if not invoice:
            return None, "Invoice not found."

        # Validate payment amount
        amount = money(amount)

        if amount <= Decimal("0.00"):
            return None, "Payment amount must be greater than zero."

        # Validate payment method
        payment_method = payment_method.strip()

        if payment_method not in ALLOWED_PAYMENT_METHODS:
            return None, "Invalid payment method."

        # Calculate existing payments
        total_paid = get_total_paid(invoice_id)

        # Calculate remaining balance
        balance = money(
            Decimal(str(invoice.total_amount))
            - total_paid
        )

        if balance <= Decimal("0.00"):
            return None, "This invoice is already fully paid."

        # Prevent overpayment
        if amount > balance:
            return None, f"Payment exceeds outstanding balance of ₹{balance}."

        # Create payment record
        payment = Payment(
            invoice_id=invoice.id,
            amount=amount,
            payment_method=payment_method,
            reference_number=reference_number
        )

        db.session.add(payment)

        # Calculate new paid amount
        new_total_paid = money(total_paid + amount)

        # Update invoice status
        if new_total_paid >= Decimal(str(invoice.total_amount)):
            invoice.status = "Paid"

        elif new_total_paid > Decimal("0.00"):
            invoice.status = "Partially Paid"

        else:
            invoice.status = "Unpaid"

        db.session.commit()

        return payment, "Payment recorded successfully!"

    except Exception as e:

        db.session.rollback()

        return None, f"Payment failed: {str(e)}"