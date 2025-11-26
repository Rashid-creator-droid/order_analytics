from django.db import models
from django.utils.timezone import now


class User(models.Model):
    """User model"""
    username = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.username


class Order(models.Model):
    """Order model"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    """Order Item model"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    sku = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('order', 'sku')

    def __str__(self):
        return self.name

class DailyStats(models.Model):
    """Daily Stats model"""
    user = models.ForeignKey('orders.User', on_delete=models.CASCADE)
    date = models.DateField(default=now)
    orders_count = models.IntegerField()
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2)
    avg_order_value = models.DecimalField(max_digits=12, decimal_places=2)
