from .models import Customer, Address, PhoneNumber
from helpers.views import BaseView
from .serializers import CustomerSerializer, AddressSerializer, PhoneNumberSerializer
from rest_framework.permissions import IsAdminUser

class CustomerDetailView(BaseView):
    permission_classes = [IsAdminUser]
    
    Serializer = CustomerSerializer
    Model = Customer

class AddressDetailView(BaseView):
    permission_classes = [IsAdminUser]

    Serializer = AddressSerializer
    Model = Address

class PhoneNumberDetailView(BaseView):
    permission_classes = [IsAdminUser]

    Serializer = PhoneNumberSerializer
    Model = PhoneNumber