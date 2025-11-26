from django.contrib import admin
from .models import User, Order, OrderItem, DailyStats


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('sku', 'name', 'quantity', 'price')
    readonly_fields = ('sku', 'name', 'quantity', 'price')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'created_at', 'total_amount', 'status')
    search_fields = ('order_number', 'user__username', 'status')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username']

@admin.register(DailyStats)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'orders_count']