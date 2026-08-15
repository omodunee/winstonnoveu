from django.core.management.base import BaseCommand

from marketplace.models import Category, Product, User, UserRole


class Command(BaseCommand):
    help = "Creates default admin, sales girl, and sample customer accounts for the storefront."

    def handle(self, *args, **options):
        admin_account, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@winstonoveu.com",
                "first_name": "Winston",
                "last_name": "Owner",
                "role": UserRole.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_account.set_password("admin123")
        admin_account.save()

        sales_girl, _ = User.objects.get_or_create(
            username="salesgirl",
            defaults={
                "email": "sales@winstonoveu.com",
                "first_name": "Sonia",
                "last_name": "Sales",
                "role": UserRole.SALESGIRL,
                "is_staff": True,
            },
        )
        sales_girl.set_password("sales123")
        sales_girl.save()

        customer, _ = User.objects.get_or_create(
            username="customer",
            defaults={
                "email": "customer@winstonoveu.com",
                "first_name": "Nia",
                "last_name": "Client",
                "role": UserRole.CUSTOMER,
            },
        )
        customer.set_password("customer123")
        customer.save()

        category_data = [
            ("Dresses", "dresses", "Statement dresses for day and evening."),
            ("Jumpsuits", "jumpsuits", "Edgy one-pieces for movement and polish."),
            ("Sets", "sets", "Matching co-ord sets for easy styling."),
        ]

        for name, slug, description in category_data:
            Category.objects.get_or_create(name=name, defaults={"slug": slug, "description": description})

        dress = Category.objects.get(slug="dresses")
        jumpsuit = Category.objects.get(slug="jumpsuits")
        sets = Category.objects.get(slug="sets")

        sample_products = [
            {"title": "Velvet Runway Dress", "category": dress, "product_type": "dress", "size": "M", "color": "Ruby Red", "material": "Velvet", "price": 240000, "stock": 8, "is_featured": True},
            {"title": "Monarch Satin Set", "category": sets, "product_type": "co-ord", "size": "L", "color": "Ivory", "material": "Satin", "price": 260000, "stock": 6, "is_featured": True},
            {"title": "Night Shift Jumpsuit", "category": jumpsuit, "product_type": "jumpsuit", "size": "S", "color": "Midnight", "material": "Crepe", "price": 220000, "stock": 10, "is_featured": True},
            {"title": "City Edge Blazer", "category": sets, "product_type": "blazer", "size": "XL", "color": "Chocolate", "material": "Wool blend", "price": 190000, "stock": 5, "is_featured": False},
        ]

        for product_data in sample_products:
            Product.objects.get_or_create(
                title=product_data["title"],
                defaults={
                    "category": product_data["category"],
                    "product_type": product_data["product_type"],
                    "size": product_data["size"],
                    "color": product_data["color"],
                    "material": product_data["material"],
                    "price": product_data["price"],
                    "stock": product_data["stock"],
                    "is_featured": product_data["is_featured"],
                    "description": "A premium statement piece designed for standout energy, elevated comfort, and modern confidence.",
                    "is_available": True,
                },
            )

        self.stdout.write(self.style.SUCCESS("Default users and sample products created successfully."))
        self.stdout.write("Admin: admin / admin123")
        self.stdout.write("Sales girl: salesgirl / sales123")
        self.stdout.write("Customer: customer / customer123")
