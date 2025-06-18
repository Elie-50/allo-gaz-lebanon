from rest_framework import serializers
from item.models import Item
from item.serializers import ItemSerializer
from .models import Order, ExchangeRate
from user.models import User

class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    # Accept item as ID when writing (POST/PUT)
    item = serializers.PrimaryKeyRelatedField(queryset=Item.objects.all(), write_only=True)
    
    # Return full item data when reading
    item_data = ItemSerializer(source='item', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def to_representation(self, instance):
        """Custom output: replace item ID with full item data"""
        rep = super().to_representation(instance)
        rep['item'] = rep.pop('item_data')  # Replace 'item' field with full item data
        return rep
    
    
    def validate(self, attrs):
        item = attrs['item']
        quantity = attrs['quantity']
        
        if item.stockQuantity < quantity:
            raise serializers.ValidationError(
                {'quantity': f"Only {item.stockQuantity} units available in stock."}
            )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')    
        validated_data['user'] = request.user

        
        item = validated_data['item']
        quantity = validated_data['quantity']

        # Deduct stock
        item.stockQuantity -= quantity
        item.save()

        # Return the created order
        return super().create(validated_data)


    def update(self, instance, validated_data):
        # Get new and old quantity
        new_quantity = validated_data.get('quantity', instance.quantity)
        item = validated_data.get('item', instance.item)

        # Adjust stock if quantity or item changed
        if item == instance.item:
            quantity_difference = new_quantity - instance.quantity
        else:
            # Restore old item's stock
            instance.item.stockQuantity += instance.quantity
            instance.item.save()
            quantity_difference = new_quantity
            item = validated_data['item']

        if item.stockQuantity < quantity_difference:
            raise serializers.ValidationError(
                {'quantity': f"Only {item.stockQuantity} units available in stock."}
            )

        item.stockQuantity -= quantity_difference
        item.save()

        return super().update(instance, validated_data)

class ExchangeRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExchangeRate
        fields = ['rate']