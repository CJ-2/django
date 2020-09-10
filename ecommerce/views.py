import os
import re
from time import gmtime, strftime

import braintree
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, \
    login  # Use alias like "django_logout" so that django doesnt get confused on which function to use.
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.files.storage import FileSystemStorage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.defaulttags import register
from django.views.decorators.csrf import csrf_exempt

from orders.forms import OrderCreateForm
from orders.models import Order, OrderItem
from .apps import EcommerceConfig
from .forms import *
from .helpers import Helpers
from .models import Member, Product, Image, User

paypal_access_token = "access_token$sandbox$8f9htcykq255v55n$d8e95f2daddb1d62da6199d05352bb4a"


def index(request):
    preview_products = Product.objects.all().order_by('-id')[:12]

    return render(request, Helpers.get_url('index.html'),
                  {'products': preview_products, 'currency': EcommerceConfig.currency})


def single_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    author = get_object_or_404(User, pk=product.author)
    product_images = product.image_set.all()
    images = []
    cart_items = request.session

    # Create an empty cart object if it does not exist yet
    if not cart_items.has_key("cart"):
        cart_items["cart"] = {}

    in_cart = True if cart_items['cart'].get(str(product_id)) else False

    if product_images:
        for data in product_images:
            images.append({"small": Helpers.get_path(str(data.image)), 'big': Helpers.get_path(str(data.image))})

    return render(request, Helpers.get_url('product/single.html'),
                  {'product': product, 'images': str(images).replace("'", '"'), 'in_cart': in_cart, 'author': author,
                   'currency': EcommerceConfig.currency})


def products(request):
    if request.method == 'POST':
        pagination_content = ""
        page_number = request.POST['data[page]'] if request.POST['data[page]'] else 1
        page = int(page_number)
        name = request.POST['data[name]']
        sort = '-' if request.POST['data[sort]'] == 'DESC' else ''
        search = request.POST['data[search]']
        max = int(request.POST['data[max]'])

        cur_page = page
        page -= 1
        per_page = max  # Set the number of results to display
        start = page * per_page

        # If search keyword is not empty, we include a query for searching
        # the "content" or "name" fields in the database for any matched strings.
        if search:
            all_posts = Product.objects.filter(Q(content__contains=search) | Q(name__contains=search)).exclude(
                status=0).order_by(sort + name)[start:per_page]
            count = Product.objects.filter(Q(content__contains=search) | Q(name__contains=search)).exclude(
                status=0).count()

        else:
            all_posts = Product.objects.exclude(status=0).order_by(sort + name)[start:cur_page * max]
            count = Product.objects.exclude(status=0).count()

    else:
        return render(request, 'ecommerce/product/index.html')


def product_search(request):
    queryset_list = Product.objects.order_by('-date')
    if 'keywords' in request.GET:
        keywords = request.GET['keywords']
        if keywords:
            queryset_list = queryset_list.filter(excerpt__icontains=keywords)
    if 'price' in request.GET:
        price = request.GET['price']
        queryset_list = queryset_list.filter(price__icontains=price)

    context = {
        'products': queryset_list,
        'values': request.GET
    }
    return render(request, Helpers.get_url('product/search.html'), context)


def about(request):
    return render(request, Helpers.get_url('about.html'))

def ALL(request):
    return render(request, Helpers.get_url('ALL.html'))


def contact(request):
    return render(request, Helpers.get_url('contact.html'))


def paymentDetails(request):
    return render(request, Helpers.get_url('payment-details.html'))


def user_login(request):
    # Redirect if already logged-in
    if request.user.is_authenticated:
        return HttpResponseRedirect(Helpers.get_path('user/account'))

    if request.method == 'POST':
        # Process the request if posted data are available
        username = request.POST['username']
        password = request.POST['password']
        # Check username and password combination if correct
        user = authenticate(username=username, password=password)
        if user is not None:
            # Success, now let's login the user.
            login(request, user)
            # Then redirect to the accounts page.
            return HttpResponseRedirect(Helpers.get_path('user/account'))
        else:
            # Incorrect credentials, let's throw an error to the screen.
            return render(request, Helpers.get_url('user/login.html'),
                          {'error_message': 'Incorrect username and / or password.'})
    else:
        # No post data availabe, let's just show the page to the user.
        return render(request, Helpers.get_url('user/login.html'))


def user_account(request):
    err_succ = {'status': 0, 'message': 'An unknown error occured'}

    # Create instance of the form and populate it with requests
    form = AccountForm(request.POST)

    # Redirect if not logged-in
    if request.user.is_authenticated == False:
        return HttpResponseRedirect(Helpers.get_path('user/login'))

    if request.method == 'POST':
        if form.is_valid():
            # Query data of currently logged-in user.
            user = User.objects.get(username=request.user.username)

            # Check if username exists
            if User.objects.filter(username=form.cleaned_data['username']).exists() and user.username != \
                    form.cleaned_data['username']:
                err_succ['message'] = 'Username aleady taken, please enter a different one.'

            # Check if email exists
            elif User.objects.filter(email=form.cleaned_data['email']).exists() and user.email != form.cleaned_data[
                'email']:
                err_succ['message'] = 'Email already taken, please enter a different one'

            elif form.cleaned_data['old_password'] and form.cleaned_data['password_repeat'] and form.cleaned_data[
                'password']:
                # Check if passwords match
                if form.cleaned_data['password_repeat'] != form.cleaned_data['password']:
                    err_succ['message'] = 'New password do not match.'

                # Check if old password is correct
                elif not user.check_password(form.cleaned_data['old_password']):
                    err_succ['message'] = 'Incorrect old password.'

            else:
                user.username = form.cleaned_data['username']
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']

                user.member.phone_number = form.cleaned_data['phone_number']
                user.member.about = form.cleaned_data['about_me']

                # Save new password if passes above validations
                if form.cleaned_data['password']:
                    user.set_password(form.cleaned_data['password'])

                # Save posted fields to their respective tables
                user.member.save()
                user.save()

                # Show success message
                err_succ['status'] = 1
                err_succ['message'] = 'Account successfully updated.'

        return JsonResponse(err_succ)
    else:
        # Let's define intial data that we are going to use to popul
        # ate our account form.
        user_data = {
            'username': request.user.username,
            'email': request.user.email,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'phone_number': request.user.member.phone_number,
            'about_me': request.user.member.about
        }
        # Render the account form
        return render(request, Helpers.get_url('user/account.html'), {'form': AccountForm(initial=user_data)})


def user_products(request):
    # Redirect if not logged-in
    if request.user.is_authenticated == False:
        return HttpResponseRedirect(Helpers.get_path('user/login'))

    if request.method == 'POST':
        pagination_content = ""
        page_number = request.POST['data[page]'] if request.POST['data[page]'] else 1
        page = int(page_number)
        name = request.POST['data[th_name]']
        sort = '-' if request.POST['data[th_sort]'] == 'DESC' else ''
        search = request.POST['data[search]']
        max = int(request.POST['data[max]'])

        cur_page = page
        page -= 1
        per_page = max  # Set the number of results to display
        start = page * per_page

        # If search keyword is not empty, we include a query for searching
        # the "content" or "name" fields in the database for any matched strings.
        if search:
            all_posts = Product.objects.filter(Q(content__contains=search) | Q(name__contains=search),
                                               author=request.user.id).order_by(sort + name)[start:per_page]
            count = Product.objects.filter(Q(content__contains=search) | Q(name__contains=search),
                                           author=request.user.id).count()

        else:
            all_posts = Product.objects.filter(author=request.user.id).order_by(sort + name)[start:cur_page * max]
            count = Product.objects.filter(author=request.user.id).count()

        if all_posts:
            for post in all_posts:
                status = 'Active' if post.status == 1 else 'Inactive'
                pagination_content += '''
					<tr>
						<td><a href="%s"><img src='%s' width='100' /></a></td>
						<td>%s</td>
						<td>%s %s</td>
						<td>%s</td>
						<td>%s</td>
						<td>%s</td>
						<td>
							<a href='%s'>  
								Edit
							</a> &nbsp; &nbsp;
							<a href='#' class='delete-product' item_id='%s'>
								Delete
							</a>
						</td>
					</tr>
				''' % (Helpers.get_path('user/product/update/' + str(post.id)), Helpers.get_path(post.featured_image),
                       post.name, EcommerceConfig.currency, intcomma(post.price), status, post.date, post.quantity,
                       Helpers.get_path('user/product/update/' + str(post.id)), post.id)
        else:
            pagination_content += "<tr><td colspan='7' class='bg-danger p-d'>No results</td></tr>"

        return JsonResponse({
            'content': pagination_content,
            'navigation': Helpers.nagivation_list(count, per_page, cur_page)
        })
    else:
        return render(request, Helpers.get_url('product/user.html'))


def user_product_create(request):
    err_succ = {'status': 0, 'message': 'An unknown error occured'}

    # Redirect if not logged-in
    if request.user.is_authenticated == False:
        return HttpResponseRedirect(Helpers.get_path('user/login'))

    # Create instance of the form and populate it with requests
    form = CreateProductForm(request.POST)

    if request.method == 'POST':
        if form.is_valid():
            price = re.compile(r'[^\d.]+')
            product = Product.objects.create(
                name=form.cleaned_data['name'],
                content=form.cleaned_data['content'],
                excerpt=form.cleaned_data['excerpt'],
                price=price.sub('', form.cleaned_data['price']),  # Strip all non numberic characters except decimal
                status=form.cleaned_data['status'],
                quantity=form.cleaned_data['quantity'],
                author=request.user.id
            )
            product.save()

            err_succ['status'] = 1
            err_succ['message'] = product.id

        return JsonResponse(err_succ)
    else:
        return render(request, Helpers.get_url('product/create.html'), {'form': CreateProductForm()})


def user_product_update(request, product_id):
    # Query object of given product id
    product = get_object_or_404(Product, pk=product_id)

    # Define default values
    err_succ = {'status': 0, 'message': 'An unknown error occured', 'images': []}

    # Redirect if not logged-in
    if request.user.is_authenticated == False:
        return HttpResponseRedirect(Helpers.get_path('user/login'))

    # Create instance of the form and populate it with requests
    form = UpdateProductForm(request.POST)

    # Check if we received a post request
    if request.method == 'POST':
        if form.is_valid():
            # Check if current user owns the product
            if product.author != request.user.id:
                err_succ['message'] = 'You are not the author of this product.'

            else:
                price = re.compile(r'[^\d.]+')

                # Update the fields
                product.name = form.cleaned_data['name']
                product.content = form.cleaned_data['content']
                product.excerpt = form.cleaned_data['excerpt']
                product.price = price.sub('', form.cleaned_data[
                    'price'])  # Strip all non numberic characters except decimal
                product.status = form.cleaned_data['status']
                product.quantity = form.cleaned_data['quantity']
                # product.save()

                # Check if there are posted images.
                if request.FILES.getlist('images'):
                    # Define the location where we will be uploading our file(s)
                    # We'll use the format ecommerce/media/products/PRODUCT_ID to group images by product.
                    product_location = 'media/products/' + str(product.id)

                    # Loop through each posted image file
                    for post_file in request.FILES.getlist('images'):
                        # Create an instance of FileSystemStorage class using a custom upload location as indicated in the parameter.
                        fs = FileSystemStorage(location=product_location)
                        # Save the file(s) to the specified location
                        filename = fs.save(post_file.name, post_file)
                        # Build the URL location of our image.
                        uploaded_file_url = product_location + '/' + filename
                        # Append file to images array so we can return it to the client side for rendering.
                        err_succ['images'].append(uploaded_file_url)

                        # Save the image to our database.
                        image = Image.objects.create(
                            product=product,
                            image=uploaded_file_url
                        )
                        image.save()
                    product.featured_image = err_succ['images'][0]
                    product.save()

                # Return a success message.
                err_succ['status'] = 1
                err_succ['message'] = 'تم تحديث المنتج'

        return JsonResponse(err_succ)
    else:
        # Define initial data to feed our form
        product_data = {
            'name': product.name,
            'content': product.content,
            'excerpt': product.excerpt,
            'price': product.price,
            'status': product.status,
            'quantity': product.quantity,
        }
        return render(request, Helpers.get_url('product/update.html'), {'form': UpdateProductForm(initial=product_data),
                                                                        'product': product})  # Include product object when rendering the view.


def set_featured_image(request):
    # Query object of given product id
    product = get_object_or_404(Product, id=10)
    # Define default values
    err_succ = {'status': 0, 'message': 'An unknown error occured'}

    # Check if logged in and owns the product
    if request.user.is_authenticated == False or product.author != request.user.id:
        return JsonResponse(err_succ)

    # Check if we received a post
    if request.method == 'POST':
        # Set image path as the featured image for this product
        product.featured_image = request.POST['image']
        product.save()

        # Return a success message.
        err_succ['status'] = 1
        err_succ['message'] = 'Image successfully set as featured'

    return JsonResponse(err_succ)


def unset_image(request):
    # Query object of given product id
    product = get_object_or_404(Product, pk=request.POST['product_id'])
    image = get_object_or_404(Image, pk=request.POST['image_id'])
    # Define default values
    err_succ = {'status': 0, 'message': 'An unknown error occured'}

    # Check if logged in and owns the product
    if request.user.is_authenticated == False or product.author != request.user.id:
        return JsonResponse(err_succ)

    # Check if we received a post
    if request.method == 'POST':
        # Delete the image from storage
        os.remove(settings.BASE_DIR + '/' + str(image.image))
        # Delete the image from database
        image.delete()

        # Return a success message.
        err_succ['status'] = 1
        err_succ['message'] = 'Image successfully deleted'

    return JsonResponse(err_succ)


def unset_product(request):
    # Query object of given product id
    product = get_object_or_404(Product, pk=request.POST['product_id'])
    # Define default values
    err_succ = {'status': 0, 'message': 'An unknown error occured'}

    # Check if logged in and owns the product
    if request.user.is_authenticated == False or product.author != request.user.id:
        return JsonResponse(err_succ)

    # Check if we received a post
    if request.method == 'POST':
        # Delete all the image under this product
        for image in product.image_set.all():
            # Delete the image from storage
            os.remove(settings.BASE_DIR + '/' + str(image.image))
            # Delete the image from database
            image.delete()

        # Delete the product from database
        product.delete()

        # Return a success message.
        err_succ['status'] = 1
        err_succ['message'] = 'تم حذف المنتج'

    return JsonResponse(err_succ)


def user_register(request):
    # Redirect if already logged-in
    if request.user.is_authenticated:
        return HttpResponseRedirect(Helpers.get_path('user/account'))

    # Create instance of the form and populate it with requests
    form = RegisterForm(request.POST)

    # Define default values
    err_succ = {'status': 0, 'message': 'An unknown error occured'}

    if request.method == 'POST':
        # check whether it's valid:
        if form.is_valid():
            if User.objects.filter(username=form.cleaned_data['username']).exists():
                err_succ['message'] = 'Username already exists.'

            elif User.objects.filter(email=form.cleaned_data['email']).exists():
                err_succ['message'] = 'Email already exists.'

            elif form.cleaned_data['password'] != form.cleaned_data['password_repeat']:
                err_succ['message'] = 'Passwords do not match.'

            else:
                # Create the user:
                user = User.objects.create_user(
                    form.cleaned_data['username'],
                    form.cleaned_data['email'],
                    form.cleaned_data['password']
                )
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']

                member = Member.objects.create(
                    user=user,
                    phone_number=form.cleaned_data['phone_number'],
                    about=''
                )

                member.save()
                user.save()

                # Login the user
                login(request, user)

                # return account page URL where we will be redirecting the user.
                err_succ['status'] = 1
                err_succ['message'] = 'Sucessfully registered, redirecting to your account..'

        return JsonResponse(err_succ)

    # No post data availabe, let's just show the page.
    else:
        return render(request, Helpers.get_url('user/register.html'), {'form': RegisterForm()})


def logout(request):
    # Clear the session cookies to logout the user.
    # django_logout(request)

    # Manually clear user auth related data
    session = request.session

    try:
        del session["_auth_user_id"]
        del session["_auth_user_backend"]
        del session["_auth_user_hash"]
    except KeyError:
        pass

    session.modified = True

    # Redirect after logout
    return HttpResponseRedirect(Helpers.get_path('user/login'))


@csrf_exempt
def cart(request):
    cart_items = request.session

    # Create an empty cart object if it does not exist yet
    if not cart_items.has_key("cart"):
        cart_items["cart"] = {}

    if request.method == 'POST':
        action = request.POST.get('action', '')
        quantity = int(request.POST.get('quantity', 0))
        item_id = str(request.POST.get('item_id', 0))

        product_data = {
            'quantity': quantity,
            'date_added': strftime("%Y-%m-%d %H:%M:%S", gmtime())
        }

        # Edit item
        if action == 'edit':
            cart_items["cart"][item_id]["quantity"] = quantity
            cart_items.modified = True

        # Add item
        if action == 'add':
            cart_items["cart"][item_id] = product_data
            cart_items.modified = True

        # Delete an item
        if action == 'delete':
            try:
                del cart_items["cart"][item_id]
            except KeyError:
                pass
            cart_items.modified = True

        # return HttpResponse(cart_items.items())
        return HttpResponseRedirect(request.POST.get('redirect', '/ecommerce/products'))

    # No post data availabe, let's just show the page.
    else:
        item_ids = cart_items["cart"].keys()
        products = Product.objects.filter(pk__in=item_ids)

        cart_total = 0
        for item in products:
            cart_item = cart_items["cart"].get(str(item.id))
            cart_total = (item.price * cart_item.get("quantity")) + cart_total

        # return HttpResponse(cart_items.items())
        return render(request, Helpers.get_url('cart.html'),
                      {'cart_session_items': cart_items["cart"], 'cart_db_items': products,
                       'cart_total': float("%0.2f" % (cart_total)), 'currency': EcommerceConfig.currency})


@csrf_exempt
def checkout(request):
    cart_items = request.session

    # paypal key
    gateway = braintree.BraintreeGateway(access_token=paypal_access_token)
    client_token = gateway.client_token.generate()

    # Create an empty cart object if it does not exist yet
    if not cart_items.has_key("cart"):
        cart_items["cart"] = {}

    item_ids = cart_items["cart"].keys()
    products = Product.objects.filter(pk__in=item_ids)

    cart_total = 0
    for item in products:
        cart_item = cart_items["cart"].get(str(item.id))
        cart_total = (item.price * cart_item.get("quantity")) + cart_total

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            request.session['order_id'] = order.id

    else:
        form = OrderCreateForm()
    # return HttpResponse(result)
    return render(request, 'ecommerce/checkout.html',
                  {'cart_session_items': cart_items["cart"], 'cart_db_items': products,
                   'cart_total': float("%0.2f" % (cart_total)), 'currency': EcommerceConfig.currency,
                   'paypal_key': client_token, 'form': form})


@csrf_exempt
def checkout_cash_on_delivery(request):
    cart_items = request.session

    # Create an empty cart object if it does not exist yet
    if not cart_items.has_key("cart"):
        cart_items["cart"] = {}

    item_ids = cart_items["cart"].keys()
    products = Product.objects.filter(pk__in=item_ids)

    cart_total = 0
    for item in products:
        cart_item = cart_items["cart"].get(str(item.id))
        cart_total = (item.price * cart_item.get("quantity")) + cart_total
        quantity = cart_item.get("quantity")
        price = item.price * quantity
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.payment_method = 'COD'
            order.save()
            for item in products:
                cart_item = cart_items["cart"].get(str(item.id))
                cart_total = (item.price * cart_item.get("quantity")) + cart_total
                quantity = cart_item.get("quantity")
                price = item.price * quantity
                OrderItem.objects.create(order=order,
                                         product=item,
                                         quantity=quantity,
                                         price=price)
                # clear the cart

            request.session['order_id'] = order.id
            return redirect('ecommerce:cash_on_delivery_created')
        else:
            messages.error(request, 'Please provide valid information.')

    else:
        form = OrderCreateForm()
    # return HttpResponse(result)
    return render(request, 'order/cash_on_delivery_checkout.html',
                  {'cart_session_items': cart_items["cart"], 'cart_db_items': products,
                   'cart_total': cart_total, 'currency': EcommerceConfig.currency,
                   'form': form})


# cash on delivery method
def cash_on_delivery_order_created(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/cash_on_delivery_created.html', {'order': order})


@csrf_exempt
def checkout_paypal(request):
    cart_items = request.session

    # Create an empty cart object if it does not exist yet
    if not cart_items.has_key("cart"):
        cart_items["cart"] = {}

    item_ids = cart_items["cart"].keys()
    products = Product.objects.filter(pk__in=item_ids)

    cart_total = 0
    for item in products:
        cart_item = cart_items["cart"].get(str(item.id))
        cart_total = (item.price * cart_item.get("quantity")) + cart_total
        quantity = cart_item.get("quantity")
        price = item.price * quantity

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.payment_method = 'PAYPAL'
            order.save()
            for item in products:
                cart_item = cart_items["cart"].get(str(item.id))
                cart_total = (item.price * cart_item.get("quantity")) + cart_total
                quantity = cart_item.get("quantity")
                price = item.price * quantity
                OrderItem.objects.create(order=order,
                                         product=item,
                                         quantity=quantity,
                                         price=price)
            request.session['order_id'] = order.id
            return redirect('ecommerce:proceed-to-pay')

        else:
            messages.error(request, 'Please provide the valid information.')

    else:
        form = OrderCreateForm()
    # return HttpResponse(result)

    return render(request, 'order/paypal_checkout.html',
                  {'cart_session_items': cart_items["cart"], 'cart_db_items': products,
                   'cart_total': round(cart_total, 2), 'currency': EcommerceConfig.currency,
                   'form': form})


@csrf_exempt
def payment_paypal(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)

    amount = request.POST.get('amount')
    payment_method_nonce = request.POST.get("payment_method_nonce")
    payment_method = 'paypal'
    description = request.POST.get('description')
    gateway = braintree.BraintreeGateway(access_token=paypal_access_token)
    result = gateway.transaction.sale({
        "amount": amount,
        "merchant_account_id": "USD",
        "payment_method_nonce": payment_method_nonce,
        "options": {
            "paypal": {
                "custom_field": "PayPal custom field",
                "description": description
            },
        }
    })
    if result.is_success:
        # mark the order as paid
        order.paid = True
        # store the unique transaction id
        order.braintree_id = result.transaction.id
        order.save()
        return JsonResponse({'statusCode': '1', 'amount': amount})

    return JsonResponse({'statusCode': '2'})


############payment module###########

# Template function for accessing cart dictionary item by key
@register.filter
def get_cart_item(dictionary, key):
    return dictionary.get(str(key))


# Template function for multipication of two numbers
@register.simple_tag()
def multiply(qty, unit_price, *args, **kwargs):
    return qty * unit_price


# proceed to pay
def proceed_to_pay(request):
    order_id = request.session.get('order_id')
    order = get_object_or_404(Order, id=order_id)
    cart_items = request.session

    # paypal key
    gateway = braintree.BraintreeGateway(access_token=paypal_access_token)
    client_token = gateway.client_token.generate()

    # Create an empty cart object if it does not exist yet
    if not cart_items.has_key("cart"):
        cart_items["cart"] = {}

    item_ids = cart_items["cart"].keys()
    products = Product.objects.filter(pk__in=item_ids)

    cart_total = 0
    for item in products:
        cart_item = cart_items["cart"].get(str(item.id))
        cart_total = (item.price * cart_item.get("quantity")) + cart_total
    # return HttpResponse(result)
    return render(request, 'order/proceed_to_pay.html',
                  {'cart_session_items': cart_items["cart"], 'cart_db_items': products,
                   'cart_total': cart_total, 'currency': EcommerceConfig.currency,
                   'paypal_key': client_token})
