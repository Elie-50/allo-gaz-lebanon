from .models import *
from rest_framework import serializers
from django.db import IntegrityError

class AddressSerializer(serializers.ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=Customer.objects.all(), write_only=True, required=False)
    image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = Address
        fields = '__all__'


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
    


class PhoneNumberSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), write_only=True, required=False)
    class Meta:
        model = PhoneNumber
        fields = '__all__'