from collections import defaultdict
from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CheckoutForm, ProductForm, UserRegistrationForm
from .models import Cart, CartItem, Category, Order, OrderItem, Product, User, UserRole


def role_required(*roles):
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")
            if request.user.role not in roles:
                messages.error(request, "You do not have permission to access this page.")
                return redirect("home")
            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def build_monthly_sales(orders):
    monthly_totals = defaultdict(Decimal)
    for order in orders:
        month = order.created_at.strftime("%b %Y")
        monthly_totals[month] += order.total_amount
    labels = []
    values = []
    for month, total in sorted(monthly_totals.items(), key=lambda x: datetime.strptime(x[0], "%b %Y"))[-6:]:
        labels.append(month)
        values.append(float(total))
    return labels, values


def home(request):
    featured_products = Product.objects.filter(is_featured=True, is_available=True).exclude(image__isnull=True).exclude(image="")[:6]
    products = Product.objects.filter(is_available=True).exclude(image__isnull=True).exclude(image="").order_by("-created_at")
    categories = Category.objects.all()
    return render(request, "home.html", {"products": products, "featured_products": featured_products, "categories": categories})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    if not product.image:
        messages.error(request, "This product is not available for display yet because it has no image.")
        return redirect("home")
    related_products = Product.objects.filter(category=product.category, is_available=True).exclude(image__isnull=True).exclude(image="").exclude(pk=product.pk)[:4]
    return render(request, "product_detail.html", {"product": product, "related_products": related_products})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect("home")
    else:
        form = UserRegistrationForm()

    return render(request, "register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Welcome back.")
            return redirect("dashboard")
        messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("home")


@login_required
def add_to_cart(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity", 1))
        product = get_object_or_404(Product, id=product_id)

        if product.stock <= 0:
            messages.error(request, "This item is currently out of stock.")
            return redirect("product_detail", slug=product.slug)

        cart = get_or_create_cart(request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        if cart_item.quantity > product.stock:
            cart_item.quantity = product.stock
        cart_item.save()

        messages.success(request, f"{product.title} added to your cart.")
    return redirect("cart")


@login_required
def cart_view(request):
    cart = get_or_create_cart(request.user)
    return render(request, "cart.html", {"cart": cart})


@login_required
def update_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    if request.method == "POST":
        new_quantity = max(1, int(request.POST.get("quantity", item.quantity)))
        item.quantity = min(new_quantity, item.product.stock)
        item.save()
        messages.success(request, "Cart updated.")
    return redirect("cart")


@login_required
def remove_cart_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect("cart")


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request.user)
    if not cart.items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect("home")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            delivery_option = form.cleaned_data["delivery_option"]
            delivery_fee = form.cleaned_data["delivery_fee"] or Decimal("0.00")
            address = form.cleaned_data["address"] or request.user.address
            note = form.cleaned_data["note"]

            order = Order.objects.create(
                customer=request.user,
                delivery_option=delivery_option,
                delivery_fee=delivery_fee,
                address=address,
                note=note,
                total_amount=cart.total_price + delivery_fee,
            )

            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price,
                    size=item.product.size,
                    color=item.product.color,
                )
                item.product.stock = max(item.product.stock - item.quantity, 0)
                item.product.save()

            cart.items.all().delete()
            return redirect("payment_success", order_id=order.id)
    else:
        form = CheckoutForm(initial={"delivery_option": "delivery", "address": request.user.address, "delivery_fee": 0})

    return render(request, "checkout.html", {"form": form, "cart": cart, "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY})


@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)

    if request.method == "POST":
        order.payment_status = "paid"
        order.status = "confirmed"
        order.paystack_reference = request.POST.get("reference", "")
        order.save()
        messages.success(request, "Payment received successfully.")
        return redirect("dashboard")

    return render(request, "order_success.html", {"order": order, "paystack_public_key": settings.PAYSTACK_PUBLIC_KEY})


@login_required
def dashboard_view(request):
    if request.user.role == UserRole.ADMIN:
        return redirect("admin_dashboard")

    if request.user.role == UserRole.SALESGIRL:
        orders = Order.objects.all().order_by("-created_at")
        products = Product.objects.all().order_by("-created_at")
        total_orders = orders.count()
        pending_orders = orders.filter(status="pending").count()
        paid_orders = orders.filter(payment_status="paid").count()
        monthly_labels, monthly_values = build_monthly_sales(orders)
        return render(
            request,
            "dashboard.html",
            {
                "orders": orders,
                "products": products,
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "paid_orders": paid_orders,
                "monthly_labels": monthly_labels,
                "monthly_values": monthly_values,
                "account_type": "Sales Girl",
            },
        )

    orders = Order.objects.filter(customer=request.user).order_by("-created_at")
    return render(request, "dashboard.html", {"orders": orders, "account_type": "Customer"})


@role_required(UserRole.ADMIN)
def admin_dashboard_view(request):
    orders = Order.objects.all().order_by("-created_at")
    products = Product.objects.all().order_by("-created_at")
    total_orders = orders.count()
    total_revenue = sum((order.total_amount for order in orders.filter(payment_status="paid")), Decimal("0.00"))
    pending_orders = orders.filter(status="pending").count()
    paid_orders = orders.filter(payment_status="paid").count()
    low_stock_products = products.filter(stock__lte=5)
    total_customers = User.objects.filter(role=UserRole.CUSTOMER).count()
    monthly_labels, monthly_values = build_monthly_sales(orders)

    return render(
        request,
        "admin_dashboard.html",
        {
            "orders": orders,
            "products": products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "pending_orders": pending_orders,
            "paid_orders": paid_orders,
            "low_stock_products": low_stock_products,
            "total_customers": total_customers,
            "monthly_labels": monthly_labels,
            "monthly_values": monthly_values,
            "account_type": "Admin",
        },
    )


def occasions_view(request):
    categories = Category.objects.all()
    return render(request, "occasions.html", {"categories": categories})


def category_products_view(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category, is_available=True).exclude(image__isnull=True).exclude(image="").order_by("-created_at")
    return render(request, "category_products.html", {"category": category, "products": products})


@role_required(UserRole.ADMIN)
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully.")
            return redirect("admin_dashboard")
    else:
        form = ProductForm()
    return render(request, "product_form.html", {"form": form, "title": "Create Product"})


@role_required(UserRole.ADMIN)
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated.")
            return redirect("admin_dashboard")
    else:
        form = ProductForm(instance=product)
    return render(request, "product_form.html", {"form": form, "title": "Update Product"})


@role_required(UserRole.ADMIN)
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    messages.success(request, "Product deleted successfully.")
    return redirect("admin_dashboard")


@role_required(UserRole.ADMIN, UserRole.SALESGIRL)
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "POST":
        status = request.POST.get("status")
        if status in dict(Order._meta.get_field("status").choices):
            order.status = status
            order.save()
            messages.success(request, "Order status updated.")
    return redirect("dashboard")
