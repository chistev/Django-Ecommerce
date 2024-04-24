import json
import os
from datetime import timedelta

from django.contrib.sessions.models import Session
from django.core.exceptions import ObjectDoesNotExist

from django.utils import timezone
from dotenv import load_dotenv

import random

import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import resolve, reverse

from ecommerce.models import UserActivity, Order, OrderItem
from ecommerce.views import merge_carts
from .forms import RegistrationForm, LoginForm, AddressForm, EmailForm, PersonalDetailsForm, EditBasicDetailsForm, \
    ForgotPasswordForm, PasswordResetForm
from .models import CustomUser, PersonalDetails, State, City, Address
from django.shortcuts import render, redirect, get_object_or_404

# Load environment variables from .env file
load_dotenv()


def login_excluded(redirect_to):
    # This decorator kicks authenticated users out of a view
    def _method_wrapper(view_method):
        def _arguments_wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                # If the user is authenticated, redirect them to the specified URL
                return redirect(redirect_to)
            # If the user is not authenticated, proceed with the view
            return view_method(request, *args, **kwargs)

        return _arguments_wrapper

    return _method_wrapper


def redirect_to_login_or_register(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login_or_register')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_excluded('ecommerce:index')
def login_or_register(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.filter(email=email).first()
            if user is not None:
                return redirect('accounts:login', email=email)
            else:
                return redirect('accounts:register', email=email)
    else:
        form = EmailForm()
    return render(request, 'accounts/login_or_register.html', {'form': form})


@login_excluded('ecommerce:index')
# if no email is provided when calling the function, it is set to None.
def register(request, email=None):
    if not email:
        return redirect('accounts:login_or_register')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                if CustomUser.objects.filter(email=email).exists():
                    messages.error(request, 'A user with that email already exists. Please log in.')
                    return redirect('accounts:login_or_register')

                else:
                    request.session['registration_data'] = {
                        'email': email,
                        'password': form.cleaned_data['password1'],
                    }
                    return redirect('accounts:personal_details')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        form = RegistrationForm(initial={'email': email})

    return render(request, 'accounts/register.html', {'form': form})


@login_excluded('ecommerce:index')
def personal_details(request):
    registration_data = request.session.get('registration_data')

    if not registration_data:
        return redirect('accounts:login_or_register')

    if request.method == 'POST':
        form = PersonalDetailsForm(request.POST)
        if form.is_valid():
            email = registration_data['email']
            password = registration_data['password']

            user = CustomUser.objects.create_user(email=email, password=password)

            # By using commit=False, Django returns an unsaved model instance, allowing you to modify its attributes
            # or perform additional operations on it.
            new_personal_details = form.save(commit=False)
            # Since the form doesn't automatically handle related models relationships, you need to manually assign
            # the related object (in this case, the 'CustomUser' instance) to the appropriate field ('user') in the
            # PersonalDetails instance before saving it.
            new_personal_details.user = user
            new_personal_details.save()

            del request.session['registration_data']

            return HttpResponseRedirect(
                reverse('accounts:successful_registration', args=(new_personal_details.first_name,)))

    else:
        form = PersonalDetailsForm()
    return render(request, 'accounts/personal_details.html', {'form': form})


@login_excluded('ecommerce:index')
def successful_registration(request, first_name):
    return render(request, 'accounts/successful_registration.html', {'first_name': first_name})


@login_excluded('ecommerce:index')
def login(request, email=None):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Authenticate user
            user = authenticate(request, email=email, password=password)
            if user is not None:
                # Log in the user
                auth_login(request, user)
                # Merge carts if user was previously non-authenticated
                if 'cart' in request.session:
                    session_key = request.session.session_key
                    session_cart = Session.objects.get(session_key=session_key)
                    merge_carts(request, user, session_cart)
                return redirect('ecommerce:index')
            else:
                messages.error(request, 'Invalid email or password')

    else:
        # If it's a GET request, render the login form
        form = LoginForm(initial={'email': email})
    return render(request, 'accounts/login.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/'  # Redirect to home page after logout


@redirect_to_login_or_register
def account_page(request, template_name, additional_context=None):
    current_path = resolve(request.path_info).url_name
    context = {'current_path': current_path}
    if additional_context:
        context.update(additional_context)
    return render(request, template_name, context)


@redirect_to_login_or_register
def my_account(request):
    user = request.user  # Get the logged-in user
    try:
        personal_details = user.personal_details  # Access the PersonalDetails related object
    except ObjectDoesNotExist:
        personal_details = None  # If PersonalDetails doesn't exist, set it to None

    # Retrieve user's addresses
    user_addresses = Address.objects.filter(user=user)

    return account_page(request, 'accounts/my_account.html',
                        {'user': user, 'personal_details': personal_details,
                         'user_addresses': user_addresses})


def calculate_delivery_dates(order_date):
    delivery_start_date = order_date + timedelta(days=5)
    delivery_end_date = order_date + timedelta(days=10)
    return delivery_start_date, delivery_end_date


@redirect_to_login_or_register
def orders(request):
    # Query orders that have not been cancelled
    active_orders = Order.objects.filter(user=request.user, is_cancelled=False).order_by('-order_date')
    orders_with_dates = []
    for order in active_orders:
        # Get the first product associated with the order
        order_item = order.orderitem_set.first()
        if order_item:
            delivery_start_date, delivery_end_date = calculate_delivery_dates(order.order_date)
            orders_with_dates.append({
                'order': order,
                'order_item': order_item,  # Pass the first order item
                'delivery_start_date': delivery_start_date,
                'delivery_end_date': delivery_end_date
            })

    # Count the total number of cancelled orders
    total_cancelled_orders = Order.objects.filter(user=request.user, is_cancelled=True).count()

    context = {'active_orders': orders_with_dates, 'total_cancelled_orders': total_cancelled_orders}
    return account_page(request, 'accounts/orders.html', context)


@redirect_to_login_or_register
def closed_orders(request):
    # Query cancelled orders and order them by cancellation_date in descending order
    cancelled_orders = Order.objects.filter(user=request.user, is_cancelled=True).order_by('-cancellation_date')
    cancelled_orders_with_items = []
    for order in cancelled_orders:
        # Get the first order item associated with the order
        order_item = order.orderitem_set.first()
        if order_item:
            cancelled_orders_with_items.append({
                'order': order,
                'order_item': order_item,
            })

    cancelled_orders_count = len(cancelled_orders_with_items)
    context = {'cancelled_orders': cancelled_orders_with_items, 'cancelled_orders_count': cancelled_orders_count}
    return account_page(request, 'accounts/closed_orders.html', context)


@redirect_to_login_or_register
def order_details(request, order_number):
    order = Order.objects.get(order_number=order_number, user=request.user)
    # Get the order items associated with the order
    order_items = OrderItem.objects.filter(order=order)

    # Calculate the total number of items in the order
    total_items = sum(order_item.quantity for order_item in order_items)

    # Calculate total cost
    total_items_cost = sum(order_item.product.new_price * order_item.quantity for order_item in order_items)

    # Calculate total cost after subtracting total items cost from the order total amount
    delivery_fee = order.total_amount - total_items_cost

    # Retrieve the user's address
    user_address = Address.objects.filter(user=request.user).first()

    # Calculate the delivery dates using the calculate_delivery_dates function
    delivery_start_date, delivery_end_date = calculate_delivery_dates(order.order_date)

    # Determine payment method
    payment_method = order.get_payment_method_display()

    return account_page(request, 'accounts/order_details.html', {'order': order, 'total_items': total_items,
                                                                 'order_items': order_items,
                                                                 'total_items_cost': total_items_cost,
                                                                 'delivery_fee': delivery_fee,
                                                                 'user_address': user_address,
                                                                 'delivery_start_date': delivery_start_date,
                                                                 'delivery_end_date': delivery_end_date,
                                                                 'payment_method': payment_method})


@redirect_to_login_or_register
def cancel_order(request, order_number):
    order = Order.objects.get(order_number=order_number, user=request.user)
    order.is_cancelled = True
    order.cancellation_date = timezone.now()
    order.save()
    return redirect('accounts:closed_orders')


@redirect_to_login_or_register
def inbox(request):
    return account_page(request, 'accounts/inbox.html')


@redirect_to_login_or_register
def saved_items(request):
    # Retrieve the count of saved products
    saved_products_count = UserActivity.objects.filter(user=request.user, saved=True).count()

    saved_products = UserActivity.objects.filter(user=request.user, saved=True).select_related('product')
    for saved_product in saved_products:
        if saved_product.product.old_price is not None and saved_product.product.old_price != 0:
            discount = ((
                                    saved_product.product.old_price - saved_product.product.new_price) / saved_product.product.old_price) * 100
            saved_product.product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            saved_product.product.discount_percentage = 0

    return account_page(request, 'accounts/saved_items.html',
                        {'saved_products': saved_products,
                         'saved_products_count': saved_products_count})


@redirect_to_login_or_register
def remove_saved_product(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        user = request.user

        if user.is_authenticated:
            # Delete the UserActivity instance for the user and product
            UserActivity.objects.filter(user=user, product_id=product_id).delete()
            # Retrieve the count of saved products after removal
            saved_products_count = UserActivity.objects.filter(user=user, saved=True).count()

            return JsonResponse({'status': 'success', 'saved_products_count': saved_products_count})
        else:
            return JsonResponse({'status': 'error', 'message': 'User is not authenticated.'}, status=403)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


@redirect_to_login_or_register
def account_management(request):
    user = request.user  # Get the logged-in user
    try:
        personal_details = user.personal_details
    except ObjectDoesNotExist:
        personal_details = None

    return render(request, 'accounts/account_management.html', {'user': user, 'personal_details': personal_details})


@redirect_to_login_or_register
def basic_details(request):
    user = request.user  # Get the logged-in user
    try:
        personal_details = user.personal_details
    except ObjectDoesNotExist:
        personal_details = None
    return render(request, 'accounts/basic_details.html', {'user': user, 'personal_details': personal_details})


@redirect_to_login_or_register
def edit_basic_details(request):
    user = request.user
    try:
        personal_details = user.personal_details
    except ObjectDoesNotExist:
        personal_details = None

    if request.method == 'POST':
        # request.POST is a dictionary-like object containing all the submitted data from the form.
        # instance = personal_details  is used to specify the instance of the model that the form is working with
        form = EditBasicDetailsForm(request.POST, instance=personal_details)
        if form.is_valid():
            form.save()
            return redirect('accounts:basic_details')
    else:
        form = EditBasicDetailsForm(instance=personal_details)

    return render(request, 'accounts/edit_basic_details.html',
                  {'user': user, 'personal_details': personal_details, 'form': form})


@redirect_to_login_or_register
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')

        user = request.user

        # Check if the current password provided matches the user's actual current password
        if not user.check_password(current_password):
            # Display an error message if the current password doesn't match
            messages.error(request, 'Your current password is incorrect.')
        elif new_password == current_password:
            messages.error(request, 'Your new password cannot be the same as your current password.')
        elif new_password != confirm_password:
            messages.error(request, 'New password and confirmation do not match.')
        else:
            # Set the new password
            user.set_password(new_password)
            user.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            # Redirect to a success page or the account page
            messages.success(request, 'Your password has been changed successfully.')
            return redirect('accounts:basic_details')

    return render(request, 'accounts/change_password.html')


@redirect_to_login_or_register
def delete_account(request):
    if request.method == 'POST':
        # Check if the user confirms the deletion
        if request.POST.get('confirm_delete'):
            user = request.user  # Get the logged-in user
            entered_password = request.POST.get('Password')  # Get the password entered by the user

            # Check if the entered password matches the user's actual password
            if user.check_password(entered_password):
                # Password matches, proceed with deletion
                user.delete()
                messages.success(request, 'Your account has been successfully deleted.')
                return redirect('ecommerce:index')  # Redirect to the index page or any other page
            else:
                # Password doesn't match, show an error message
                messages.error(request, 'Incorrect password. Please try again.')

    return render(request, 'accounts/delete_account.html')


@redirect_to_login_or_register
def address_book(request):
    current_path = resolve(request.path_info).url_name
    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)

    context = {
        'user_addresses': user_addresses,
        'current_path': current_path
    }
    return render(request, 'accounts/address_book.html', context)


@redirect_to_login_or_register
def save_address(request, form):
    if form.is_valid():
        # Save or update personal details for the user
        user = request.user
        personal_details, created = PersonalDetails.objects.get_or_create(user=user)
        personal_details.first_name = form.cleaned_data['first_name']
        personal_details.last_name = form.cleaned_data['last_name']
        personal_details.save()

        # Save address details
        address_instance = form.save(commit=False)
        address_instance.user = user
        address_instance.save()


@redirect_to_login_or_register
def address_book_create(request):
    current_path = resolve(request.path_info).url_name
    user = request.user
    personal_details = user.personal_details

    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)

        if form.is_valid():
            save_address(request, form)
            return redirect('accounts:address_book')
    else:
        initial_data = {'first_name': personal_details.first_name if personal_details else '',
                        'last_name': personal_details.last_name if personal_details else ''}
        form = AddressForm(initial=initial_data, user=user)
    states = State.objects.all()
    context = {
        'user': user,
        'personal_details': personal_details,
        'states': states,
        'form': form,
        'current_path': current_path
    }
    return render(request, 'accounts/address_book_create.html', context)


@redirect_to_login_or_register
def address_book_edit(request, address_id):
    current_path = resolve(request.path_info).url_name
    # Fetch the address object from the database
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        # Create an instance of the AddressForm and populate it with the POST data and instance
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('accounts:address_book')  # Redirect to the address book page after successful update
    else:
        # Populate the form with the existing address details
        form = AddressForm(instance=address)

    context = {
        'form': form,
        'current_path': current_path
    }
    return render(request, 'accounts/address_book_edit.html', context)


@redirect_to_login_or_register
def get_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse({'cities': list(cities)})


def terms_and_conditions(request):
    return render(request, 'accounts/terms_and_conditions.html')


@redirect_to_login_or_register
def send_security_code(email):
    # Generate 4-digit security code
    security_code = ''.join(random.choices('0123456789', k=4))

    # Calculate expiration time (30 minutes from now)
    expiration_time = timezone.now() + timezone.timedelta(minutes=30)

    # Save the security code and expiration time to the database
    user = CustomUser.objects.filter(email=email).first()
    if user:
        user.personal_details.security_code = security_code
        user.personal_details.security_code_expiration = expiration_time
        user.personal_details.save()

        # Send the security code to the user's email
        send_security_code_email(email, security_code)

    return security_code  # Return the security code for verification in the security code reset view


@login_excluded('ecommerce:index')
def forgot_password(request, email=None):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            security_code = send_security_code(email)
            if security_code:
                # Store the email and security code in the session for validation in security_code_reset view
                request.session['reset_email'] = email
                request.session['security_code'] = security_code
            # To maintain security, provide a generic message instead of revealing whether the email exists
            messages.success(request, 'An email with instructions has been sent if the provided address is registered.')
            return redirect('accounts:security_code_reset')
        else:
            messages.error(request, 'Please provide a valid email address.')
    else:
        form = ForgotPasswordForm(initial={'email': email})
    return render(request, 'accounts/forgot_password.html', {'email': email, 'form': form})


@redirect_to_login_or_register
def send_security_code_email(email, security_code):
    # Check for the presence of the API key
    api_key = os.environ.get('BREVO_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the 'BREVO_API_KEY' environment variable.")
    api_url = 'https://api.brevo.com/v3/smtp/email'
    sender_email = 'stephenowabie@gmail.com'
    sender_name = 'Chistev'

    # Fetch user details based on the provided email
    try:
        user = CustomUser.objects.get(email=email)
        personal_details = user.personal_details
        first_name = personal_details.first_name
    except ObjectDoesNotExist:
        print("User not found for the provided email.")
        return

    # Replace placeholder with actual security code and user's first name
    with open('accounts/templates/accounts/security_code_email.html', 'r') as file:
        custom_html_content = file.read()

    # Replace placeholder with actual security code
    custom_html_content = custom_html_content.replace('{security_code}', security_code)
    custom_html_content = custom_html_content.replace('{first_name}', first_name)

    payload = {
        "sender": {
            "name": sender_name,
            "email": sender_email,
        },
        "to": [
            {
                "email": email
            }
        ],
        "subject": "Password Reset Security Code",
        "htmlContent": custom_html_content
    }

    headers = {
        'Content-Type': 'text/html',  # Set Content-Type to text/html for HTML email
        'Accept': 'application/json',
        'api-key': api_key
    }
    # json.dumps() converts the Python dictionary payload into a JSON string that can be sent over the network.
    response = requests.post(api_url, data=json.dumps(payload), headers=headers)

    if response.status_code == 201:
        print("Security code email sent successfully.")
    else:
        print("Failed to send security code email.")


@redirect_to_login_or_register
def security_code_reset(request):
    reset_email = request.session.get('reset_email', None)
    if request.method == 'POST':
        # Get the entered security code from the form
        entered_code = ''.join(request.POST.get(f'code{i}', '') for i in range(1, 5))

        # Get the email associated with the security code from the session
        reset_email = request.session.get('reset_email', None)
        security_code = request.session.get('security_code', None)
        if reset_email and security_code:
            if security_code == entered_code:
                # Redirect to the password reset page if the codes match
                return redirect('accounts:password_reset')
            else:
                messages.error(request, "This verification code is not valid. Please request a new one.")
        else:
            messages.error(request, "Session data not found. Please request a new verification code.")
    # If the codes don't match or if the method is GET, render the security code reset page
    return render(request, 'accounts/security_code_reset.html', {'email': reset_email})


@redirect_to_login_or_register
def resend_security_code(request):
    # Retrieve the email from the session
    reset_email = request.session.get('reset_email')

    # Resend the security code
    if reset_email:
        # Generate a new security code and update the session
        new_security_code = send_security_code(reset_email)
        request.session['security_code'] = new_security_code  # Update the session with the new security code
        messages.success(request, 'A new security code has been sent to your email.')
    else:
        messages.error(request, 'Session data not found. Please request a new verification code.')

    # Redirect back to the security code reset page
    return redirect('accounts:security_code_reset')


@redirect_to_login_or_register
def password_reset(request):
    # Retrieve the email from the session
    reset_email = request.session.get('reset_email')
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Get the cleaned data from the form
            password = form.cleaned_data['password']

            # Update the user's password using reset_email
            user = CustomUser.objects.get(email=reset_email)
            user.set_password(password)
            user.save()

            # clear/reset the reset_email session variable
            del request.session['reset_email']

            # Log the user in Since "user" is obtained directly from the database, any changes made to the session
            # after this point won't affect the authentication process.
            user = authenticate(request, email=user.email, password=password)
            if user is not None:
                login(request, user)
                return redirect('ecommerce:index')
        else:
            messages.error(request, "passwords do not match")
    else:
        form = PasswordResetForm(initial={'email': reset_email})
    context = {'reset_email': reset_email, 'form': form}
    return render(request, 'accounts/password_reset.html', context)
