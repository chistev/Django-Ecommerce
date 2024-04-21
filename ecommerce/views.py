from urllib.parse import unquote

from django.contrib.humanize.templatetags.humanize import intcomma

from django.db.models import Min, Max, Sum, Q
from django.shortcuts import render, get_object_or_404


from accounts.forms import AddressForm
from accounts.models import Address, State

from ecommerce.models import Product, Cart, CartItem, UserActivity, SuperCategory, Category

from django.http import JsonResponse


def index(request):
    breadcrumb = [('Home', '/')]
    return render(request, 'ecommerce/index.html', {'breadcrumb': breadcrumb})


def get_category_data(super_category_name, title):
    breadcrumb = [('Home', '/'), (title, f'/{super_category_name}/')]
    super_category = SuperCategory.objects.get(name=super_category_name)
    categories = Category.objects.filter(super_category=super_category)
    return {'breadcrumb': breadcrumb, 'categories': categories}


def supermarket(request):
    return render(request, 'ecommerce/supermarket.html', get_category_data('Supermarket', 'Supermarket'))


def home_and_office(request):
    return render(request, 'ecommerce/home_and_office.html', get_category_data('Home & Office', 'Home and Office'))


def phones_and_accessories(request):
    return render(request, 'ecommerce/phones_and_accessories.html', get_category_data('Phones & Accessories',
                                                                                      'Phones and Accessories'))


def computing(request):
    return render(request, 'ecommerce/computing.html', get_category_data('Computing', 'Computing'))


def gaming(request):
    return render(request, 'ecommerce/gaming.html', get_category_data('Gaming', 'Gaming'))


def category_products(request, category_name):
    decoded_category_name = unquote(category_name)
    category = get_object_or_404(Category, name=decoded_category_name)
    # Retrieve product data using the get_products_data function
    products_data = get_products_data(request, category)

    return render(request, 'ecommerce/category.html', products_data)


def get_products_data(request, category):
    min_price = Product.objects.filter(category=category).aggregate(Min('new_price'))['new_price__min']
    max_price = Product.objects.filter(category=category).aggregate(Max('new_price'))['new_price__max']

    products = Product.objects.filter(category=category)

    for product in products:
        if product.old_price is not None:
            if product.old_price != 0:
                discount = (product.old_price - product.new_price) / product.old_price * 100
                product.discount_percentage = round(discount, 2) * -1  # Make it negative
            else:
                product.discount_percentage = 0
        else:
            product.discount_percentage = 0

        product.formatted_old_price = intcomma(int(product.old_price) if product.old_price is not None else 0)
        product.formatted_price = intcomma(int(product.new_price))

        product.cart_quantity = CartItem.objects.filter(
            cart__user=request.user, product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0

    breadcrumb = [('Home', '/'), ('Supermarket', '/supermarket/'), (category.name.title(), f'/supermarket/{category.name.replace(" ", "-")}/')]

    return {'breadcrumb': breadcrumb, 'products': products, 'min_price': min_price, 'max_price': max_price}


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if product.old_price is not None and product.old_price != 0:
        discount = (product.old_price - product.new_price) / product.old_price * 100
        product.discount_percentage = round(discount, 2) * -1  # Make it negative
    else:
        product.discount_percentage = 0

    saved_product = None
    if request.user.is_authenticated:
        user_cart_items = CartItem.objects.filter(cart__user=request.user, product=product)

        # Check if the product is saved by the user
        saved_product = UserActivity.objects.filter(user=request.user, product=product, saved=True).exists()
    else:
         user_cart_items = []

    # Format the price with commas
    product.formatted_old_price = intcomma(int(product.old_price)) if product.old_price is not None else None
    product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)
    form = AddressForm(user=request.user)  # Pass the user object to the form
    states = State.objects.all()  # Retrieve all states from the database

    # Render the product detail page
    return render(request, 'ecommerce/product_detail.html', {
        'product': product,
        'user_address': user_addresses,
        'form': form,
        'states': states,
        'user_cart_items': user_cart_items,
        'saved_product': saved_product
    })


def process_cart_action(request, action):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        # Ensure user has a cart
        cart, created = Cart.objects.get_or_create(user=user)

        # Perform action on cart
        response_data = action(request, product, cart)

        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def add_to_cart(request):
    def add_to_cart_action(request, product, cart):
        # Check if the product is already in the cart
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            # If the product is already in the cart, increment the quantity
            cart_item.quantity += 1
            cart_item.save()
            product_quantity = cart_item.quantity
        else:
            # If the product is not in the cart, create a new CartItem
            CartItem.objects.create(cart=cart, product=product, quantity=1)
            product_quantity = 1

        # Get the updated cart count
        cart_count = CartItem.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        if cart_count is None:
            cart_count = 0

        # Calculate subtotal
        cart_items = CartItem.objects.filter(cart=cart)
        subtotal = sum(item.product.new_price * item.quantity for item in cart_items)
        formatted_subtotal = 'N ' + intcomma(int(subtotal))

        return {'status': 'success', 'cart_quantity': cart_count, 'product_quantity': product_quantity, 'subtotal': formatted_subtotal}

    return process_cart_action(request, add_to_cart_action)


def remove_from_cart(request):
    def remove_from_cart_action(request, product, cart):
        # Check if the user has a cart and the product is in the cart
        cart_item = CartItem.objects.filter(cart__user=request.user, product=product).first()
        if cart_item:
            if cart_item.quantity > 1:
                # If the quantity is more than 1, decrement the quantity
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

            # Get the updated cart count
            cart_count = CartItem.objects.filter(cart=cart_item.cart).aggregate(total_quantity=
                                                                                Sum('quantity'))['total_quantity']
            if cart_count is None:
                cart_count = 0

            # Get the quantity of the specific product in the cart
            product_quantity = cart_item.quantity

            # Calculate subtotal
            cart_items = CartItem.objects.filter(cart=cart_item.cart)
            subtotal = sum(item.product.new_price * item.quantity for item in cart_items)
            formatted_subtotal = 'N ' + intcomma(int(subtotal))

            return {'status': 'success', 'cart_quantity': cart_count, 'product_quantity': product_quantity,
                    'subtotal': formatted_subtotal}

        else:
            return {'status': 'error', 'message': 'Product not found in the cart'}

    return process_cart_action(request, remove_from_cart_action)


def cart_count(request):
    if request.user.is_authenticated:
        # Sum the quantities of all cart items for the authenticated user
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_quantity=
                                                                                Sum('quantity'))['total_quantity']
        if cart_count is None:
            cart_count = 0  # Set the count to 0 if no items are found
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

                if user_activity.saved:
                    return JsonResponse({'status': status, 'message': 'already_saved'})
                else:
                    return JsonResponse({'status': status})
            else:
                # Create a new UserActivity instance if none exists
                UserActivity.objects.create(user=request.user, product=product, saved=True)
                status = 'save'
            # Pass the updated save status of the product to the template
            product_saved = product.is_saved(request.user)
            return JsonResponse({'status': status, 'product_saved': product_saved})
        else:
            return JsonResponse({'status': 'error', 'message': 'User is not authenticated.'}, status=403)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


def product_search(request):
    query = request.GET.get('query', '')
    products = []

    if query:
        # Perform search query on Product model
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

        # Calculate min and max prices for the searched products
        min_price = products.aggregate(Min('new_price'))['new_price__min']
        max_price = products.aggregate(Max('new_price'))['new_price__max']

        for product in products:
            # Calculate discount percentage
            if product.old_price is not None and product.old_price != 0:
                discount = ((product.old_price - product.new_price) / product.old_price) * 100
                product.discount_percentage = round(discount, 2) * -1  # Make it negative
            else:
                product.discount_percentage = 0

            # Format the prices with commas
            product.formatted_old_price = intcomma(int(product.old_price) if product.old_price is not None else 0)
            product.formatted_price = intcomma(int(product.new_price))

            # Retrieve the quantity of the product in the user's cart
            product.cart_quantity = CartItem.objects.filter(cart__user=request.user, product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0

    return render(request, 'ecommerce/search_results.html', {'products': products, 'query': query, 'min_price': min_price, 'max_price': max_price})


def autocomplete(request):
    query = request.GET.get('query', '')
    matching_products = Product.objects.filter(name__icontains=query)[:5]  # Limit to 5 suggestions
    suggestions = [{'name': product.name} for product in matching_products]
    return JsonResponse(suggestions, safe=False)
