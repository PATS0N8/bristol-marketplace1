from django.shortcuts import render, get_object_or_404
from .models import Category, Product


def home(request):
    categories = Category.objects.all().order_by("name")
    products = Product.objects.select_related("category", "producer").order_by("-created_at")[:20]
    return render(request, "products/home.html", {"categories": categories, "products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category", "producer"), id=product_id)
    return render(request, "products/product_detail.html", {"product": product})