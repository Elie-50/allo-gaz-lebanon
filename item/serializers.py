from rest_framework import serializers
from .models import Item, Source
from rest_framework.exceptions import PermissionDenied, ValidationError
from helpers.serializers import BaseSerializer

class ItemSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()
    class Meta:
        model = Item
        fields = '__all__'
    
    def get_imageUrl(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            # Use request.build_absolute_uri to return full URL
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None

    def validate_price(self, value):
        # print("CUSTOM VALIDATE PRICE RAN:", value)
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value
    
    def validate_limit(self, value):
        # print("CUSTOM VALIDATE LIMIT RAN:", value)
        if value < 0:
            raise serializers.ValidationError("Limit must be a positive number.")
        return value
    
    def validate_stockQuantity(self, value):
        print("CUSTOM VALIDATE STOCKQUANTITY RAN:", value)
        if value < 0:
            raise serializers.ValidationError("Quantity must be a positive number.")
        return value
    
    def validate(self, data):
        print("CUSTOM VALIDATE RAN: ", data)
        user = self.context.get('request').user

        buy_price = data.get('buyPrice')
        price = data.get('price')
        stock_quantity = data.get('stockQuantity')
        print(f"I GOT THE BUY  PRICE AS: {buy_price}")
        print(f"I GOT STOCK AS {stock_quantity}")

        if user and user.is_superuser:
            if int(stock_quantity) < 0:
                raise ValidationError({
                    'stockQuantity': "Ensure the stock quantity is more than zero!"
                })
            if buy_price is not None and price is not None and price < buy_price:
                raise serializers.ValidationError({
                    'price': "Selling price must be greater than buying price.",
                    'buyPrice': "Buying price must be less than selling price."
                })
            
            

        return data

    def update(self, instance, validated_data):
        request = self.context.get('request')
        user = request.user if request else None

        if not (user and user.is_superuser):
            # Check if unauthorized change is attempted
            if 'price' in validated_data and validated_data['price'] != instance.price:
                raise PermissionDenied("Only superusers can modify the price.")
            if 'buyPrice' in validated_data and validated_data['buyPrice'] != instance.buyPrice:
                raise PermissionDenied("Only superusers can modify the buy price.")

        return super().update(instance, validated_data)

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = '__all__'

    # Optional: You can add additional validation if needed.
    # For example, validating that price is greater than zero (though this is already handled by the model's validator).
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value