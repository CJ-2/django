from django.contrib import admin

# Register your models here.
from .models import Order, OrderItem


class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'street_address', 'country', 'city', 'email', 'phone', 'paid', 'braintree_id', 'payment_method')
    list_display_link = ['first_name', 'street_address', 'email']
    search_fields = ('email', 'street_address', 'paid', 'braintree_id')


admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)
