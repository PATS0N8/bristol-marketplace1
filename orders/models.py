from decimal import Decimal
from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = [
        ("PAID", "Paid"),
        ("PREPARING", "Preparing"),
        ("DISPATCHED", "Dispatched"),
        ("DELIVERED", "Delivered"),
    ]

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PAID")
    payment_reference = models.CharField(max_length=100, blank=True)

    def total_amount(self):
        return sum((item.price * item.quantity for item in self.orderitem_set.all()), Decimal("0.00"))

    def commission_amount(self):
        return self.total_amount() * Decimal("0.05")

    def producer_payout_amount(self):
        return self.total_amount() * Decimal("0.95")

    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product} x {self.quantity}"

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Order {self.order.id} -> {self.status}"
