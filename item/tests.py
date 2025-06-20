from django.urls import reverse
from rest_framework import status
from .models import Item, Source
from helpers.tests import BaseTestCase,  GraphQLTestCase

class ItemTestCase(BaseTestCase):
    def test_create_item(self):
        url = reverse('add-item')
        data = {
            "name": "item_name",
            "stockQuantity": 5,
            "price": 10,
            "type": "type 1",
            "buyPrice": 5,
            "tva": True
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'item_name')
    
    def test_create_item_invalid_price(self):
        url = reverse('add-item')
        data = {
            "name": "item_name",
            "stockQuantity": 5,
            "price": 0,
            "type": "type 1",
            "buyPrice": 5
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_item_invalid_quantity(self):
        url = reverse('add-item')
        data = {
            "name": "item_name",
            "stockQuantity": -1,
            "price": 10,
            "type": "type 1",
            "buyPrice": 5
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_item(self):
        url = reverse('edit-item', args=[self.item.id])
        data = {
            "name": self.item.name,
            "stockQuantity": 20,
            "price": self.item.price,
            "type": self.item.type,
            "buyPrice": 5
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.item.refresh_from_db()
        self.assertEqual(self.item.stockQuantity, 20)

    def test_update_item_invalid_user(self):
        url = reverse('edit-item', args=[self.item.id])
        data = {
            "name": self.item.name,
            "stockQuantity": 20,
            "price": 20,
            "type": self.item.type,
            "buyPrice": 5
        }
        
        # Get JWT token
        res = self.client.post(
            reverse('login'),
            {'username': 'staff', 'password': 'staff_password'},
            format='json'
        )
        token = res.data['access']
        auth_header = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        response = self.client.put(url, data, format='json', **auth_header)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.item.refresh_from_db()
        self.assertEqual(self.item.price, 5)
        self.assertEqual(self.item.buyPrice, 2)
        

    def test_soft_delete_item(self):
        url = reverse('edit-item', args=[self.item.id])
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(Item.objects.filter(id=self.item.id).exists())
        self.assertFalse(Item.objects.get(id=self.item.id).isActive)


class SourceTestCase(BaseTestCase):
    def test_create_source(self):
        url = reverse('add-source')
        data = {
            "item": self.item.id,
            "name": "source 1",
            "price": 10,
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'source 1')
    
    def test_create_source_invalid_price(self):
        url = reverse('add-source')
        data = {
            "item": self.item.id,
            "name": "source C",
            "price": 0,
        }

        response = self.client.post(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_update_source(self):
        url = reverse('edit-source', args=[self.source.id])
        data = {
            "item": self.item.id,
            "name": "Source A1",
            "price": 5,
        }
        response = self.client.put(url, data, format='json', **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        

    def test_soft_delete_item(self):
        url = reverse('edit-source', args=[self.source.id])
        response = self.client.delete(url, **self.auth_header)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertTrue(Source.objects.filter(id=self.source.id).exists())
        self.assertFalse(Source.objects.get(id=self.source.id).isActive)

# class ItemGraphQLTestCase(GraphQLTestCase):
#     def test_item_by_id(self):
#         item = Item.objects.create(name="X", price=10, buyPrice=5)
#         query = """query { itemById }"""
#         response = self.graphql(query)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    