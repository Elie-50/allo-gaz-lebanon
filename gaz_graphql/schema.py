import graphene
import datetime
from django.db.models import Q, F, Sum
from django.core.paginator import Paginator, EmptyPage
from django.utils.timezone import make_aware
from graphene_django import DjangoObjectType
from user.models import User
from order.models import Order
from item.models import Item, Source
from customer.models import Customer, Address, PhoneNumber
from helpers.util import login_required_resolver
from urllib.parse import urlparse, urlunparse

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'middle_name', 'email', 'last_name', 'phone_number', 'is_driver', 'is_staff', 'is_active', 'is_superuser')

    orders = graphene.List(lambda: OrderType)

    def resolve_orders(self, info):
        return self.orders_made.all()

class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'

    addresses = graphene.List(lambda: AddressType)

    def resolve_addresses(self, info):
        return self.addresses.all()

    orders = graphene.List(lambda: OrderType)

    def resolve_orders(self, info):
        return self.orders.all()

class CustomerSearchResult(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    totalPages = graphene.Int()

class EmployeeSearchResult(graphene.ObjectType):
    employees = graphene.List(UserType)
    totalPages = graphene.Int()

class PhoneNumberType(DjangoObjectType):
    class Meta:
        model = PhoneNumber
        fields = '__all__'

class AddressType(DjangoObjectType):
    class Meta:
        model = Address
        fields = '__all__'
    
    image_url = graphene.String()

    def resolve_image_url(self, info):
        request = info.context
        if self.image:
            # Build the absolute URL
            absolute_url = request.build_absolute_uri(self.image.url)

            # Parse and remove query and fragment
            parsed = urlparse(absolute_url)
            clean_url = urlunparse(parsed._replace(query="", fragment=""))

            return clean_url
        return None
    
    orders = graphene.List(lambda: OrderType)

    def resolve_orders(self, info):
        return self.orders.all()
    
    mobile_numbers = graphene.List(lambda: PhoneNumberType)

    def resolve_mobile_numbers(self, info):
        return self.mobile_numbers.all()

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"

class SourceType(DjangoObjectType):
    class Meta:
        model = Source
        fields = '__all__'

class ItemType(DjangoObjectType):
    class Meta:
        model = Item
        fields = "__all__"

    image_url = graphene.String()

    def resolve_image_url(self, info):
        request = info.context
        if self.image:
            # Build the absolute URL
            absolute_url = request.build_absolute_uri(self.image.url)

            # Parse and remove query and fragment
            parsed = urlparse(absolute_url)
            clean_url = urlunparse(parsed._replace(query="", fragment=""))

            return clean_url
        return None

    orders = graphene.List(lambda: OrderType)

    def resolve_orders(self, info):
        return self.orders.all()
    
    sources = graphene.List(lambda: SourceType)

    def resolve_sources(self, info):
        return self.sources.all()

class OrderPaginationResult(graphene.ObjectType):
    orders = graphene.List(OrderType)
    address = graphene.Field(AddressType)
    total_pages = graphene.Int()


class Query(graphene.ObjectType):
    customer_by_id = graphene.Field(CustomerType, id=graphene.Int(required=True))
    order_by_id = graphene.Field(OrderType, id=graphene.Int(required=True))
    item_by_id = graphene.Field(ItemType, id=graphene.Int(required=True))
    user_by_id = graphene.Field(UserType, id=graphene.Int(required=True))
    address_by_id = graphene.Field(AddressType, id=graphene.Int(required=True))
    all_items = graphene.List(ItemType)
    customers_search = graphene.Field(
        CustomerSearchResult,
        firstname=graphene.String(required=True),
        lastname=graphene.String(required=True),
        middlename=graphene.String(required=True),
        page=graphene.Int(required=True),
        number_of_results=graphene.Int(required=True),
        mobile=graphene.String(required=True),
        email=graphene.String(required=True),
        order_by=graphene.String(required=True),
        order_direction=graphene.Int(required=True),
        is_active=graphene.Boolean(required=True)
    )
    employees_search = graphene.Field(
        EmployeeSearchResult,
        username=graphene.String(required=True),
        firstname=graphene.String(required=True),
        lastname=graphene.String(required=True),
        middlename=graphene.String(required=True),
        page=graphene.Int(required=True),
        number_of_results=graphene.Int(required=True),
        mobile=graphene.String(required=True),
        email=graphene.String(required=True),
        order_by=graphene.String(required=True),
        order_direction=graphene.Int(required=True),
        is_active=graphene.Boolean(required=True)
    )
    total_profit = graphene.Float(
        start_date=graphene.Date(required=True),
        end_date=graphene.Date(),
        address_id=graphene.Int()
    )
    paginated_orders = graphene.Field(
        OrderPaginationResult,
        start_date=graphene.Date(required=True),
        end_date=graphene.Date(),
        address_id=graphene.Int(),
        page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=10)
    )

    drivers_search = graphene.List(
        UserType
    )

    @login_required_resolver
    def resolve_drivers_search(self, info):
        return User.objects.filter(is_driver=True)

    @login_required_resolver
    def resolve_total_profit(self, info, start_date, end_date=None, address_id=None):
        start_of_day = make_aware(datetime.datetime.combine(start_date, datetime.time.min))
        end_of_day = make_aware(datetime.datetime.combine(end_date or start_date, datetime.time.max))

        if address_id:
            try:
                address = Address.objects.get(id=address_id)
                orders = address.orders.filter(
                    orderedAt__range=(start_of_day, end_of_day),
                    isActive=True,
                    deliveredAt__isnull=False
                )
            except Address.DoesNotExist:
                return 0.0
        else:
            orders = Order.objects.filter(
                orderedAt__range=(start_of_day, end_of_day),
                isActive=True,
                deliveredAt__isnull=False
            )

        total_profit = orders.annotate(
            profit=(F('item__price') - F('item__buyPrice')) * F('quantity') * (1 - F('discount') / 100)
        ).aggregate(total_profit=Sum('profit'))['total_profit'] or 0.0

        return round(total_profit, 2)

    @login_required_resolver
    def resolve_paginated_orders(self, info, start_date, end_date=None, address_id=None, page=1, page_size=10):
        start_of_day = make_aware(datetime.datetime.combine(start_date, datetime.time.min))
        end_of_day = make_aware(datetime.datetime.combine(end_date or start_date, datetime.time.max))

        address = None
        orders = []
        if address_id:
            try:
                address = Address.objects.get(id=address_id)
                orders = address.orders.filter(
                    orderedAt__range=(start_of_day, end_of_day),
                    isActive=True,
                )
            except Address.DoesNotExist:
                return OrderPaginationResult(orders=[], address=address, total_pages=0)
        else:
            orders = Order.objects.filter(
                orderedAt__range=(start_of_day, end_of_day),
                isActive=True,
                deliveredAt__isnull=False
            )

        # Prefetch related data
        orders = orders.prefetch_related('item')

        # Apply pagination
        paginator = Paginator(orders, page_size)
        try:
            paginated_orders = paginator.page(page)
        except EmptyPage:
            return OrderPaginationResult(orders=[], address=address, totalPages=paginator.num_pages)

        return OrderPaginationResult(
            orders=paginated_orders.object_list,
            address=address,
            total_pages=paginator.num_pages,
        )

    @login_required_resolver
    def resolve_all_items(self, info):
        return Item.objects.all()
    
    @login_required_resolver
    def resolve_customer_by_id(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    @login_required_resolver
    def resolve_address_by_id(self, info, id):
        try:
            return Address.objects.get(id=id)
        except Address.DoesNotExist:
            return None
    
            
    @login_required_resolver
    def resolve_user_by_id(self, info, id):
        try:
            return User.objects.get(id=id)
        except User.DoesNotExist:
            return None
        
    @login_required_resolver
    def resolve_item_by_id(self, info, id):
        try:
            return Item.objects.get(id=id)
        except Item.DoesNotExist:
            return None

    @login_required_resolver   
    def resolve_order_by_id(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None
    
    @login_required_resolver
    def resolve_employees_search(self, info, username, firstname, email, mobile, lastname, middlename, page, number_of_results, order_by, order_direction, is_active):
        user = info.context.user
        # Initial name-based filter
        queryset = User.objects.filter(
            first_name__icontains=firstname,
            middle_name__icontains=middlename,
            last_name__icontains=lastname,
            is_active=is_active
        ).exclude(id=user.id)

        if username:
            queryset = queryset.filter(username__icontains=username)

        if mobile:
            queryset = queryset.filter(phone_number__icontains=mobile)

        if email:
            queryset = queryset.filter(email__icontains=email)

        # Handle ordering logic
        if order_by == "name":
            queryset = queryset.order_by("first_name", "last_name", "middle_name")
        elif order_by == "createdAt":
            queryset = queryset.order_by("date_joined")  # Adjust field name if necessary

        # If order_direction is -1, reverse the order
        if order_direction == -1:
            queryset = queryset.reverse()

        # Paginate the queryset
        paginator = Paginator(queryset, number_of_results)
        
        # Check if page exists, if not return an empty result
        try:
            paginated_page = paginator.page(page)
        except EmptyPage:
            return EmployeeSearchResult(employees=[], totalPages=paginator.num_pages)
        
        # Return both employees and the total number of pages
        return EmployeeSearchResult(
            employees=paginated_page.object_list,
            totalPages=paginator.num_pages
        )

    @login_required_resolver
    def resolve_customers_search(self, info, firstname, email, mobile, lastname, middlename, page, number_of_results, order_by, order_direction, is_active):
        # Initial name-based filter
        queryset = Customer.objects.filter(
            firstName__icontains=firstname,
            middleName__icontains=middlename,
            lastName__icontains=lastname,
            isActive=is_active
        )

        queryset = queryset.prefetch_related(
            'addresses__mobile_numbers'
        )

        if mobile:
            queryset = queryset.filter(
                Q(addresses__mobile_numbers__mobile__icontains=mobile) |
                Q(addresses__landline__icontains=mobile)
            )

        if email:
            queryset = queryset.filter(
                addresses__email__icontains=email
            )

        # Handle ordering logic
        if order_by == "name":
            queryset = queryset.order_by("firstName", "lastName", "middleName")
        elif order_by == "createdAt":
            queryset = queryset.order_by("createdAt")  # Adjust field name if necessary

        # If order_direction is -1, reverse the order
        if order_direction == -1:
            queryset = queryset.reverse()

        # Paginate the queryset
        paginator = Paginator(queryset, number_of_results)
        
        # Check if page exists, if not return an empty result
        try:
            paginated_page = paginator.page(page)
        except EmptyPage:
            return CustomerSearchResult(customers=[], totalPages=paginator.num_pages)
        
        # Return both customers and the total number of pages
        return CustomerSearchResult(
            customers=paginated_page.object_list,
            totalPages=paginator.num_pages
        )


schema = graphene.Schema(query=Query)
