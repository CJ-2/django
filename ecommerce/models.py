from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save, pre_save


class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(verbose_name=_("Phone Number"), max_length=30)
    about = models.TextField(verbose_name=_("About"))

    class Meta:
        verbose_name = _("Member")
        verbose_name_plural = _("Members")


class Product(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=200)
    content = models.TextField(verbose_name=_("Content"))
    excerpt = models.TextField(verbose_name=_("Excerpt"))
    price = models.DecimalField(verbose_name=_("Price"), max_digits=20, decimal_places=2)
    status = models.IntegerField(verbose_name=_("Status"), default=0)
    date = models.DateTimeField(verbose_name=_("Date"), auto_now_add=True)
    quantity = models.PositiveIntegerField(verbose_name=_("Quantity"))
    author = models.PositiveIntegerField(verbose_name=_("Author"))
    featured_image = models.CharField(verbose_name=_("Featured_image"), max_length=300)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Product")
        verbose_name_plural = _("Products")


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    product_location = '/ar/ecommerce/media/products/' + str(instance.product.id)
    fs = FileSystemStorage(location=product_location)
    uploaded_file_url = product_location + '/' + filename
    return uploaded_file_url


class Image(models.Model):
    product = models.ForeignKey(Product, verbose_name=_("Product"), on_delete=models.CASCADE)
    image = models.ImageField(verbose_name=_("Image"))

    class Meta:
        verbose_name = _("Image")
        verbose_name_plural = _("Images")

# def save(self, *args, **kwargs):
#     product_location = 'media/products/' + str(instance.product.id)
#     fs = FileSystemStorage(location=product_location)
#     uploaded_file_url = product_location + '/' + filename
#     return uploaded_file_url
#
#
#     p = Product.objects.get(id=self.product.id)
#
#     p.featured_image = "products/{0}/{1}".format(p.id, self.image)
#     p.save()
#     super(Image, self).save(*args, **kwargs)


# @receiver(post_save, sender=Image)
# def save_image(sender, instance, **kwargs):
#     instance.product.featured_image = instance.image
#     instance.save()
#
#     #instance.product.featured_image = kwargs['image']
#     #instance.save()
#
