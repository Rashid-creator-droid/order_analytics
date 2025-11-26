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
    """Adds or updates order details"""
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        serializer = UploadOrdersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_data = serializer.validated_data['user']
        orders_data = serializer.validated_data['orders']

        user, created = User.objects.get_or_create(username=user_data)
        logger.info(f'User: {user.username} (created={created})')

        items_to_create = []
        items_to_update = []

        existing_orders = {
            o.order_number: o
            for o in Order.objects.filter(order_number__in=[o['order_number'] for o in orders_data])
        }

        for order_data in orders_data:
            order_number = order_data['order_number']
            if order_number in existing_orders:
                order_instance = existing_orders[order_number]
                logger.info(f'Processing existing order {order_number}')
                order_instance.created_at = order_data['created_at']
                order_instance.total_amount = order_data['total_amount']
                order_instance.status = order_data['status']
                order_instance.save(update_fields=['created_at', 'total_amount', 'status'])
            else:
                order_instance = Order.objects.create(
                    user=user,
                    order_number=order_number,
                    created_at=order_data['created_at'],
                    total_amount=order_data['total_amount'],
                    status=order_data['status']
                )
                existing_orders[order_number] = order_instance
                logger.info(f'Created new order {order_number}')

            items_data = order_data.get('items', [])

            existing_items_qs = OrderItem.objects.filter(order=order_instance)
            existing_items = {i.sku: i for i in existing_items_qs}

            incoming_skus = set(item['sku'] for item in items_data)

            skus_to_delete = set(existing_items.keys()) - incoming_skus
            if skus_to_delete:
                logger.info(f'Deleting items from order {order_number}: {skus_to_delete}')
                OrderItem.objects.filter(order=order_instance, sku__in=skus_to_delete).delete()


            for item_data in items_data:
                sku = item_data['sku']
                if sku in existing_items:
                    item = existing_items[sku]
                    if (item.name != item_data['name'] or
                            item.quantity != item_data['quantity'] or
                            item.price != item_data['price']):
                        logger.info(
                            f'Updating item {sku} in order {order_number}: '
                            f'name {item.name} -> {item_data["name"]}, '
                            f'quantity {item.quantity} -> {item_data["quantity"]}, '
                            f'price {item.price} -> {item_data["price"]}')
                        item.name = item_data['name']
                        item.quantity = item_data['quantity']
                        item.price = item_data['price']
                        items_to_update.append(item)
                else:
                    logger.info(f'Creating new item {sku} in order {order_number}')
                    items_to_create.append(OrderItem(order=order_instance, **item_data))

        if items_to_create:
            logger.info(f'Bulk creating {len(items_to_create)} items')
            OrderItem.objects.bulk_create(items_to_create)
        if items_to_update:
            logger.info(f'Bulk updating {len(items_to_update)} items')
            OrderItem.objects.bulk_update(items_to_update, ['name', 'quantity', 'price'])

        return Response({'detail': 'Orders uploaded successfully'}, status=status.HTTP_200_OK)


class UserStatsView(APIView):
    """Displays user statistics"""
    def get(self, request):
        username = request.query_params.get('user')
        if not username:
            return Response({'error': 'User query param is required'}, status=status.HTTP_400_BAD_REQUEST)

        user_obj = get_object_or_404(User, username=username)

        orders = user_obj.orders.all()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        orders_count = orders.count()
        avg_order_value = total_revenue / orders_count if orders_count else 0

        return Response({
            'user': username,
            'orders_count': orders_count,
            'total_revenue': float(total_revenue),
            'avg_order_value': float(avg_order_value)
        })