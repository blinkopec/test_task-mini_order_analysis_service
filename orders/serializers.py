from orders.models import Order, OrderItem
from rest_framework import serializers

class OrderItemSeriazlier(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('sku', 'name', 'quantity', 'price')

    def create(self, validated_data):
         obj, created = OrderItem.objects.update_or_create(
            sku=validated_data['sku'],
            defaults=validated_data
            )
         return obj



class OrderSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(validators=[]) 
    items = OrderItemSeriazlier(many=True)

    class Meta:
        model =  Order
        fields = ('user', 'order_number', 'created_at', 'total_amount', 'status', 'items')
        read_only_fields = ('created_at',)
            

    def create(self, validated_data):
        items = validated_data.pop("items")

        order, created = Order.objects.update_or_create(
            order_number=validated_data["order_number"],
            defaults=validated_data
        )

        # Обновляем позиции
        order.items.all().delete()
        for item in items:
            OrderItem.objects.create(order=order, **item)

        return order

