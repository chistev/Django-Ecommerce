import uuid
from datetime import timedelta, datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from accounts.forms import AddressForm
from accounts.views import save_address
from ecommerce.models import CartItem


@login_required
def checkout_view(request):
    # Ensure user is authenticated before accessing the view
    user = request.user

    # Retrieve the user's address if available
    address = None
    if hasattr(user, 'addresses'):
        address = user.addresses.first()  # Assuming the user has only one address, adjust as needed

    # Retrieve the user's cart items and calculate the total number of items in the cart
    cart_items = None
    total_items_in_cart = 0
    total_cost = 0
    try:
        cart_items = CartItem.objects.filter(cart__user=user)
        total_items_in_cart = sum(cart_item.quantity for cart_item in cart_items)
        total_cost = sum(cart_item.product.new_price * cart_item.quantity for cart_item in cart_items)
    except CartItem.DoesNotExist:
        pass

    delivery_fee = calculate_delivery_fee(cart_items)  # Calculate delivery fee based on cart items

    # Calculate the total amount (delivery fee + total cost)
    total_amount = delivery_fee + total_cost

    # Calculate the delivery start and end dates
    order_date = timezone.now()
    delivery_start_date = order_date + timedelta(days=5)  # Add 5 days to the order date for the start date
    delivery_end_date = order_date + timedelta(days=10)  # Add 10 days to the order date for the end date

    # Create an instance of the AddressForm if there's no address available
    if address is None:
        form = AddressForm(user=user)
    else:
        form = AddressForm(instance=address)

    # Retrieve the user's personal details if available
    personal_details = None
    if hasattr(user, 'personal_details'):
        personal_details = user.personal_details

    if request.method == 'POST':
        form = AddressForm(request.POST, user=user)
        if form.is_valid():
            save_address(request, form)
            # After saving the address, redirect to the same page to continue checkout
            return HttpResponseRedirect(request.path_info)  # Redirect to the same page to refresh data
        else:
            # If it's a GET request, initialize the form with existing address data or empty form
            initial_data = {'first_name': user.personal_details.first_name if user.personal_details else '',
                            'last_name': user.personal_details.last_name if user.personal_details else ''}
            form = AddressForm(initial=initial_data, user=user)

    return render(request, 'checkout/checkout.html',
                  {'form': form, 'personal_details': personal_details, 'address': address,
                   'cart_items': cart_items, 'delivery_fee': delivery_fee, 'delivery_start_date':
                       delivery_start_date, 'delivery_end_date': delivery_end_date,
                   'total_items_in_cart': total_items_in_cart, 'total_cost': total_cost, 'total_amount': total_amount
                   })


def calculate_delivery_fee(cart_items):
    # logic to calculate the delivery fee based on the total price of the items
    total_price = sum(cart_item.product.new_price * cart_item.quantity for cart_item in cart_items)
    # Add N10 for every N1000 spent on items
    delivery_fee = (total_price // 1000) * 10
    return delivery_fee


def order_success_view(request):
    return render(request, 'checkout/order_success.html')

