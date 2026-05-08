# Imports Decimal for accurate financial calculations
from decimal import Decimal

# Django model imports
from django.db import models
from django.conf import settings


# ---------------- ORDER MODEL ---------------- #

# Stores customer orders
class Order(models.Model):

    # Available order statuses
    STATUS_CHOICES = [
        ("PAID", "Paid"),
        ("PREPARING", "Preparing"),
        ("DISPATCHED", "Dispatched"),
        ("DELIVERED", "Delivered"),
    ]

    # Links order to the customer who placed it
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Automatically stores order creation date/time
    created_at = models.DateTimeField(auto_now_add=True)

    # Current order fulfilment status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PAID"
    )

    # Stores Stripe or demo payment reference
    payment_reference = models.CharField(max_length=100, blank=True)

    # Calculates total order value
    def total_amount(self):
        return sum(
            (item.price * item.quantity for item in self.orderitem_set.all()),
            Decimal("0.00")
        )

    # Calculates marketplace commission (5%)
    def commission_amount(self):
        return self.total_amount() * Decimal("0.05")

    # Calculates producer payout after commission
    def producer_payout_amount(self):
        return self.total_amount() * Decimal("0.95")

    # String representation shown in Django admin and shell
    def __str__(self):
        return f"Order {self.id}"


# ---------------- ORDER ITEM MODEL ---------------- #

# Stores individual products within an order
class OrderItem(models.Model):

    # Links item to its parent order
    order = models.ForeignKey(Order, on_delete=models.CASCADE)

    # Links item to the purchased product
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE
    )

    # Quantity purchased
    quantity = models.IntegerField()

    # Product price at the time of purchase
    # Stored separately so future product price changes do not affect old orders
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Calculates subtotal for this order item
    def subtotal(self):
        return self.price * self.quantity

    # String representation shown in Django admin and shell
    def __str__(self):
        return f"{self.product} x {self.quantity}"


# ---------------- ORDER STATUS HISTORY ---------------- #

# Stores historical timeline updates for order fulfilment
class OrderStatusHistory(models.Model):

    # Links status update to an order
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="status_history"
    )

    # Stores updated order status
    status = models.CharField(
        max_length=20,
        choices=Order.STATUS_CHOICES
    )

    # User who updated the order status
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # Optional notes attached to status updates
    notes = models.CharField(max_length=255, blank=True)

    # Automatically stores timestamp of status update
    created_at = models.DateTimeField(auto_now_add=True)

    # Orders history chronologically
    class Meta:
        ordering = ["created_at"]

    # String representation shown in Django admin and shell
    def __str__(self):
        return f"Order {self.order.id} -> {self.status}"


# Sprint 3 refinement


# ---------------- SETTLEMENT MODEL ---------------- #

# Stores weekly settlement calculations for producers
class Settlement(models.Model):

    # Producer receiving the payout
    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settlements"
    )

    # Week ending date for this settlement period
    week_ending = models.DateField()

    # Total sales amount before commission
    gross_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Marketplace commission amount retained
    commission = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Final payout amount sent to producer
    payout = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # Tracks whether settlement has been paid
    is_paid = models.BooleanField(default=False)

    # Timestamp when settlement was marked as paid
    paid_at = models.DateTimeField(null=True, blank=True)

    # Optional admin notes about settlement/payment
    notes = models.CharField(max_length=255, blank=True)

    # Automatically stores settlement creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    # Shows newest settlements first
    class Meta:
        ordering = ["-week_ending"]

    # String representation shown in Django admin and shell
    def __str__(self):
        return f"Settlement for {self.producer.username} week ending {self.week_ending}"