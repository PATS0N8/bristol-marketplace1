from decimal import Decimal
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Product
from orders.models import Order, OrderItem, OrderStatusHistory

User = get_user_model()

def custom_login(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        account_type = request.POST.get("account_type")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if account_type == "admin":
                if getattr(user, "role", "") == "ADMIN" or user.is_staff:
                    return redirect("/dashboard/")
                logout(request)
                error = "This account does not have admin access."
            return redirect("/")
        else:
            error = "Invalid username or password."

    return render(request, "registration/login.html", {"error": error})

def custom_logout(request):
    logout(request)
    return redirect("/")

def register_customer(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            error = "Username and password are required."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.role = "CUSTOMER"
            user.save()
            login(request, user)
            return redirect("/")

    return render(request, "registration/register_customer.html", {"error": error})

def register_producer(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            error = "Username and password are required."
        elif User.objects.filter(username=username).exists():
            error = "Username already exists."
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.role = "PRODUCER"
            user.save()
            login(request, user)
            return redirect("/")

    return render(request, "registration/register_producer.html", {"error": error})

def home(request):
    categories = Category.objects.all().order_by("name")
    q = request.GET.get("q", "").strip()
    products = Product.objects.select_related("category", "producer").filter(stock_qty__gt=0).order_by("-id")
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, "products/home.html", {
        "categories": categories,
        "products": products,
        "query": q,
    })

def product_detail(request, product_id):
    product = get_object_or_404(Product.objects.select_related("category", "producer"), id=product_id)
    return render(request, "products/product_detail.html", {"product": product})

def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.select_related("category", "producer").filter(category=category, stock_qty__gt=0).order_by("-id")
    return render(request, "products/category_products.html", {
        "category": category,
        "products": products,
    })

def add_to_cart(request, product_id):
    cart = request.session.get("cart", {})
    pid = str(product_id)
    product = get_object_or_404(Product, id=product_id)
    current_qty = cart.get(pid, 0) + 1

    if current_qty > product.stock_qty:
        return redirect(request.META.get("HTTP_REFERER", "/"))

    cart[pid] = current_qty
    request.session["cart"] = cart
    return redirect(request.META.get("HTTP_REFERER", "/"))

def view_cart(request):
    cart = request.session.get("cart", {})
    items = []
    total = Decimal("0.00")
    grouped = {}

    for pid, qty in cart.items():
        product = Product.objects.select_related("producer", "category").get(id=pid)
        subtotal = product.price_gbp * qty
        total += subtotal
        item = {
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        }
        items.append(item)

        producer_key = product.producer.username
        grouped.setdefault(producer_key, [])
        grouped[producer_key].append(item)

    return render(request, "products/cart.html", {
        "items": items,
        "grouped": grouped,
        "total": total
    })

def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    qty = int(request.POST.get("quantity", 1))
    product = get_object_or_404(Product, id=product_id)

    if qty > product.stock_qty:
        qty = product.stock_qty

    if qty > 0:
        cart[str(product_id)] = qty
    else:
        cart.pop(str(product_id), None)

    request.session["cart"] = cart
    return redirect("/cart/")

def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    cart.pop(str(product_id), None)
    request.session["cart"] = cart
    return redirect("/cart/")

@login_required
def checkout(request):
    if getattr(request.user, "role", "") != "CUSTOMER":
        return HttpResponseForbidden("Only customers can checkout.")
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("/")

    items = []
    total = Decimal("0.00")
    grouped = {}

    for pid, qty in cart.items():
        product = Product.objects.select_related("producer", "category").get(id=pid)
        subtotal = product.price_gbp * qty
        total += subtotal
        item = {
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        }
        items.append(item)

        producer_key = product.producer.username
        grouped.setdefault(producer_key, [])
        grouped[producer_key].append(item)

    return render(request, "products/checkout.html", {
        "items": items,
        "grouped": grouped,
        "total": total
    })

@login_required
def payment(request):
    if getattr(request.user, "role", "") != "CUSTOMER":
        return HttpResponseForbidden("Only customers can pay.")
    cart = request.session.get("cart", {})
    if not cart:
        return redirect("/")

    items = []
    total = Decimal("0.00")
    grouped = {}

    for pid, qty in cart.items():
        product = Product.objects.select_related("producer", "category").get(id=pid)
        subtotal = product.price_gbp * qty
        total += subtotal
        item = {
            "product": product,
            "quantity": qty,
            "subtotal": subtotal
        }
        items.append(item)
        grouped.setdefault(product.producer.username, [])
        grouped[product.producer.username].append(item)

    if request.method == "POST":
        order = Order.objects.create(
            customer=request.user,
            status="PAID",
            payment_reference=f"DEMO-{request.user.id}-{len(cart)}-{request.user.username}"
        )
        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price_gbp
            )
            product.stock_qty -= qty
            if product.stock_qty < 0:
                product.stock_qty = 0
            product.save()
        OrderStatusHistory.objects.create(
            order=order,
            status="PAID",
            updated_by=request.user,
            notes="Order placed and payment completed."
        )
        request.session["cart"] = {}
        return render(request, "products/checkout_success.html", {"order": order})

    return render(request, "products/payment.html", {
        "items": items,
        "grouped": grouped,
        "total": total
    })

@login_required
def customer_orders(request):
    if getattr(request.user, "role", "") != "CUSTOMER":
        return HttpResponseForbidden("Only customers can view past orders.")
    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    return render(request, "products/customer_orders.html", {"orders": orders})

@login_required
def producer_orders(request):
    if getattr(request.user, "role", "") != "PRODUCER":
        return HttpResponseForbidden("Only producers can view fulfilment orders.")

    orders = Order.objects.filter(
        orderitem__product__producer=request.user
    ).distinct().order_by("-created_at")

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        status = request.POST.get("status")
        notes = request.POST.get("notes", "").strip()

        order = get_object_or_404(
            Order.objects.filter(orderitem__product__producer=request.user).distinct(),
            id=order_id
        )
        order.status = status
        order.save()

        OrderStatusHistory.objects.create(
            order=order,
            status=status,
            updated_by=request.user,
            notes=notes
        )

        return redirect("/producer-orders/")

    return render(request, "products/producer_orders.html", {"orders": orders})

@login_required
def admin_dashboard(request):
    if getattr(request.user, "role", "") != "ADMIN" and not request.user.is_staff:
        return HttpResponseForbidden("Only admins can view the dashboard.")
    users = User.objects.all().order_by("-id")[:8]
    products = Product.objects.select_related("category", "producer").order_by("-id")[:8]
    orders = Order.objects.select_related("customer").order_by("-id")[:8]
    return render(request, "products/admin_dashboard.html", {
        "user_count": User.objects.count(),
        "product_count": Product.objects.count(),
        "order_count": Order.objects.count(),
        "users": users,
        "products": products,
        "orders": orders,
    })

@login_required
def admin_settlements(request):
    if getattr(request.user, "role", "") != "ADMIN" and not request.user.is_staff:
        return HttpResponseForbidden("Only admins can view settlements.")

    orders = Order.objects.prefetch_related("orderitem_set__product").order_by("-created_at")
    settlement_rows = []

    for order in orders:
        producer_groups = {}
        for item in order.orderitem_set.all():
            producer_name = item.product.producer.username
            producer_groups.setdefault(producer_name, Decimal("0.00"))
            producer_groups[producer_name] += item.price * item.quantity

        for producer_name, gross in producer_groups.items():
            commission = gross * Decimal("0.05")
            payout = gross * Decimal("0.95")
            settlement_rows.append({
                "order": order,
                "producer_name": producer_name,
                "gross": gross,
                "commission": commission,
                "payout": payout,
            })

    return render(request, "products/admin_settlements.html", {"rows": settlement_rows})

@login_required
def producer_add_product(request):
    if getattr(request.user, "role", "") != "PRODUCER":
        return HttpResponseForbidden("Only producers can add products.")

    categories = Category.objects.all().order_by("name")
    error = ""

    if request.method == "POST":
        try:
            category = Category.objects.get(id=request.POST.get("category"))
            Product.objects.create(
                producer=request.user,
                category=category,
                name=request.POST.get("name", "").strip(),
                description=request.POST.get("description", "").strip(),
                price_gbp=Decimal(request.POST.get("price_gbp")),
                unit=request.POST.get("unit", "").strip(),
                stock_qty=int(request.POST.get("stock_qty")),
                availability=request.POST.get("availability", "IN_STOCK"),
                allergens=request.POST.get("allergens", "").strip(),
                harvest_date=request.POST.get("harvest_date") or None,
                best_before_date=request.POST.get("best_before_date") or None,
                is_organic=request.POST.get("is_organic") == "on",
            )
            return redirect("/")
        except Exception as e:
            error = f"Could not create product: {e}"

    return render(request, "products/producer_add_product.html", {
        "categories": categories,
        "error": error,
    })

@login_required
def producer_settlements(request):
    if getattr(request.user, "role", "") != "PRODUCER":
        return HttpResponseForbidden("Only producers can view settlements.")

    from orders.models import OrderItem
    from decimal import Decimal

    items = OrderItem.objects.select_related("order", "product").filter(product__producer=request.user)

    rows = []
    total_gross = Decimal("0.00")
    total_commission = Decimal("0.00")
    total_payout = Decimal("0.00")

    for item in items:
        gross = item.price * item.quantity
        commission = gross * Decimal("0.05")
        payout = gross * Decimal("0.95")

        total_gross += gross
        total_commission += commission
        total_payout += payout

        rows.append({
            "order": item.order,
            "product": item.product,
            "quantity": item.quantity,
            "gross": gross,
            "commission": commission,
            "payout": payout,
        })

    return render(request, "products/producer_settlements.html", {
        "rows": rows,
        "total_gross": total_gross,
        "total_commission": total_commission,
        "total_payout": total_payout,
    })
# Sprint 3 refinement
