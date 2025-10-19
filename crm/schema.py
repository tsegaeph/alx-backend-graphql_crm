import re
import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from .models import Customer, Product, Order
from datetime import datetime
from graphene_django.types import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from .filters import CustomerFilter, ProductFilter, OrderFilter

# ---------------- Input Types ----------------
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(default_value=0)


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# ---------------- Object Types ----------------
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone")


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock")


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# ---------------- Mutations ----------------
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        if input.phone and not re.match(r"^\+?\d{7,15}$", input.phone) and not re.match(r"^\d{3}-\d{3}-\d{4}$", input.phone):
            raise Exception("Invalid phone format")

        customer = Customer.objects.create(name=input.name, email=input.email, phone=input.phone)
        return CreateCustomer(customer=customer, message="Customer created successfully!")


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    @transaction.atomic
    def mutate(self, info, input):
        created_customers = []
        error_list = []

        for cust in input:
            try:
                if Customer.objects.filter(email=cust.email).exists():
                    raise Exception(f"Email {cust.email} already exists")
                if cust.phone and not re.match(r"^\+?\d{7,15}$", cust.phone) and not re.match(r"^\d{3}-\d{3}-\d{4}$", cust.phone):
                    raise Exception(f"Invalid phone format for {cust.name}")

                customer = Customer.objects.create(name=cust.name, email=cust.email, phone=cust.phone)
                created_customers.append(customer)
            except Exception as e:
                error_list.append(str(e))

        return BulkCreateCustomers(customers=created_customers, errors=error_list)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        if input.price <= 0:
            raise Exception("Price must be positive")
        if input.stock < 0:
            raise Exception("Stock cannot be negative")

        product = Product.objects.create(name=input.name, price=input.price, stock=input.stock)
        return CreateProduct(product=product)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not input.product_ids:
            raise Exception("At least one product must be selected")

        products = Product.objects.filter(id__in=input.product_ids)
        if products.count() != len(input.product_ids):
            raise Exception("One or more product IDs are invalid")

        order = Order.objects.create(customer=customer, order_date=input.order_date or datetime.now())
        order.products.set(products)
        order.total_amount = sum([p.price for p in products])
        order.save()

        return CreateOrder(order=order)


# ---------------- Query & Mutation ----------------
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    all_customers = graphene.List(CustomerType)
    all_products = graphene.List(ProductType)
    all_orders = graphene.List(OrderType)

    def resolve_all_customers(self, info):
        return Customer.objects.all()

    def resolve_all_products(self, info):
        return Product.objects.all()

    def resolve_all_orders(self, info):
        return Order.objects.all()


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")

    # Filtered queries
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)

    def resolve_hello(self, info):
        return "Hello, GraphQL!"
 
    