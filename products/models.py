from django.db import models
from django.conf import settings


class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    class Availability(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In Stock"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Out of Stock"
        SEASONAL = "SEASONAL", "Seasonal"
        LIMITED = "LIMITED", "Limited Stock"

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
        default=Availability.IN_STOCK
    )
    allergens = models.CharField(max_length=400, help_text="e.g., milk, eggs, nuts")
    #Bool field for organic certification
    is_organic = models.BooleanField(default=False)
    is_surplus = models.BooleanField(default=False)
    discount_percent = models.PositiveIntegerField(default=0, help_text="Discount percentage e.g. 20 for 20%")
    harvest_date = models.DateField(null=True, blank=True)
    best_before_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


    def discounted_price(self):
        if self.is_surplus and self.discount_percent > 0:
            from decimal import Decimal
            discount = self.price_gbp * Decimal(self.discount_percent) / Decimal(100)
            return self.price_gbp - discount
        return self.price_gbp

    def __str__(self):
        return self.name
