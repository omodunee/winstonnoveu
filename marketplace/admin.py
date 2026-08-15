from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import reverse
from django.db import models

from .models import Cart, CartItem, Category, Order, OrderItem, Product, User


admin.site.register(User, UserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "slug")


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ("order", "quantity", "price")
    readonly_fields = ("order", "quantity", "price")
    extra = 0


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("image_preview", "title", "category", "stock", "price", "total_sold", "revenue_generated")
    list_filter = ("category", "is_available", "is_featured")
    search_fields = ("title", "description")
    readonly_fields = ("image_preview", "total_sold", "revenue_generated")
    inlines = [OrderItemInline]

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:64px;height:64px;object-fit:cover;border-radius:8px;"/>', obj.image.url)
        return "-"

    image_preview.short_description = "Image"

    def total_sold(self, obj):
        return OrderItem.objects.filter(product=obj).aggregate(total=models.Sum('quantity'))['total'] or 0

    total_sold.short_description = "Sold"

    def revenue_generated(self, obj):
        from django.db.models import F, Sum

        val = OrderItem.objects.filter(product=obj).aggregate(total=Sum(F('price') * F('quantity')))['total']
        if val:
            return f"₦{val}"
        return "₦0"

    revenue_generated.short_description = "Revenue"

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ("cart", "product", "quantity")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "customer", "delivery_option", "status", "payment_status", "total_amount")
    list_filter = ("status", "payment_status", "delivery_option")
    search_fields = ("order_number", "customer__username")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price")


# Site branding
admin.site.site_header = "Winstonoveu Admin"
admin.site.site_title = "Winstonoveu"
admin.site.index_title = "Store Administration"
