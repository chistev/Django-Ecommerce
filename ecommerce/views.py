from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import IntegrityError

from django.db.models import Min, Max, F, Sum
from django.shortcuts import render, get_object_or_404, redirect

from accounts.forms import AddressForm
from accounts.models import Address, State
from ecommerce.models import Product, Cart, CartItem, UserActivity

from django.http import JsonResponse


def index(request):
    breadcrumb = [('Home', '/')]
    return render(request, 'ecommerce/index.html', {'breadcrumb': breadcrumb})


def supermarket(request):
    breadcrumb = [('Home', '/'), ('Supermarket', '/supermarket/')]
    return render(request, 'ecommerce/supermarket.html', {'breadcrumb': breadcrumb})


def grains_and_rice(request):
    # Retrieve the minimum and maximum prices of available products
    min_price = Product.objects.filter(category='grains_rice').aggregate(Min('new_price'))['new_price__min']
    max_price = Product.objects.filter(category='grains_rice').aggregate(Max('new_price'))['new_price__max']

    products = Product.objects.filter(category='grains_rice')

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

    # Filter products based on the price range and category
    filtered_products = Product.objects.filter(category='grains_rice', new_price__gte=min_price,
                                               new_price__lte=max_price)

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
            'id': product.id,  # Include product ID
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
    # Retrieve the product
    product = get_object_or_404(Product, pk=product_id)

    # Retrieve user-related information if the user is authenticated
    user_activity_exists = False  # Initialize saved status as False
    if request.user.is_authenticated:
        # Check if the product is in the user's cart
        user_cart_items = CartItem.objects.filter(cart__user=request.user, product=product)

        # Check if the product is saved by the user
        user_activity_exists = UserActivity.objects.filter(user=request.user, product=product).exists()
    else:
        user_cart_items = []

    # Format the price with commas
    product.formatted_old_price = intcomma(int(product.old_price))  # Cast to int to remove decimals
    product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)
    form = AddressForm(user=request.user)  # Pass the user object to the form
    states = State.objects.all()  # Retrieve all states from the database

    # Prepare breadcrumb navigation
    breadcrumb = [
        ('Home', '/'),
        ('Supermarket', '/supermarket/'),
        ('Rice & Grains', '/grains_and_rice/'),
        (product.name, ''),  # Display the product name directly
    ]

    # Render the product detail page
    return render(request, 'ecommerce/product_detail.html', {
        'breadcrumb': breadcrumb,
        'product': product,
        'user_address': user_addresses,
        'form': form,
        'states': states,
        'user_cart_items': user_cart_items,
        'user_activity_exists': user_activity_exists,
    })


def add_to_cart(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        # Check if the user has a cart
        cart, created = Cart.objects.get_or_create(user=user)

        # Check if the product is already in the cart
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            # If the product is already in the cart, increment the quantity
            cart_item.quantity = F('quantity') + 1
            cart_item.save()
        else:
            # If the product is not in the cart, create a new CartItem
            CartItem.objects.create(cart=cart, product=product, quantity=1)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'error'}, status=400)


def remove_from_cart(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        # Check if the user has a cart and the product is in the cart
        cart_item = CartItem.objects.filter(cart__user=user, product=product).first()
        if cart_item:
            if cart_item.quantity > 1:
                # If the quantity is more than 1, decrement the quantity
                cart_item.quantity = F('quantity') - 1
                cart_item.save()
            else:
                # If the quantity is 1, remove the item from the cart
                cart_item.delete()
            return JsonResponse({'status': 'success'})
        else:
            # If the product is not in the cart, return an error
            return JsonResponse({'status': 'error', 'message': 'Product not found in the cart'}, status=404)
    else:
        # If the request is not AJAX or not a POST request, return an error
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def cart_count(request):
    if request.user.is_authenticated:
        # Sum the quantities of all cart items for the authenticated user
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_quantity=Sum('quantity'))\
        ['total_quantity']
        if cart_count is None:
            cart_count = 0  # Set the count to 0 if no items are found
        print(cart_count)
        # Return the cart count as JSON response
        return JsonResponse({'count': cart_count})
    else:
        # Return an error response if the user is not authenticated
        return JsonResponse({'error': 'User is not authenticated'}, status=401)


def return_policy(request):
    return render(request, 'ecommerce/return_policy.html')


def save_product(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)

        if request.user.is_authenticated:
            # Query for UserActivity instances for the user and product
            user_activities = UserActivity.objects.filter(user=request.user, product=product)

            if user_activities.exists():
                # If there are multiple instances, delete all but one
                if user_activities.count() > 1:
                    user_activities.exclude(pk=user_activities.first().pk).delete()

                # Toggle the 'saved' status for the remaining instance
                user_activity = user_activities.first()
                user_activity.saved = not user_activity.saved
                user_activity.save()
                status = 'save' if user_activity.saved else 'unsave'
            else:
                # Create a new UserActivity instance if none exists
                UserActivity.objects.create(user=request.user, product=product, saved=True)
                status = 'save'

            return JsonResponse({'status': status})
        else:
            return JsonResponse({'status': 'error', 'message': 'User is not authenticated.'}, status=403)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)