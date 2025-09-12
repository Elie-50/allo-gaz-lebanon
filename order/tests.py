from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from user.models import User
from .models import Order, ExchangeRate
from helpers.tests import BaseTestCase
from datetime import date

class OrderTestCase(BaseTestCase):
    def test_create_order(self):
        url = reverse('add-order')
        data = {
            "customer": self.customer.id,
            "item": self.item.id,
            "quantity": 5,
            "address": self.address.id,
            "liraRate": 89000,
            "driver": self.driver.id
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.item.refresh_from_db()

        self.assertEqual(self.item.stockQuantity, 5)
        self.assertEqual(response.data['user'], self.admin_user.id)
    
    def test_create_order_invalid_quantity(self):
        url = reverse('add-order')
        data = {
            "customer": self.customer.id,
            "item": self.item.id,
            "quantity": 15,
            "address": self.address.id,
            "liraRate": 89000,
            "driver": self.driver.id
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order(self):
        url = reverse('edit-order', args=[self.order.id])
        data = {
            "customer": self.customer.id,
            "item": self.item2.id,
            "quantity": 10,
            "address": self.address.id,
            "liraRate": 89000,
            "driver": self.driver.id
        }

        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.item2.refresh_from_db()
        self.assertEqual(self.item2.stockQuantity, 10)

    def test_update_order_change_item(self):
        url = reverse('edit-order', args=[self.order.id])
        data = {
            "customer": self.customer.id,
            "item": self.item.id,
            "quantity": 5,
            "address": self.address.id,
            "liraRate": 89000,
            "driver": self.driver.id
        }

        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.item2.refresh_from_db()
        self.assertEqual(self.item2.stockQuantity, 20)

        self.item.refresh_from_db()
        self.assertEqual(self.item.stockQuantity, 5)

    def test_soft_delete_order(self):
        url = reverse('edit-order', args=[self.order.id])
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(Order.objects.filter(id=self.order.id).exists())
        self.assertFalse(Order.objects.get(id=self.order.id).isActive)

        self.item2.refresh_from_db()
        self.assertEqual(self.item2.stockQuantity, 20)

        

class ExchangeRateViewTests(APITestCase):

    def setUp(self):
        self.url = reverse('exchange-rate')

        self.admin_user = User.objects.create_user(
            username='admin', password='adminpass', is_superuser=True, is_staff=True
        )

        # Get JWT token
        response = self.client.post(
            reverse('login'),
            {'username': 'admin', 'password': 'adminpass'},
            format='json'
        )
        self.token = response.data['access']
        self.auth_header = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}


        # Ensure no ExchangeRate exists
        ExchangeRate.objects.all().delete()
    def test_get_creates_default_exchange_rate_if_not_exists(self):
        response = self.client.get(self.url,  **self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('rate', response.data)
        self.assertEqual(response.data['rate'], 89000)

        # Ensure it was actually created in the DB
        self.assertEqual(ExchangeRate.objects.count(), 1)

    def test_get_returns_existing_exchange_rate(self):
        ExchangeRate.objects.create(rate=90000)
        response = self.client.get(self.url,  **self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rate'], 90000)

    def test_put_updates_exchange_rate(self):
        ExchangeRate.objects.create(rate=88000)
        response = self.client.put(self.url, {'rate': 90000}, format='json',  **self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['rate'], 90000)

        self.assertEqual(ExchangeRate.objects.get().rate, 90000)

class MarkOrdersDeliveredTests(BaseTestCase):
    def test_mark_orders_as_delivered(self):
        # Make sure there's at least one pending order for today
        pending_order = Order.objects.create(
            customer=self.customer,
            user=self.admin_user,
            item=self.item,
            driver=self.driver,
            quantity=3,
            address=self.address,
            status='P',
            liraRate=90000,
        )

        # Build the URL and data payload
        url = reverse('mark-orders-delivered')
        payload = {
            'date': date.today().isoformat(),
            'address_id': self.address.id
        }

        # Send the request
        response = self.client.post(url, payload, format='json', **self.auth_header)

        # Refresh the order from the DB
        pending_order.refresh_from_db()

        # Assertions
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(pending_order.status, 'D')
        self.assertIsNotNone(pending_order.deliveredAt)
        self.assertIn('message', response.data)
        self.assertIn('order(s) marked as delivered', response.data['message'])