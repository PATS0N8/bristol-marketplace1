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

    path("product/<int:product_id>/add-recipe/", add_recipe, name="add_recipe"),
    path("product/<int:product_id>/add-storage/", add_storage_guide, name="add_storage_guide"),

    path("dashboard/add-category/", admin_add_category, name="admin_add_category"),
    path("dashboard/add-user/", admin_add_user, name="admin_add_user"),
    path("dashboard/add-product/", admin_add_product, name="admin_add_product"),

    path("dashboard/settlements/generate/", admin_generate_settlements, name="admin_generate_settlements"),
    path("dashboard/settlements/manage/", admin_manage_settlements, name="admin_manage_settlements"),
]
# Sprint 3 refinement

from .views import create_checkout_session, payment_success

urlpatterns += [
    path('create-checkout-session/', create_checkout_session, name='create_checkout_session'),
    path('payment-success/', payment_success, name='payment_success'),
]

urlpatterns += [
    path("settlements/all/", settlements_debug_all, name="settlements_debug_all"),
]
