from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:item_id>/", views.update_cart_item, name="update_cart_item"),
    path("cart/remove/<int:item_id>/", views.remove_cart_item, name="remove_cart_item"),
    path("checkout/", views.checkout_view, name="checkout"),
    path("order-success/<int:order_id>/", views.payment_success, name="payment_success"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("occasions/", views.occasions_view, name="occasions"),
    path("category/<slug:slug>/", views.category_products_view, name="category_products"),
    path("orders/<int:pk>/status/", views.update_order_status, name="update_order_status"),
]
