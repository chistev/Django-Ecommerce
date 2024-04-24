from urllib.parse import unquote

from django.contrib.auth.models import AnonymousUser
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.sessions.models import Session
from django.db.models import Min, Max, Sum, Q, OuterRef, Subquery, F
from django.shortcuts import render, get_object_or_404


from accounts.forms import AddressForm
from accounts.models import Address, State

from ecommerce.models import Product, Cart, CartItem, UserActivity, SuperCategory, Category

from django.http import JsonResponse


def index(request):
    breadcrumb = [('Home', '/')]
    return render(request, 'ecommerce/index.html', {'breadcrumb': breadcrumb})


def get_category_data(super_category_name, title):
    breadcrumb_title_link = title.lower().replace("&", "and").replace(" ", "_")
    breadcrumb = [('Home', '/'), (title, f'/{breadcrumb_title_link}/')]
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
    products = Product.objects.filter(category=category)

    for product in products:
        if product.old_price is not None:
            if product.old_price != 0:
                discount = (product.old_price - product.new_price) / product.old_price * 100
                product.discount_percentage = round(discount, 2) * -1
            else:
                product.discount_percentage = 0
        else:
            product.discount_percentage = 0

        product.formatted_old_price = intcomma(int(product.old_price) if product.old_price is not None else 0)
        product.formatted_price = intcomma(int(product.new_price))

        # Fetch cart quantity for the product if the user is authenticated
        if request.user.is_authenticated:
            cart_quantity = CartItem.objects.filter(
                cart__user=request.user,
                product_id=product.pk
            ).values('quantity').first()
            product.cart_quantity = cart_quantity['quantity'] if cart_quantity else 0
        else:
            product.cart_quantity = 0

    return {'products': products}



def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Record the user's activity for viewing this product
    if not request.user.is_authenticated:
        # For non-authenticated users, update recently viewed products in session
        viewed_product_ids = request.session.get('recently_viewed', [])
        if product.id not in viewed_product_ids:
            viewed_product_ids.append(product.id)
            request.session['recently_viewed'] = viewed_product_ids
    else:
        # Record the user's activity for viewing this product
        if request.user.is_authenticated:
            # Check if the user has already viewed this product
            viewed_product = UserActivity.objects.filter(user=request.user, product=product).exists()
            if not viewed_product:
                # If not, create a new UserActivity instance
                UserActivity.objects.create(user=request.user, product=product, saved=False)

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
        # Retrieve cart items from session for non-authenticated users
        cart_data = request.session.get('cart', {})
        print(cart_data)
        product_id_str = str(product.id)
        if product_id_str in cart_data:
            user_cart_items = [{'product': product, 'quantity': cart_data[product_id_str]}]
        else:
            user_cart_items = []
        print("user cart items: " + str(user_cart_items))
    # Format the price with commas
    product.formatted_old_price = intcomma(int(product.old_price)) if product.old_price is not None else None
    product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user) if request.user.is_authenticated else []
    form = AddressForm(user=request.user) if request.user.is_authenticated else None
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

        if request.user.is_authenticated:
            user = request.user
        else:
            # If the user is not authenticated, set user to None
            user = None

        # Ensure user has a cart
        if user:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            print("Anonymous user")
            cart, created = Cart.objects.get_or_create(user=None)

        # Perform action on cart
        response_data = action(request, product, cart)

        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def add_to_cart(request):
    def add_to_cart_action(request, product, cart):
        if request.user.is_authenticated:
            # For authenticated users, use the database-backed cart
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if created:
                # If the item is newly created, set the quantity to 1
                cart_item.quantity = 1
            else:
                # If the item already exists, increment the quantity by 1
                cart_item.quantity += 1
            cart_item.save()
            product_quantity = cart_item.quantity
        else:
            cart_data = request.session.get('cart', {})
            if str(product.id) in cart_data:
                # If the item already exists in the session cart, increment the quantity
                cart_data[str(product.id)] += 1
            else:
                # If it's a new item, add it to the session cart with quantity 1
                cart_data[str(product.id)] = 1

            request.session['cart'] = cart_data
            product_quantity = cart_data[str(product.id)]


        # Get the updated cart count
        if request.user.is_authenticated:
            cart_count = CartItem.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        else:
            cart_count = sum(cart_data.values())

        # Calculate subtotal
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart=cart)
            subtotal = sum(item.product.new_price * item.quantity for item in cart_items)
        else:
            subtotal = sum(product.new_price * quantity for product_id, quantity in cart_data.items())
        formatted_subtotal = 'N ' + intcomma(int(subtotal))

        return {'status': 'success', 'cart_quantity': cart_count, 'product_quantity': product_quantity,
                'subtotal': formatted_subtotal}

    return process_cart_action(request, add_to_cart_action)



def remove_from_cart(request):
    def remove_from_cart_action(request, product, cart):
        if request.user.is_authenticated:
            # If the user is authenticated, remove the item from their cart
            cart_item = CartItem.objects.filter(cart__user=request.user, product=product).first()
            if cart_item:
                if cart_item.quantity > 1:
                    # If the quantity is more than 1, decrement the quantity
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
        else:
            # If the user is not authenticated, use session-based cart
            session_key = request.session.session_key
            cart_data = request.session.get('cart', {})
            if str(product.id) in cart_data:
                if cart_data[str(product.id)] > 1:
                    # If the quantity is more than 1, decrement the quantity in session
                    cart_data[str(product.id)] -= 1
                    request.session['cart'] = cart_data
                else:
                    # If the quantity is 1, remove the item from the session cart
                    del cart_data[str(product.id)]
                    request.session['cart'] = cart_data

        # Get the updated cart count
        if request.user.is_authenticated:
            cart_count = CartItem.objects.filter(cart=cart_item.cart).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        else:
            cart_count = sum(cart_data.values())

        if cart_count is None:
            cart_count = 0

        # Get the quantity of the specific product in the cart
        if request.user.is_authenticated:
            product_quantity = cart_item.quantity if cart_item else 0
        else:
            product_quantity = cart_data.get(str(product.id), 0)

        # Calculate subtotal
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(cart=cart_item.cart)
            subtotal = sum(item.product.new_price * item.quantity for item in cart_items)
        else:
            subtotal = sum(product.new_price * quantity for product_id, quantity in cart_data.items())
        formatted_subtotal = 'N ' + intcomma(int(subtotal))

        return {'status': 'success', 'cart_quantity': cart_count, 'product_quantity': product_quantity,
                'subtotal': formatted_subtotal}

    return process_cart_action(request, remove_from_cart_action)




def cart_count(request):
    if request.user.is_authenticated:
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_quantity=Sum('quantity'))['total_quantity']
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.save()
            session_key = request.session.session_key

        session_cart = Session.objects.get(session_key=session_key)
        cart_data = session_cart.get_decoded()
        cart_items = cart_data.get('cart', {})

        cart_count = sum(cart_items.values())

    if cart_count is None:
        cart_count = 0

    # Debugging prints
    print("Cart Count:", cart_count)    # Debugging statement

    return JsonResponse({'count': cart_count})

def merge_carts(request, user, session_cart):
    session_cart_data = session_cart.get_decoded()
    session_cart_items = session_cart_data.get('cart', {})

    # Get or create the authenticated user's cart
    user_cart, _ = Cart.objects.get_or_create(user=user)

    # Merge items from session cart to user cart
    for product_id, quantity in session_cart_items.items():
        product = get_object_or_404(Product, pk=product_id)
        print("Merging product:", product, "Quantity from session:", quantity)

        # Get or create the CartItem instance
        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)

        # If the item is newly created, set its quantity to the session quantity
        if created:
            cart_item.quantity = quantity
            print("New quantity after merge:", cart_item.quantity)
        else:
            print("Existing quantity in user's cart:", cart_item.quantity)
            # Update the quantity by adding the session quantity
            cart_item.quantity = F('quantity') + quantity
            print("New quantity after merge:", cart_item.quantity)

        cart_item.save()

    # Clear the session cart after merging
    del request.session['cart']

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
            return JsonResponse({'status': status})
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

            # Check if the user is authenticated
            if isinstance(request.user, AnonymousUser):
                # If user is not authenticated, set cart_quantity to 0
                product.cart_quantity = 0
            else:
                # Retrieve the quantity of the product in the user's cart
                product.cart_quantity = CartItem.objects.filter(cart__user=request.user, product=product).aggregate(Sum('quantity'))['quantity__sum'] or 0

    return render(request, 'ecommerce/search_results.html', {'products': products, 'query': query})

def autocomplete(request):
    query = request.GET.get('query', '')
    matching_products = Product.objects.filter(name__icontains=query)[:5]  # Limit to 5 suggestions
    suggestions = [{'name': product.name} for product in matching_products]
    return JsonResponse(suggestions, safe=False)


