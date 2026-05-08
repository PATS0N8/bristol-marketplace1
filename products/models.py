# Django model imports
from django.db import models
from django.conf import settings


# ---------------- CATEGORY MODEL ---------------- #

# Stores product categories such as Fruit, Dairy, Vegetables etc.
class Category(models.Model):

    # Category name must be unique
    name = models.CharField(max_length=120, unique=True)

    # String representation shown in Django admin and shell
    def __str__(self):
        return self.name


# ---------------- PRODUCT MODEL ---------------- #

# Stores marketplace products listed by producers
class Product(models.Model):

    # Product stock/availability states
    class Availability(models.TextChoices):
        IN_STOCK = "IN_STOCK", "In Stock"
        OUT_OF_STOCK = "OUT_OF_STOCK", "Out of Stock"
        SEASONAL = "SEASONAL", "Seasonal"
        LIMITED = "LIMITED", "Limited Stock"

    # Links product to the producer who created it
    producer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="products"
    )

    # Links product to a category
    # PROTECT prevents deleting a category that still contains products
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products"
    )

    # Product name displayed to customers
    name = models.CharField(max_length=200)

    # Optional product description
    description = models.TextField(blank=True)

    # Product price stored in GBP
    price_gbp = models.DecimalField(max_digits=8, decimal_places=2)

    # Product measurement unit
    # Example: kg, dozen, bunch
    unit = models.CharField(max_length=50)

    # Current stock quantity available
    stock_qty = models.PositiveIntegerField(default=0)

    # Product availability status
    availability = models.CharField(
        max_length=20,
        choices=Availability.choices,
        default=Availability.IN_STOCK
    )

    # Optional future availability date
    # Used for 48-hour lead time functionality
    available_from = models.DateField(
        null=True,
        blank=True,
        help_text="Date from which this product is available for collection/delivery"
    )

    # Stores allergen information for food safety
    allergens = models.CharField(
        max_length=400,
        help_text="e.g., milk, eggs, nuts"
    )

    # Indicates whether the product is organically certified
    is_organic = models.BooleanField(default=False)

    # Indicates whether the product is currently treated as surplus stock
    is_surplus = models.BooleanField(default=False)

    # Percentage discount applied to surplus products
    discount_percent = models.PositiveIntegerField(
        default=0,
        help_text="Discount percentage e.g. 20 for 20%"
    )

    # Stock level where surplus discounts become active
    overstock_threshold = models.PositiveIntegerField(
        default=20,
        help_text="Stock level where surplus discount can apply"
    )

    # Removes surplus discount once stock drops below this level
    discount_remove_threshold = models.PositiveIntegerField(
        default=5,
        help_text="Remove surplus discount when stock falls to this level"
    )

    # Date product was harvested
    harvest_date = models.DateField(null=True, blank=True)

    # Best before date shown to customers
    best_before_date = models.DateField(null=True, blank=True)

    # Automatically stores product creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)


    # Calculates discounted product price if surplus discount is active
    def discounted_price(self):
        if self.is_surplus and self.discount_percent > 0:
            from decimal import Decimal

            # Calculates discount amount
            discount = (
                self.price_gbp
                * Decimal(self.discount_percent)
                / Decimal(100)
            )

            # Returns reduced price
            return self.price_gbp - discount

        # Returns normal price if no discount applies
        return self.price_gbp


    # String representation shown in Django admin and shell
    def __str__(self):
        return self.name


# ---------------- RECIPE MODEL ---------------- #

# Stores recipes linked to products
class Recipe(models.Model):

    # Links recipe to a product
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="recipes"
    )

    # Recipe title
    title = models.CharField(max_length=200)

    # Recipe ingredient list
    ingredients = models.TextField()

    # Step-by-step cooking instructions
    instructions = models.TextField()

    # Producer/admin who created the recipe
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Automatically stores creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    # String representation shown in Django admin and shell
    def __str__(self):
        return self.title


# ---------------- STORAGE GUIDE MODEL ---------------- #

# Stores storage guidance for a product
class StorageGuide(models.Model):

    # One-to-one relationship ensures only one storage guide per product
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="storage_guide"
    )

    # Storage guidance text
    guidance = models.TextField()

    # User who created the storage guide
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    # Automatically stores creation timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    # String representation shown in Django admin and shell
    def __str__(self):
        return f"Storage guide for {self.product.name}"


# ---------------- SURPLUS DISCOUNT HELPERS ---------------- #

# Checks whether a product currently qualifies for an active discount
def product_has_active_discount(self):
    return (
        # Product must have a discount percentage
        getattr(self, "discount_percent", 0) > 0

        # Stock must still be above overstock threshold
        and getattr(self, "stock_qty", 0)
        >= getattr(self, "overstock_threshold", 0)

        # Stock must still be above remove-discount threshold
        and getattr(self, "stock_qty", 0)
        > getattr(self, "discount_remove_threshold", 0)
    )


# Dynamically attaches helper method to Product model
Product.has_active_discount = product_has_active_discount


# Decimal import used for accurate financial calculations
from decimal import Decimal


# Returns currently active discount percentage
def active_discount_percent(self):

    # Discount only applies if stock conditions are met
    if (
        self.discount_percent > 0
        and self.stock_qty >= self.overstock_threshold
        and self.stock_qty > self.discount_remove_threshold
    ):
        return self.discount_percent

    # No discount applies
    return 0


# Calculates discounted product price dynamically
def active_discount_price(self):

    # Gets currently active discount percentage
    discount = active_discount_percent(self)

    # Applies percentage reduction if discount exists
    if discount > 0:
        return self.price_gbp - (
            self.price_gbp * Decimal(discount) / Decimal(100)
        )

    # Otherwise returns normal product price
    return self.price_gbp


# Dynamically attaches calculated properties to Product model
Product.active_discount_percent = property(active_discount_percent)
Product.active_discount_price = property(active_discount_price)