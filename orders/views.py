from django.db import transaction, connection
from django.db.models import Sum
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import User, Order, OrderItem
from .serializers import UploadOrdersSerializer
import logging

logger = logging.getLogger(__name__)


class UploadOrdersView(APIView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = UploadOrdersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data['user']
        orders_data = serializer.validated_data['orders']

        user, _ = User.objects.get_or_create(username=user_data)

        items_to_create = []
        items_to_update = []

        existing_orders = {o.order_number: o for o in Order.objects.filter(order_number__in=[o['order_number'] for o in orders_data])}

        for order_data in orders_data:
            order_number = order_data['order_number']
            order_instance = existing_orders[order_number]
            items_data = order_data.get('items', [])

            existing_items_qs = OrderItem.objects.filter(order=order_instance)
            existing_items = {i.sku: i for i in existing_items_qs}

            incoming_skus = set(item['sku'] for item in items_data)

            skus_to_delete = set(existing_items.keys()) - incoming_skus
            if skus_to_delete:
                OrderItem.objects.filter(order=order_instance, sku__in=skus_to_delete).delete()

            items_to_create = []
            items_to_update = []

            for item_data in items_data:
                sku = item_data['sku']
                if sku in existing_items:
                    item = existing_items[sku]
                    if (item.name != item_data['name'] or
                            item.quantity != item_data['quantity'] or
                            item.price != item_data['price']):
                        item.name = item_data['name']
                        item.quantity = item_data['quantity']
                        item.price = item_data['price']
                        items_to_update.append(item)
                else:
                    items_to_create.append(OrderItem(order=order_instance, **item_data))

        if items_to_create:
            OrderItem.objects.bulk_create(items_to_create)
        if items_to_update:
            OrderItem.objects.bulk_update(items_to_update, ['name', 'quantity', 'price'])
        for q in connection.queries:
            print(q['sql'])

        return Response({"detail": "Orders uploaded successfully"}, status=status.HTTP_200_OK)


class UserStatsView(APIView):

    def get(self, request):
        username = request.query_params.get('user')
        if not username:
            return Response({"error": "User query param is required"}, status=400)

        user_obj = get_object_or_404(User, username=username)

        orders = user_obj.orders.all()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        orders_count = orders.count()
        avg_order_value = total_revenue / orders_count if orders_count else 0

        return Response({
            "user": username,
            "orders_count": orders_count,
            "total_revenue": float(total_revenue),
            "avg_order_value": float(avg_order_value)
        })