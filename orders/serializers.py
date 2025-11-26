from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['sku', 'name', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['order_number', 'created_at', 'total_amount', 'status', 'items']
        extra_kwargs = {
            'order_number': {'validators': []}
        }

    def validate_items(self, value):
        skus = [item['sku'] for item in value]
        if len(skus) != len(set(skus)):
            raise serializers.ValidationError("Duplicate SKU in the same order is not allowed.")
        return value

class UploadOrdersSerializer(serializers.Serializer):
    user = serializers.CharField(max_length=50)
    orders = OrderSerializer(many=True)