from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        UNAVAILABLE = "UNAVAILABLE", "Unavailable"

    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price_gbp = models.DecimalField(max_digits=8, decimal_places=2)
    unit = models.CharField(max_length=50)         # e.g., "kg", "dozen"
    stock_qty = models.PositiveIntegerField(default=0)

    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.AVAILABLE
    )
    allergens = models.CharField(max_length=400, help_text="e.g., milk, eggs, nuts")
    harvest_dates = models.DateField(null=True, blank=True)
    best_before_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
