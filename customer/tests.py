from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from customer.models import Address, PhoneNumber, Customer
from helpers.util import create_dummy_image
from helpers.tests import BaseTestCase

class CustomerTestCase(BaseTestCase):
    def test_create_customer(self):
        url = reverse('customer-list')
        data = {
            "firstName": "Alice",
            "lastName": "Smith",
            "middleName": "Eve"
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['firstName'], 'Alice')
        self.assertEqual(Customer.objects.count(), 2)

    def test_create_customer_duplicate_name(self):
        url = reverse('customer-list')
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "middleName": "Steve"
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_not_logged_in(self):
        url = reverse('customer-list')
        data = {
            "firstName": "Alice",
            "lastName": "Smith",
            "middleName": "Eve"
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_customer(self):
        url = reverse('customer-detail', args=[self.customer.id])
        data = {
            "firstName": "Johnny",
            "lastName": "Updated",
            "middleName": "Steve"
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['firstName'], 'Johnny')
        self.assertEqual(response.data['lastName'], 'Updated')

    def test_update_customer_name_exists(self):
        customer = Customer.objects.create(
            firstName="Johnny",
            lastName="Doe",
            middleName="Steve"
        )
        url = reverse('customer-detail', args=[customer.id])
        data = {
            "firstName": "John",
            "lastName": "Doe",
            "middleName": "Steve"
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    
    def test_hard_delete_customer(self):
        url = reverse('customer-detail', args=[self.customer.id])
        id = self.customer.id
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Confirm hard delete
        still_exists = Customer.objects.filter(id=id).exists()
        self.assertFalse(still_exists)

class AddressTestCase(BaseTestCase):
    def test_add_address_to_customer(self):
        url = reverse('add-address')
        data = {
            "customer": self.customer.id,
            "email": "email1@example.com",
            "landline": "",
            "link": "some link",
            "image": self.dummy_image,
            "region": "Zgharta",
            "Street": "Street 42",
            "building": "Abou Samir",
            "floor": "2nd floor"
        }

        response = self.client.post(url, data, format='multipart', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['link'], 'some link')
        self.assertEqual(response.data['building'], 'Abou Samir')


    def test_update_address(self):
        address = Address.objects.create(
            customer=self.customer, 
            email="email2@example.com", 
            image=self.dummy_image, 
            link="test link",
            region="Zgharta",
            street="Street 123",
            building="Abou Walid",
            floor="Ground Floor"
        )

        url = reverse('edit-address', args=[address.id])
        data = {
            "link": "another_link",
            "email": "email2@example.com",
            "image": create_dummy_image(),
            "region": "Ehden"
        }
        response = self.client.put(url, data, format='multipart', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'email2@example.com')
        self.assertEqual(response.data['region'], 'Ehden')
    
    def test_update_address_no_image(self):
        address = Address.objects.create(
            customer=self.customer, 
            email="email3@example.com",
            image=self.dummy_image,
            link="test link",
            region="Zgharta",
            street="Street 123",
            building="Abou Walid",
            floor="Ground Floor"
        )

        url = reverse('edit-address', args=[address.id])
        data = {
            "landline": "06111000",
            "link": "another_link",
            "email":"email3@example.com"
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['landline'], '06111000')

    def test_delete_address(self):
        address = Address.objects.create(
            customer=self.customer, 
            email="email3@example.com",
            image=self.dummy_image,
            link="test link",
            region="Zgharta",
            street="Street 123",
            building="Abou Walid",
            floor="Ground Floor"
        )
        url = reverse('edit-address', args=[address.id])

        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

class PhoneNumberTestCase(BaseTestCase):
    def test_create_phone_number(self):
        url = reverse('add-phone-number')
        data = {
            "address": self.address.id,
            "mobile": "+1234467891",
            "priority": 1
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['mobile'], '+1234467891')

        self.address.refresh_from_db()
        self.assertEqual(self.address.mobile_numbers.count(), 1)

    def test_edit_phone_number(self):
        pn = PhoneNumber.objects.create(address=self.address, mobile='1234467891', priority=1)
        url = reverse('edit-phone-number', args=[pn.id])
        data = {
            "mobile": "+1234567891",
            "priority": 2
        }

        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['priority'], 2)

        self.address.refresh_from_db()
        self.assertEqual(self.address.mobile_numbers.get(pk=pn.id).priority, 2)

    def test_delete_address(self):
        pn = PhoneNumber.objects.create(address=self.address, mobile='123456', priority=1)
        url = reverse('edit-phone-number', args=[pn.id])

        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)