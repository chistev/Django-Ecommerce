
from django.contrib.humanize.templatetags.humanize import intcomma

from django.db.models import Min, Max
from django.shortcuts import render, get_object_or_404, redirect

from accounts.forms import AddressForm
from accounts.models import Address, State
from ecommerce.models import Product, Cart, CartItem

from django.http import JsonResponse


def index(request):
    breadcrumb = [('Home', '/')]
    return render(request, 'ecommerce/index.html', {'breadcrumb': breadcrumb})


def supermarket(request):
    breadcrumb = [('Home', '/'), ('Supermarket', '/supermarket/')]
    return render(request, 'ecommerce/supermarket.html', {'breadcrumb': breadcrumb})


def grains_and_rice(request):
    # Retrieve the minimum and maximum prices of available products
    min_price = Product.objects.aggregate(Min('new_price'))['new_price__min']
    max_price = Product.objects.aggregate(Max('new_price'))['new_price__max']

    products = Product.objects.all()
    # Calculate the discount percentage for each product
    for product in products:
        if product.old_price != 0:
            discount = (product.old_price - product.new_price) / product.old_price * 100
            product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            product.discount_percentage = 0

        # Format the price with commas for each product
        product.formatted_old_price = intcomma(int(product.old_price))  # Cast to int to remove decimals
        product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    breadcrumb = [('Home', '/'), ('Supermarket', '/supermarket/'), ('Rice & Grains', '/grains_and_rice/')]
    return render(request, 'ecommerce/grains_and_rice.html', {'breadcrumb': breadcrumb, 'products': products,
                                                              'min_price': min_price, 'max_price': max_price})


def filter_products(request):
    # Get the minimum and maximum price values from the request
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    # Filter products based on the price range
    filtered_products = Product.objects.filter(new_price__gte=min_price, new_price__lte=max_price)

    # Prepare product data to send to the frontend
    products_data = []
    for product in filtered_products:
        # Calculate discount percentage
        if product.old_price > 0 and product.old_price > product.new_price:
            discount_percentage = round(((product.old_price - product.new_price) / product.old_price) * 100) * -1
        else:
            discount_percentage = 0

        # Format the price with commas
        product.formatted_old_price = intcomma(int(product.old_price))  # Cast to int to remove decimals
        product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

        # Prepare product data to send to the frontend
        product_data = {
            'name': product.name,
            'price': product.new_price,
            'old_price': product.old_price,
            'discount_percentage': discount_percentage,
            'formatted_price': product.formatted_price,
            'formatted_old_price': product.formatted_old_price,
            'image_url': product.image.url
        }
        products_data.append(product_data)

    # Return JSON response with product data
    return JsonResponse(products_data, safe=False)


def food_cupboard(request):
    return render(request, 'ecommerce/food_cupboard.html')


def household_care(request):
    return render(request, 'ecommerce/household_care.html')


def laundry(request):
    return render(request, 'ecommerce/laundry.html')


def fragrances(request):
    return render(request, 'ecommerce/fragrances.html')


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    user_cart_items = []

    if request.user.is_authenticated:
        # Check if the product is in the user's cart
        user_cart_items = CartItem.objects.filter(cart__user=request.user, product=product)

    # Format the price with commas
    product.formatted_old_price = intcomma(int(product.old_price))  # Cast to int to remove decimals
    product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)
    form = AddressForm(user=request.user)  # Pass the user object to the form
    states = State.objects.all()  # Retrieve all states from the database

    breadcrumb = [
        ('Home', '/'),
        ('Supermarket', '/supermarket/'),
        ('Rice & Grains', '/grains_and_rice/'),
        (product.name, ''),  # Display the product name directly
    ]

    return render(request, 'ecommerce/product_detail.html', {'breadcrumb': breadcrumb, 'product': product,
                                                             'user_address': user_addresses, 'form': form,
                                                             'states': states, 'user_cart_items': user_cart_items})


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, pk=product_id)
        # Check if the user is authenticated
        if request.user.is_authenticated:
            # Get or create the user's cart
            cart, created = Cart.objects.get_or_create(user=request.user)
            # Check if the product is already in the cart
            cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
            # If the item is already in the cart, increase its quantity
            if not item_created:
                cart_item.quantity += 1
                cart_item.save()
            return redirect('ecommerce:product_detail', product_id=product_id)
        else:
            # If the user is not authenticated, you may want to redirect them to the login page
            return redirect('accounts:login')  # Adjust the URL name according to your project
    else:
        return redirect('ecommerce:product_detail', product_id=product_id)
