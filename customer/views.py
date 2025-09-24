from .models import Customer, Address, PhoneNumber
from helpers.views import BaseView
from .serializers import CustomerSerializer, AddressSerializer, PhoneNumberSerializer
from rest_framework.permissions import IsAdminUser
from rest_framework.exceptions import AuthenticationFailed, NotFound
from rest_framework.response import Response
from rest_framework import status

class CustomerDetailView(BaseView):
    permission_classes = [IsAdminUser]
    
    Serializer = CustomerSerializer
    Model = Customer

    def delete(self, request, pk):
        if not request.user.is_active:
            raise AuthenticationFailed("Access Denied")
        
        try:
            customer = Customer.objects.get(id=pk)
        except Customer.DoesNotExist:
            raise NotFound("Customer not found")
        
        customer.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
    
class AddressDetailView(BaseView):
    permission_classes = [IsAdminUser]

    Serializer = AddressSerializer
    Model = Address

class PhoneNumberDetailView(BaseView):
    permission_classes = [IsAdminUser]

    Serializer = PhoneNumberSerializer
    Model = PhoneNumber