import json
import uuid
from datetime import timedelta

import requests
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from accounts.forms import AddressForm
from accounts.models import Address
from accounts.views import save_address, redirect_to_login_or_register
from ecommerce.models import CartItem, Order, OrderItem, PaymentEvent
from accounts.models import CustomUser

import os
from dotenv import load_dotenv

# Load environmental variables from .env file
load_dotenv()

FLUTTERWAVE_API_KEY = os.getenv('FLUTTERWAVE_API_KEY')


def calculate_delivery_dates():
    order_date = timezone.now()
    delivery_start_date = order_date + timedelta(days=5)
    delivery_end_date = order_date + timedelta(days=10)
    return delivery_start_date, delivery_end_date


def calculate_delivery_fee(cart_items):
    total_price = sum(cart_item.product.new_price * cart_item.quantity for cart_item in cart_items)
    # Add N10 for every N1000 spent on items
    delivery_fee = (total_price // 1000) * 10
    return delivery_fee


@redirect_to_login_or_register
def checkout_view(request):
    user = request.user
    address = user.addresses.first() if hasattr(user, 'addresses') else None

    cart_items = CartItem.objects.filter(cart__user=user)
    total_items_in_cart = sum(cart_item.quantity for cart_item in cart_items)
    total_cost = sum(cart_item.product.new_price * cart_item.quantity for cart_item in cart_items)

    if total_items_in_cart == 0:
        return redirect('cart:cart')

    delivery_fee = calculate_delivery_fee(cart_items)
    total_amount = delivery_fee + total_cost

    delivery_start_date, delivery_end_date = calculate_delivery_dates()

    form = AddressForm(user=user, instance=address)
    personal_details = user.personal_details if hasattr(user, 'personal_details') else None

    if request.method == 'POST':
        selected_payment_method = request.POST.get('payment_method')
        request.session['selected_payment_method'] = selected_payment_method

        if 'confirm_delivery' in request.POST:
            # Set a session variable to indicate that the delivery details have been confirmed
            request.session['delivery_details_confirmed'] = True
            return HttpResponseRedirect(reverse('checkout:checkout'))  # Redirect to the same page after POST

        form = AddressForm(request.POST, user=user)
        if form.is_valid():
            save_address(request, form)
            # After saving the address, redirect to the same page to continue checkout
            return HttpResponseRedirect(request.path_info)  # Redirect to the same page to refresh data
        elif 'edit_address' in request.GET:
            initial_data = {
                'first_name': user.personal_details.first_name if user.personal_details else '',
                'last_name': user.personal_details.last_name if user.personal_details else '',
                'address': address.address if address else '',
                'additional_info': address.additional_info if address else '',
                'state': address.state if address else '',
                'city': address.city if address else '',
            }
            form = AddressForm(initial=initial_data, user=user)

    return render(request, 'checkout/checkout.html',
                  {'form': form, 'personal_details': personal_details, 'address': address,
                   'cart_items': cart_items, 'delivery_fee': delivery_fee, 'delivery_start_date':
                       delivery_start_date, 'delivery_end_date': delivery_end_date,
                   'total_items_in_cart': total_items_in_cart, 'total_cost': total_cost, 'total_amount': total_amount,
                   'delivery_details_confirmed': request.session.get('delivery_details_confirmed', False),
                   'selected_payment_method': request.session.get('selected_payment_method', None),
                   })


@redirect_to_login_or_register
def pay_on_delivery(request):
    # Check if an order with the same user and not cancelled already exists
    existing_order = Order.objects.filter(user=request.user, is_cancelled=False).first()

    if existing_order:
        order_number = existing_order.order_number
    else:
        order_number = uuid.uuid4().hex.upper()[:10]

    # Calculate the delivery start and end dates
    delivery_start_date, delivery_end_date = calculate_delivery_dates()

    cart_items = CartItem.objects.filter(cart__user=request.user)

    total_cost = sum(cart_item.product.new_price * cart_item.quantity for cart_item in cart_items)

    # Calculate delivery fee
    delivery_fee = calculate_delivery_fee(cart_items)

    total_amount = delivery_fee + total_cost

    payment_method = 'pay_on_delivery'

    with transaction.atomic():
        order = existing_order if existing_order else Order.objects.create(
            order_number=order_number,
            user=request.user,
            total_amount=total_amount,
            payment_method=payment_method
        )

        for cart_item in cart_items:
            OrderItem.objects.create(order=order, product=cart_item.product, quantity=cart_item.quantity,
                                     price=cart_item.product.new_price)

        CartItem.objects.filter(cart__user=request.user).delete()

    return render(request, 'checkout/order_success.html', {'order_number': order_number,
                                                           'delivery_start_date': delivery_start_date,
                                                           'delivery_end_date': delivery_end_date})


@redirect_to_login_or_register
def payment_method_view(request):
    if request.method == 'POST' and 'selected_payment_method' in request.POST:
        selected_payment_method = request.POST.get('selected_payment_method')
        if selected_payment_method == 'tap_and_relax':
            return redirect('checkout:pay_on_delivery')
        elif selected_payment_method == 'bank_transfer':
            return HttpResponseRedirect(
                reverse('checkout:flutterwave_payment') + f'?selected_payment_method={selected_payment_method}')
    messages.error(request, "Invalid payment method or request")
    return redirect('checkout:checkout')


def flutterwave_payment_view(request):
    if request.method == 'GET' and 'selected_payment_method' in request.GET:

        user_email = request.user.email
        user_address = Address.objects.get(user=request.user)
        user_first_name = user_address.first_name
        user_last_name = user_address.last_name

        order_number = uuid.uuid4().hex.upper()[:10]

        cart_items = CartItem.objects.filter(cart__user=request.user)

        total_cost = sum(cart_item.product.new_price * cart_item.quantity for cart_item in cart_items)

        delivery_fee = calculate_delivery_fee(cart_items)

        total_amount = delivery_fee + total_cost

        tx_ref = order_number
        amount = float(total_amount)
        currency = "NGN"
        redirect_url = "https:chistevstore.pythonanywhere.com/accounts/orders/"

        customer_email = user_email
        customer_name = user_first_name + ' ' + user_last_name

        payment_data = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": currency,
            "redirect_url": redirect_url,
            "customer": {
                "email": customer_email,
                "name": customer_name
            }
            # Add any other optional parameters as needed
        }
        response = requests.post(
            "https://api.flutterwave.com/v3/payments",
            headers={"Authorization": "Bearer " + FLUTTERWAVE_API_KEY},
            json=payment_data
        )

        if response.status_code == 200:
            payment_link = response.json().get("data", {}).get("link")
            if payment_link:
                return redirect(payment_link)
        else:
            messages.error(request, "We're sorry, but we couldn't process your payment at this time. Please try again "
                                    "later or contact support for assistance.")
            return redirect("checkout:checkout")
    else:
        return redirect("checkout:checkout")


@csrf_exempt
def flutterwave_webhook_view(request):
    if request.method == 'POST':
        webhook_secret_hash = os.getenv("WEBHOOK_SECRET_HASH")
        signature = request.headers.get("verif-hash")

        if not signature or signature != webhook_secret_hash:
            return JsonResponse({"error": "Unauthorized"}, status=401)

        try:
            payload = json.loads(request.body)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid payload"}, status=400)

        # Extract information about the successful payment
        event = payload.get("event")
        data = payload.get("data")

        if event == "charge.completed":
            # To verify the payment details
            transaction_id = data.get("id")
            amount = data.get("amount")
            currency = data.get("currency")

            # Extract user email from the webhook payload
            user_email = data.get("customer", {}).get("email")
            # Authenticate the user based on the email
            if user_email:
                user = CustomUser.objects.filter(email=user_email).first()
            else:
                return JsonResponse({"error": "User email not provided in the payload"}, status=400)

            if not user:
                # If user does not exist, return error
                return JsonResponse({"error": "User not found"}, status=400)

            # Check if the event has already been processed
            existing_event = PaymentEvent.objects.filter(transaction_id=transaction_id).first()
            if existing_event and existing_event.status == "success":
                return JsonResponse({"message": "Webhook event already processed"}, status=200)

            # Make a request to Flutterwave's transaction verification endpoint
            verification_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
            headers = {"Authorization": "Bearer " + FLUTTERWAVE_API_KEY}
            response = requests.get(verification_url, headers=headers)

            if response.status_code == 200:

                verification_data = response.json()
                # Check if the payment is successful and matches the expected amount and currency
                if (
                        verification_data.get("status") == "success"
                        and verification_data.get("data", {}).get("amount") == amount
                        and verification_data.get("data", {}).get("currency") == currency
                ):
                    # Success! Create a new order for the user
                    order_number = data.get("tx_ref")
                    total_amount = amount

                    payment_method = 'bank_transfer'

                    order = Order.objects.create(
                        order_number=order_number,
                        user=user,
                        total_amount=total_amount,
                        payment_method=payment_method
                    )

                    cart_items = CartItem.objects.filter(cart__user=user)

                    for cart_item in cart_items:
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.new_price
                        )

                    CartItem.objects.filter(cart__user=user).delete()

                    PaymentEvent.objects.create(transaction_id=transaction_id, status="success")

                    order_date = timezone.now()
                    delivery_start_date = order_date + timedelta(days=5)
                    delivery_end_date = order_date + timedelta(days=10)

                    return JsonResponse({
                        "message": "Payment verification successful. Order created and cart cleared.",
                        "delivery_start_date": delivery_start_date.isoformat(),
                        "delivery_end_date": delivery_end_date.isoformat()
                    }, status=200)
                else:
                    return JsonResponse({"error": "Payment verification failed"}, status=400)
            else:
                return JsonResponse({"error": "Failed to verify payment with Flutterwave"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)
