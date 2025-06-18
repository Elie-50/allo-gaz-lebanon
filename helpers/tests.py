from django.urls import reverse
from rest_framework.test import APITestCase
from item.models import Item, Source
from user.models import User
from order.models import Order, ExchangeRate
from user.models import User
from customer.models import Customer, Address
from helpers.util import create_dummy_image


class BaseTestCase(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin', password='adminpass', is_staff=True, is_superuser=True
        )

        self.user = User.objects.create_user(
            username='staff', password='staff_password', is_staff=True, is_superuser=False
        )

        self.item = Item.objects.create(
            name='item 1', stockQuantity=10, price=5, type="type 1", buyPrice=2
        )

        self.item2 = Item.objects.create(
            name='item 2', stockQuantity=15, price=5, type="type 1", buyPrice=2
        )

        self.source = Source.objects.create(
            item=self.item,
            name="Source A",
            price=5
        )

        # Create a customer to use in PUT and DELETE tests
        self.customer = Customer.objects.create(
            firstName="John",
            lastName="Doe",
            middleName="Steve"
        )

        self.dummy_image = create_dummy_image()

        
        self.address = Address.objects.create(
            customer=self.customer,
            email="example1@example.com",
            landline="",
            link="link",
            image=create_dummy_image(),
            region="Zgharta",
            street="Street 123",
            building="Abou Walid",
            floor="Ground Floor"
        )

        self.order = Order.objects.create(
            customer=self.customer,
            user=self.admin_user,
            item=self.item2,
            quantity=5,
            address=self.address,
            liraRate=90000
        )

        # Get JWT token
        response = self.client.post(
            reverse('login'),
            {'username': 'admin', 'password': 'adminpass'},
            format='json'
        )
        self.token = response.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

class GraphQLTestCase(BaseTestCase):
    def graphql(self, query, variables=None):
        return self.client.post(
            "/graphql/", 
            data={"query": query, "variables": variables}, 
            content_type="application/json",
            **self.auth_header
        )