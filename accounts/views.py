from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import resolve, reverse

from ecommerce.models import UserActivity
from .forms import RegistrationForm, LoginForm, AddressForm, EmailForm, PersonalDetailsForm, EditBasicDetailsForm, \
    ForgotPasswordForm
from .models import CustomUser, PersonalDetails, State, City, Address
from django.shortcuts import render, redirect, get_object_or_404


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


@login_excluded('ecommerce:index')
def login_or_register(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Check if the email exists in the database
            user = CustomUser.objects.filter(email=email).first()
            if user is not None:
                # If the email exists, redirect to the login page
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
        # Handle the case where email is not present
        return redirect('accounts:login_or_register')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            password1 = form.cleaned_data['password1']
            password2 = form.cleaned_data['password2']

            if password1 == password2:
                # Check if a user with the provided email already exists
                if CustomUser.objects.filter(email=email).exists():
                    # User with the provided email already exists, display error message
                    messages.error(request, 'A user with that email already exists. Please log in.')
                    return redirect('accounts:login_or_register')

                else:
                    # Passwords match, store relevant details in the session until the registration process is complete
                    request.session['registration_data'] = {
                        'email': email,  # refers to the value passed to the register function as a parameter
                        'password': form.cleaned_data['password1'],
                    }
                    return redirect('accounts:personal_details')
            else:
                messages.error(request, 'Passwords do not match')
        else:
            # Form is invalid, and errors are already in the form object
            # Displaying form errors using messages framework
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")
    else:
        # GET request, render an empty form
        form = RegistrationForm(initial={'email': email})

    return render(request, 'accounts/register.html', {'form': form})


@login_excluded('ecommerce:index')
def personal_details(request):
    # Retrieve stored details from the session
    registration_data = request.session.get('registration_data')

    if not registration_data:
        # If no registration data is found, redirect to login_or_register
        return redirect('accounts:login_or_register')

    if request.method == 'POST':
        form = PersonalDetailsForm(request.POST)
        if form.is_valid():
            # Retrieve email and password from session data
            email = registration_data['email']
            password = registration_data['password']

            # Create a new user
            user = CustomUser.objects.create_user(email=email, password=password)

            # By using commit=False, Django returns an unsaved model instance, allowing you to modify its attributes
            # or perform additional operations on it.
            new_personal_details = form.save(commit=False)
            # Since the form doesn't automatically handle related models relationships, you need to manually assign
            # the related object (in this case, the 'CustomUser' instance) to the appropriate field ('user') in the
            # PersonalDetails instance before saving it.
            new_personal_details.user = user
            new_personal_details.save()

            # Clear registration_data from the session
            del request.session['registration_data']

            # Redirect to successful_registration view with first name as URL parameter
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
                return redirect('ecommerce:index')
        else:
            messages.error(request, 'Invalid email or password')

    else:
        # If it's a GET request, render the login form
        form = LoginForm(initial={'email': email})
    return render(request, 'accounts/login.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/'  # Redirect to home page after logout


@login_required
def account_page(request, template_name, additional_context=None):
    current_path = resolve(request.path_info).url_name
    context = {'current_path': current_path}
    if additional_context:
        context.update(additional_context)
    return render(request, template_name, context)


@login_required
def my_account(request):
    user = request.user  # Get the logged-in user
    personal_details = user.personal_details  # Access the PersonalDetails related object

    # Retrieve user's addresses
    user_addresses = Address.objects.filter(user=user)

    return account_page(request, 'accounts/my_account.html',
                        {'user': user, 'personal_details': personal_details,
                            'user_addresses': user_addresses})


@login_required
def orders(request):
    return account_page(request, 'accounts/orders.html')


@login_required
def closed_orders(request):
    return account_page(request, 'accounts/closed_orders.html')


@login_required
def inbox(request):
    return account_page(request, 'accounts/inbox.html')


@login_required
def saved_items(request):
    # Retrieve the count of saved products
    saved_products_count = UserActivity.objects.filter(user=request.user, saved=True).count()

    saved_products = UserActivity.objects.filter(user=request.user, saved=True).select_related('product')
    for saved_product in saved_products:
        if saved_product.product.old_price is not None and saved_product.product.old_price != 0:
            discount = ((saved_product.product.old_price - saved_product.product.new_price) / saved_product.product.old_price) * 100
            saved_product.product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            saved_product.product.discount_percentage = 0

    return account_page(request, 'accounts/saved_items.html',
                        {'saved_products': saved_products,
                            'saved_products_count': saved_products_count})


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


@login_required
def account_management(request):
    user = request.user  # Get the logged-in user
    personal_details = user.personal_details
    return render(request, 'accounts/account_management.html', {'user': user, 'personal_details': personal_details})


@login_required
def basic_details(request):
    user = request.user  # Get the logged-in user
    personal_details = user.personal_details
    return render(request, 'accounts/basic_details.html', {'user': user, 'personal_details': personal_details})


@login_required
def edit_basic_details(request):
    user = request.user
    personal_details = user.personal_details

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


@login_required
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


@login_required
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


@login_required
def address_book(request):
    current_path = resolve(request.path_info).url_name
    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)

    context = {
        'user_addresses': user_addresses,
        'current_path': current_path
    }
    return render(request, 'accounts/address_book.html', context)


@login_required
def address_book_create(request):
    current_path = resolve(request.path_info).url_name
    user = request.user
    personal_details = user.personal_details

    if request.method == 'POST':
        form = AddressForm(request.POST, user=request.user)

        if form.is_valid():
            # Save or update personal details for the user
            personal_details, created = PersonalDetails.objects.get_or_create(user=user)
            personal_details.first_name = form.cleaned_data['first_name']
            personal_details.last_name = form.cleaned_data['last_name']
            personal_details.save()

            # Save address details
            address_instance = form.save(commit=False)
            address_instance.user = user
            address_instance.save()

            # Redirect the user to a success page
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


@login_required
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


def get_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse({'cities': list(cities)})


def terms_and_conditions(request):
    return render(request, 'accounts/terms_and_conditions.html')

# User = get_user_model()'''
# '''def send_security_code(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         user = User.objects.filter(email=email).first()
#         if user:
#             # Generate a random 4-digit security code
#             security_code = str(random.randint(1000, 9999))
#             # Save the security code in the user's PersonalDetails model
#             user.personal_details.security_code = security_code
#             user.personal_details.save()
#             # Send email with security code
#             subject = 'Password Reset Security Code'
#             message = f'Your security code is: {security_code}'
#             from_email = 'stephenowabie@gmail.com'  # Update with your email
#             recipient_list = [email]
#             send_mail(subject, message, from_email, recipient_list)
#             # Redirect to the security_code_reset view
#             return redirect('accounts:security_code_reset')
#
#     # Handle the case where the form submission fails
#     return render(request, 'accounts/forgot_password.html')
#
# def security_code_reset(request):
#     return render(request, 'accounts/security_code_reset.html')
# '''


@login_excluded('ecommerce:index')
def forgot_password(request, email=None):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            return redirect('accounts:security_code_reset')
        else:
            messages.error(request, 'Please provide a valid email address.')
    else:
        form = ForgotPasswordForm(initial={'email': email})
    return render(request, 'accounts/forgot_password.html', {'email': email, 'form': form})


def security_code_reset(request):
    return render(request, 'accounts/security_code_reset.html')