from django import forms
from django_countries.widgets import CountrySelectWidget
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'street_address', 'country', 'city', 'state', 'postal_code',
                  'email', 'phone', 'additional_information']

        widgets = {'country': CountrySelectWidget()}

    def clean(self):
        cleaned_data = super(OrderCreateForm, self).clean()
        first_name = cleaned_data.get('first_name')
        address = cleaned_data.get('address')
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        if not first_name and not email and not address and not phone:
            raise forms.ValidationError('You have to write something!')
