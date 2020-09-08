from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _
from ecommerce.models import Product


class Order(models.Model):
    PAYMENT_METHOD = (
        ('COD', _('Cash On Delivery')),
        ('PAYPAL', _('paypal')),
    )

    first_name = models.CharField(verbose_name=_("First Name"), max_length=50)
    last_name = models.CharField(verbose_name=_("Last Name"), max_length=50)
    street_address = models.CharField(verbose_name=_("Street Address"), max_length=250)
    country = CountryField(verbose_name=_("Country"), blank_label='(select country)')
    city = models.CharField(verbose_name=_("City"), max_length=100)
    state = models.CharField(verbose_name=_("State"), max_length=50, default='Punjab')
    postal_code = models.CharField(verbose_name=_("Postal Code"), max_length=20)
    email = models.EmailField(verbose_name="Email", max_length=100)
    phone = models.CharField(verbose_name=_("Phone"), max_length=13)
    additional_information = models.TextField(verbose_name=_("Additional Information"), max_length=400)
    created = models.DateTimeField(verbose_name=_("created"), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_("updated"), auto_now=True)
    payment_method = models.CharField(verbose_name=_("Payment Method"), choices=PAYMENT_METHOD,
                                      max_length=50, blank=True)
    paid = models.BooleanField(verbose_name=_("Paid"), default=False)
    braintree_id = models.CharField(verbose_name=_("Braintree Id"), max_length=150, blank=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")

    def __str__(self):
        return 'Order {}'.format(self.id)


class OrderItem(models.Model):
    TAX_RATE = 0.05
    order = models.ForeignKey(Order,
                              related_name='items',
                              on_delete=models.CASCADE)

    product = models.ForeignKey(Product,
                                related_name='order_items',
                                on_delete=models.CASCADE)
    price = models.FloatField(verbose_name=_("Price"), default=300)
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"), default=1)

    def __str__(self):
        return '{}'.format(self.id)

    class Meta:
        verbose_name = _("Order Items")

