from django.contrib import admin
from .models import Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "producer", "category", "price_gbp", "stock_qty", "availability")
    list_filter = ("category", "availability")
    search_fields = ("name", "description", "producer__username")
