from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path("product/<int:product_id>/", product_detail, name="product_detail"),
    path("category/<int:category_id>/", category_products, name="category_products"),

    path("add-to-cart/<int:product_id>/", add_to_cart, name="add_to_cart"),
    path("cart/", view_cart, name="view_cart"),
    path("update-cart/<int:product_id>/", update_cart, name="update_cart"),
    path("remove-from-cart/<int:product_id>/", remove_from_cart, name="remove_from_cart"),

    path("checkout/", checkout, name="checkout"),
    path("payment/", payment, name="payment"),

    path("my-orders/", customer_orders, name="customer_orders"),
    path("producer-orders/", producer_orders, name="producer_orders"),
    path("producer/add-product/", producer_add_product, name="producer_add_product"),

    path("producer/earnings/", producer_settlements, name="producer_settlements"),

    path("dashboard/", admin_dashboard, name="admin_dashboard"),
    path("dashboard/settlements/", admin_settlements, name="admin_settlements"),
]
