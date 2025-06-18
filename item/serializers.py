from rest_framework import serializers
from .models import Item, Source
from rest_framework.exceptions import PermissionDenied

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
        if value <= 0:
            raise serializers.ValidationError("Price must be a positive number.")
        return value
    
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