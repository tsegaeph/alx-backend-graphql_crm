import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql.settings")
django.setup()

from crm.models import Customer, Product

def seed():
    Customer.objects.all().delete()
    Product.objects.all().delete()

    Customer.objects.create(name="Alice", email="alice@example.com", phone="+123456789")
    Customer.objects.create(name="Bob", email="bob@example.com")

    Product.objects.create(name="Laptop", price=999.99, stock=10)
    Product.objects.create(name="Phone", price=499.99, stock=20)

    print("Database seeded successfully!")

if __name__ == "__main__":
    seed()
