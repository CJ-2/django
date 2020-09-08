from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin

urlpatterns = i18n_patterns(
        url(r'^ecommerce/', include('ecommerce.urls')),  # Include ecommerce app views.
        url(r'^admin/', admin.site.urls),

)


