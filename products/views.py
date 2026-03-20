from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from .models import Category, Product
from orders.models import Order, OrderItem


def custom_login(request):
    error = ""

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        account_type = request.POST.get("account_type")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            if account_type == "admin":
                if user.is_staff:
                    return redirect("/admin/")
                else:
                    logout(request)
                    error = "This account does not have admin access."
            else:
                return redirect("/")
        else:
            error = "Invalid username or password."

    return render(request, "registration/login.html", {"error": error})


def custom_logout(request):
    logout(request)
    return redirect("/")


def home(request):
    categories = Category.objects.all()
    products = Product.objects.select_related("category", "producer")
    return render(request, "products/home.html", {
        "categories": categories,
        "products": products
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, "products/product_detail.html", {"product": product})


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category)
    return render(request, "products/category_products.html", {
        "category": category,
        "products": products
    })


def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session["cart"] = cart
    return redirect("view_cart")


def view_cart(request):
    cart = request.session.get("cart", {})
    items = []
    total = 0

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        subtotal = product.price_gbp * qty
        total += subtotal
        items.append({
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        })

    return render(request, "products/cart.html", {
        "items": items,
        "total": total
    })


def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    product_id = str(product_id)
    qty = int(request.POST.get("quantity"))

    if qty > 0:
        cart[product_id] = qty
    else:
        cart.pop(product_id, None)

    request.session["cart"] = cart
    return redirect("view_cart")


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("view_cart")


@login_required
def checkout(request):
    if getattr(request.user, "role", None) != "CUSTOMER":
        return HttpResponseForbidden("Only customers can checkout.")

    cart = request.session.get("cart", {})
    if not cart:
        return redirect("home")

    order = Order.objects.create(customer=request.user)

    for pid, qty in cart.items():
        product = Product.objects.get(id=pid)
        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=qty,
            price=product.price_gbp
        )

    request.session["cart"] = {}
    return render(request, "products/checkout_success.html", {"order": order})


@login_required
def customer_orders(request):
    if getattr(request.user, "role", None) != "CUSTOMER":
        return HttpResponseForbidden("Only customers can view customer orders.")

    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    return render(request, "products/customer_orders.html", {"orders": orders})


@login_required
def producer_orders(request):
    if getattr(request.user, "role", None) != "PRODUCER":
        return HttpResponseForbidden("Only producers can view producer orders.")

    items = OrderItem.objects.select_related("product", "order", "order__customer").filter(
        product__producer=request.user
    ).order_by("-order__created_at")

    return render(request, "products/producer_orders.html", {"items": items})
