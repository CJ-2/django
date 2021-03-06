from django.conf.urls import include, url
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'ecommerce'  # This will be like this: {% url 'ecommerce:detail' item.id %} on our templates.
urlpatterns = [
                  url(r'^$', views.index, name='index'),
                  url(r'^products/$', views.products, name='products'),
                  url(r'^product/(?P<product_id>[0-9]+)/$', views.single_product, name='single_product'),
                  url(r'^about/$', views.about, name='about'),
                  url(r'^contact/$', views.contact, name='contact'),
                  url(r'^cart/$', views.cart, name='cart'),
                  url(r'^checkout/$', views.checkout, name='checkout'),
                  url(r'^payment-paypal$', views.payment_paypal, name='payment-paypal'),
                  url(r'^cash-on-delivery$', views.checkout_cash_on_delivery, name='checkout-cash-on-delivery'),
                  url(r'^cash-on-delivery/order/created/$', views.cash_on_delivery_order_created,
                      name='cash_on_delivery_created'),
                  url(r'^checkout/paypal$', views.checkout_paypal, name='paypal-checkout'),
                  url(r'^checkout/payment/process/$', views.proceed_to_pay, name='proceed-to-pay'),
                  url(r'^search/$', views.product_search, name='search'),
                  url(r'^ALL/$', views.ALL, name='ALL'),
	              url(r'^man/$', views.man, name='man'),
                  url(r'^women/$', views.women, name='women'),
	              url(r'^kids/$', views.kids, name='kids'),
	              url(r'^Devices/$', views.Devices, name='Devices'),
	               url(r'^termsandconditions/$', views.termsandconditions, name='termsandconditions'),
                  url(r'^user/', include([
                      url(r'^login/$', views.user_login, name='user_login'),
                      url(r'^register/$', views.user_register, name='user_register'),
                      url(r'^account/$', views.user_account, name='user_account'),
                      url(r'^products/$', views.user_products, name='user_products'),
                      url(r'^product/create/$', views.user_product_create, name='user_product_create'),
                      url(r'^product/update/(?P<product_id>[0-9]+)/$', views.user_product_update,
                          name='user_product_update'),
                      url(r'^product/update/set-featured-image/', views.set_featured_image),
                      url(r'^product/update/unset-image/$', views.unset_image),
                      url(r'^product/unset-product/$', views.unset_product),
                      url(r'^logout/$', views.logout),
                  ])),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
