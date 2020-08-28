from django.contrib import admin
from apps.order_manager.models import Customer, Order
# Register your models here.

admin.site.register(Customer)
admin.site.register(Order)

