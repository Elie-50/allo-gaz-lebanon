# import datetime
# import pytest
# from customer.models import Customer, Address
# from item.models import Item
# from order.models import Order
# from user.models import User
# from django.utils.timezone import make_aware
# from django.test import Client

# @pytest.mark.django_db
# class TestGraphQLResolvers:
#     def setup_method(self):
#         self.client = Client()
#         self.password = "TestPass123!"
#         self.user = User.objects.create_user(
#             username="testuser", password=self.password, is_staff=True
#         )
#         self.client.login(username=self.user.username, password=self.password)

#     def graphql(self, query, variables=None):
#         return self.client.post("/graphql/", data={"query": query, "variables": variables}, content_type="application/json")

#     def test_drivers_search(self):
#         User.objects.create(username="driver1", is_driver=True)
#         query = """query { driversSearch { id username } }"""
#         response = self.graphql(query)
#         assert response.status_code == 200
#         assert "driversSearch" in response.json()["data"]

#     def test_orders_search(self):
#         item = Item.objects.create(name="Item A", price=100, buyPrice=50)
#         order_date = make_aware(datetime.datetime.now())
#         order = Order.objects.create(
#             item=item,
#             quantity=2,
#             discount=10,
#             orderedAt=order_date,
#             deliveredAt=order_date,
#             isActive=True
#         )
#         start_date = order_date.date().isoformat()
#         query = """
#         query ($startDate: Date!) {
#             ordersSearch(startDate: $startDate) {
#                 totalProfit
#                 orders { id }
#             }
#         }
#         """
#         variables = {"startDate": start_date}
#         response = self.graphql(query, variables)
#         assert response.status_code == 200
#         assert "ordersSearch" in response.json()["data"]

#     def test_all_items(self):
#         query = """query { allItems { id name } }"""
#         response = self.graphql(query)
#         assert response.status_code == 200
#         assert "allItems" in response.json()["data"]

#     def test_customer_by_id(self):
#         customer = Customer.objects.create(firstName="John", lastName="Doe")
#         query = f"""query {{ customerById(id: "{customer.id}") {{ id firstName }} }}"""
#         response = self.graphql(query)
#         assert response.status_code == 200
#         assert response.json()["data"]["customerById"]["id"] == str(customer.id)

#     def test_address_by_id(self):
#         address = Address.objects.create(street="123 Street")
#         query = f"""query {{ addressById(id: "{address.id}") {{ id street }} }}"""
#         response = self.graphql(query)
#         assert response.status_code == 200

#     def test_user_by_id(self):
#         query = f"""query {{ userById(id: "{self.user.id}") {{ id username }} }}"""
#         response = self.graphql(query)
#         assert response.status_code == 200
#         assert response.json()["data"]["userById"]["username"] == self.user.username

#     def test_item_by_id(self):
#         item = Item.objects.create(name="X", price=10, buyPrice=5)
#         query = f"""query {{ itemById(id: "{item.id}") {{ id name }} }}"""
#         response = self.graphql(query)
#         assert response.status_code == 200

#     def test_order_by_id(self):
#         item = Item.objects.create(name="Test Item", price=10, buyPrice=5)
#         order = Order.objects.create(item=item, quantity=1, orderedAt=make_aware(datetime.datetime.now()), deliveredAt=make_aware(datetime.datetime.now()), isActive=True)
#         query = f"""query {{ orderById(id: "{order.id}") {{ id }} }}"""
#         response = self.graphql(query)
#         assert response.status_code == 200

#     def test_employees_search(self):
#         User.objects.create(username="employee1", first_name="Alex", last_name="Smith", email="alex@example.com", phone_number="123456789")
#         query = """
#         query {
#             employeesSearch(
#                 username: "", firstname: "Alex", email: "", mobile: "", lastname: "Smith", middlename: "", 
#                 page: 1, numberOfResults: 10, orderBy: "name", orderDirection: 1
#             ) {
#                 employees { id username }
#                 totalPages
#             }
#         }
#         """
#         response = self.graphql(query)
#         assert response.status_code == 200
#         assert "employees" in response.json()["data"]["employeesSearch"]

#     def test_customers_search(self):
#         Customer.objects.create(firstName="Jane", lastName="Doe", middleName="X")
#         query = """
#         query {
#             customersSearch(
#                 firstname: "Jane", email: "", mobile: "", lastname: "Doe", middlename: "X", 
#                 page: 1, numberOfResults: 10, orderBy: "name", orderDirection: 1
#             ) {
#                 customers { id firstName }
#                 totalPages
#             }
#         }
#         """
#         response = self.graphql(query)
#         assert response.status_code == 200
#         assert "customers" in response.json()["data"]["customersSearch"]
