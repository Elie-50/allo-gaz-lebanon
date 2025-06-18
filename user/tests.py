from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User
from helpers.tests import BaseTestCase

class UserTestCase(BaseTestCase):
    def test_get_user(self):
        url = reverse('user-detail')

        response = self.client.get(url, **self.auth_header)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('is_superuser', response.data)

    def test_create_user(self):
        url = reverse('add-user')
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "username": "AliceSmith",
            "phone_number": "+123465789",
            "password": "test_password",
            "is_staff": True
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['first_name'], 'Alice')
        user = User.objects.get(username='AliceSmith')
        self.assertTrue(user.check_password("test_password"))

    def test_create_user_no_password(self):
        url = reverse('add-user')
        data = {
            "first_name": "Alice",
            "last_name": "Smith",
            "username": "AliceSmith",
            "phone_number": "123465789",
            "is_staff": True
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_update_user_password(self):
        url = reverse('edit-user', args=[self.user.id])
        data = {
            "username": "staff",
            "first_name": "Johnny",
            "last_name": "Updated",
            "password": "new_password"
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Johnny')
        self.assertEqual(response.data['last_name'], 'Updated')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("new_password"))

    def test_update_user(self):
        url = reverse('edit-user', args=[self.user.id])
        data = {
            "username": "staff",
            "first_name": "Johnny",
            "last_name": "Updated",
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Johnny')
        self.assertEqual(response.data['last_name'], 'Updated')

    def test_soft_delete_user(self):
        url = reverse('edit-user', args=[self.user.id])
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Refresh from DB and confirm soft delete
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class LoginTestCase(APITestCase):
    def setUp(self):
        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email="admin@example.com",
            phone_number="99912345678",
            password='adminpass',
            is_staff=True,
            is_superuser=True
        )

    def test_login_via_email(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'admin@example.com', 'password': 'adminpass'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_via_phone_number(self):
        response = self.client.post(
            reverse('login'),
            {'username': '99912345678', 'password': 'adminpass'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_via_username(self):
        response = self.client.post(
            reverse('login'),
            {'username': 'admin', 'password': 'adminpass'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)