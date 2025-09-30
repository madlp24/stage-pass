# orders/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:ticket_type_id>/", views.cart_add, name="cart_add"),
    path("cart/update/<int:ticket_type_id>/", views.cart_update, name="cart_update"),
    path("cart/remove/<int:ticket_type_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("my/", views.my_orders, name="my_orders"), 
]

