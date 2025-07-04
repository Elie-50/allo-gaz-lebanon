from .models import *
from rest_framework import serializers

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

    def validate(self, data):
        firstName = data.get('firstName')
        lastName = data.get('lastName')
        middleName = data.get('middleName')

        # Check for duplicates, excluding the current instance (on update)
        queryset = Customer.objects.filter(
            firstName=firstName,
            lastName=lastName,
            middleName=middleName
        )
        
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError({
                'firstName': "A customer with this name already exists.",
                'lastName': "A customer with this name already exists.",
                'middleName': "A customer with this name already exists."
            })

        return data


class PhoneNumberSerializer(serializers.ModelSerializer):
    address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all(), write_only=True, required=False)
    class Meta:
        model = PhoneNumber
        fields = '__all__'