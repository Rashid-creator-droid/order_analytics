from celery import shared_task
from django.db.models import Sum
from orders.models import DailyStats, User, Order
from django.utils.timezone import now


@shared_task(bind=True)
def daily_order_stats(self):
    today = now().date()
    users = User.objects.all()

    for user in users:
        orders = Order.objects.filter(user=user, created_at__date=today)
        orders_count = orders.count()
        total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
        avg_order_value = total_revenue / orders_count if orders_count else 0

        DailyStats.objects.create(
            user=user,
            date=today,
            orders_count=orders_count,
            total_revenue=total_revenue,
            avg_order_value=avg_order_value
        )
    return f'{len(users)} users processed, date={today}'