from django.contrib import admin
from django.urls import path, include
from products.views import custom_login, custom_logout, register_customer, register_producer
from accounts.views import account_settings

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("login/", custom_login, name="login"),
    path("logout/", custom_logout, name="logout"),
    path("register/customer/", register_customer, name="register_customer"),
    path("register/producer/", register_producer, name="register_producer"),
    path("account/", account_settings, name="account_settings"),
    path("", include("products.urls")),
]
