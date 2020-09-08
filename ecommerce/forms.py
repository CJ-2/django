from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Product

class RegisterForm(forms.Form):
    username = forms.CharField(label=_("username"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=_("email"), widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=_("password"), widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_repeat = forms.CharField(label=_("password_repeat"),
                                      widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label=_("first_name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label=_("last_name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label=_("phone_number"), widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   required=False)


class AccountForm(forms.Form):
    username = forms.CharField(label=_("username"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=_("email"), widget=forms.EmailInput(attrs={'class': 'form-control'}))
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if no change'}),
        required=False, label=_("old_password"))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if no change'}),
        required=False, label=_("password"))
    password_repeat = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank if no change'}),
        required=False, label=_("password_repeat"))
    first_name = forms.CharField(label=_("first_name"), widget=forms.TextInput(attrs={'class': 'form-control'}, ))
    last_name = forms.CharField(label=_("last_name"), widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label=_("phone_number"), widget=forms.NumberInput(attrs={'class': 'form-control'}),
                                   required=False)
    about_me = forms.CharField(label=_("about_me"),
                               widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'ck-editor-area'}),
                               required=False)


class CreateProductForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'ck-editor-area'}))
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '7'}), required=False)
    price = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}))
    status = forms.CharField(
        widget=forms.Select(choices=(('1', 'Active'), ('0', 'Inactive'),), attrs={'class': 'form-control'}))
    quantity = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class UpdateProductForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'ck-editor-area'}))
    excerpt = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '7'}), required=False)
    images = forms.CharField(widget=forms.FileInput(
        attrs={'class': 'form-control image-input', 'accept': 'image/*', 'multiple': 'multiple'}), required=False)
    price = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Amount'}))
    status = forms.CharField(
        widget=forms.Select(choices=(('1', 'Active'), ('0', 'Inactive'),), attrs={'class': 'form-control'}))
    quantity = forms.CharField(widget=forms.NumberInput(attrs={'class': 'form-control'}))


class Product_Create(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('featured_image',)
