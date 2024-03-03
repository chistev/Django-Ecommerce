from django.contrib.humanize.templatetags import humanize
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Min, Max, Count, OuterRef, Subquery
from django.shortcuts import render, get_object_or_404

from accounts.forms import AddressForm
from accounts.models import Address, State
from ecommerce.models import Product, UserActivity

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
    # Format the price with commas
    product.formatted_old_price = intcomma(int(product.old_price))  # Cast to int to remove decimals
    product.formatted_price = intcomma(int(product.new_price))  # Cast to int to remove decimals

    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)
    form = AddressForm(user=request.user)  # Pass the user object to the form
    states = State.objects.all()  # Retrieve all states from the database

    recently_viewed = []
    if request.user.is_authenticated:
        # Save user activity
        UserActivity.objects.create(user=request.user, product=product)

        # Get subquery to find the most recent timestamp for each product
        subquery = UserActivity.objects.filter(
            user=request.user,
            product=OuterRef('pk')
        ).order_by('-timestamp').values('timestamp')[:1]

        # Retrieve recently viewed items for the user, excluding duplicates
        recently_viewed = Product.objects.filter(
            id__in=UserActivity.objects.filter(user=request.user).annotate(
                recent_timestamp=Subquery(subquery)
            ).values('product')
        )

        # Format the price with commas for each viewed_product
        for viewed_product in recently_viewed:
            viewed_product.formatted_old_price = humanize.intcomma(int(viewed_product.old_price))
            viewed_product.formatted_price = humanize.intcomma(int(viewed_product.new_price))

    breadcrumb = [
        ('Home', '/'),
        ('Supermarket', '/supermarket/'),
        ('Rice & Grains', '/grains_and_rice/'),
        (product.name, ''),  # Display the product name directly
    ]

    return render(request, 'ecommerce/product_detail.html', {'breadcrumb': breadcrumb, 'product': product,
                                                             'user_address': user_addresses, 'form': form,
                                                             'states': states, 'recently_viewed': recently_viewed,})

