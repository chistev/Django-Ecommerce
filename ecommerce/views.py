from urllib.parse import unquote

from django.contrib.auth.models import AnonymousUser
from django.contrib.humanize.templatetags import humanize
from django.contrib.humanize.templatetags.humanize import intcomma
from django.contrib.sessions.models import Session
from django.db.models import Sum, Q, F
from django.shortcuts import render, get_object_or_404


from accounts.forms import AddressForm
from accounts.models import Address, State

from ecommerce.models import Product, Cart, CartItem, UserActivity, SuperCategory, Category, OrderItem

from django.http import JsonResponse


def index(request):
    product_quantities = {}
    order_items = OrderItem.objects.all()
    for item in order_items:
        if item.product.id in product_quantities:
            product_quantities[item.product.id] += item.quantity
        else:
            product_quantities[item.product.id] = item.quantity

    # Sort the products based on their total quantities in descending order
    sorted_products = sorted(product_quantities.items(), key=lambda x: x[1], reverse=True)

    top_selling_products = [Product.objects.get(id=prod_id) for prod_id, _ in
                            sorted_products[:6]]

    for product in top_selling_products:
        if product.old_price is not None and product.old_price != 0:
            discount = (product.old_price - product.new_price) / product.old_price * 100
            product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            product.discount_percentage = 0

        product.formatted_old_price = humanize.intcomma(
            int(product.old_price)) if product.old_price is not None else None
        product.formatted_price = humanize.intcomma(int(product.new_price))
    return render(request, 'ecommerce/index.html', {'top_selling_products': top_selling_products})


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

    if not request.user.is_authenticated:
        viewed_product_ids = request.session.get('recently_viewed', [])
        if product.id not in viewed_product_ids:
            viewed_product_ids.append(product.id)
            request.session['recently_viewed'] = viewed_product_ids
    else:
        if request.user.is_authenticated:
            viewed_product = UserActivity.objects.filter(user=request.user, product=product).exists()
            if not viewed_product:
                UserActivity.objects.create(user=request.user, product=product, saved=False)

    if product.old_price is not None and product.old_price != 0:
        discount = (product.old_price - product.new_price) / product.old_price * 100
        product.discount_percentage = round(discount, 2) * -1  # Make it negative
    else:
        product.discount_percentage = 0

    saved_product = None
    if request.user.is_authenticated:
        user_cart_items = CartItem.objects.filter(cart__user=request.user, product=product)

        saved_product = UserActivity.objects.filter(user=request.user, product=product, saved=True).exists()
    else:
        cart_data = request.session.get('cart', {})
        product_id_str = str(product.id)
        if product_id_str in cart_data:
            user_cart_items = [{'product': product, 'quantity': cart_data[product_id_str]}]
        else:
            user_cart_items = []

    product.formatted_old_price = intcomma(int(product.old_price)) if product.old_price is not None else None
    product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    user_addresses = Address.objects.filter(user=request.user) if request.user.is_authenticated else []
    form = AddressForm(user=request.user) if request.user.is_authenticated else None
    states = State.objects.all()

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
            user = None

        if user:
            cart, created = Cart.objects.get_or_create(user=user)
        else:
            cart, created = Cart.objects.get_or_create(user=None)

        response_data = action(request, product, cart)

        return JsonResponse(response_data)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


def add_to_cart(request):
    def add_to_cart_action(request, product, cart):
        if request.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
            if created:
                cart_item.quantity = 1
            else:
                cart_item.quantity += 1
            cart_item.save()
            product_quantity = cart_item.quantity
        else:
            cart_data = request.session.get('cart', {})
            if str(product.id) in cart_data:
                cart_data[str(product.id)] += 1
            else:
                cart_data[str(product.id)] = 1

            request.session['cart'] = cart_data
            product_quantity = cart_data[str(product.id)]

        if request.user.is_authenticated:
            cart_count = CartItem.objects.filter(cart=cart).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        else:
            cart_count = sum(cart_data.values())

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
            cart_item = CartItem.objects.filter(cart__user=request.user, product=product).first()
            if cart_item:
                if cart_item.quantity > 1:
                    cart_item.quantity -= 1
                    cart_item.save()
                else:
                    cart_item.delete()
        else:
            cart_data = request.session.get('cart', {})
            if str(product.id) in cart_data:
                if cart_data[str(product.id)] > 1:
                    cart_data[str(product.id)] -= 1
                    request.session['cart'] = cart_data
                else:
                    del cart_data[str(product.id)]
                    request.session['cart'] = cart_data

        if request.user.is_authenticated:
            cart_count = CartItem.objects.filter(cart=cart_item.cart).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        else:
            cart_count = sum(cart_data.values())

        if cart_count is None:
            cart_count = 0

        if request.user.is_authenticated:
            product_quantity = cart_item.quantity if cart_item else 0
        else:
            product_quantity = cart_data.get(str(product.id), 0)

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
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_quantity=
                                                                                Sum('quantity'))['total_quantity']
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

    return JsonResponse({'count': cart_count})


def merge_carts(request, user, session_cart):
    session_cart_data = session_cart.get_decoded()
    session_cart_items = session_cart_data.get('cart', {})

    # _ is a dummy variable used to discard the second element of the tuple, which is a boolean indicating whether the
    # instance was newly created (True) or retrieved from the database (False). Since we are only interested in the
    # user_cart variable, we use _ to discard the second element
    user_cart, _ = Cart.objects.get_or_create(user=user)

    for product_id, quantity in session_cart_items.items():
        product = get_object_or_404(Product, pk=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=user_cart, product=product)

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity = F('quantity') + quantity

        cart_item.save()

    del request.session['cart']


def return_policy(request):
    return render(request, 'ecommerce/return_policy.html')


def save_product(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)

        if request.user.is_authenticated:
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
        products = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

        for product in products:
            if product.old_price is not None and product.old_price != 0:
                discount = ((product.old_price - product.new_price) / product.old_price) * 100
                product.discount_percentage = round(discount, 2) * -1  # Make it negative
            else:
                product.discount_percentage = 0

            product.formatted_old_price = intcomma(int(product.old_price) if product.old_price is not None else 0)
            product.formatted_price = intcomma(int(product.new_price))

    return render(request, 'ecommerce/search_results.html', {'products': products, 'query': query})


def autocomplete(request):
    query = request.GET.get('query', '')
    matching_products = Product.objects.filter(name__icontains=query)[:5]
    suggestions = [{'name': product.name} for product in matching_products]
    return JsonResponse(suggestions, safe=False)
