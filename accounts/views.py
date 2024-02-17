from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, get_user_model, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LogoutView
from django.http import JsonResponse
from django.urls import resolve

from .forms import RegistrationForm, LoginForm, AddressForm
from .models import CustomUser, PersonalDetails, State, City, Address
from django.shortcuts import render, redirect


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
        email = request.POST.get('email')

        # Check if the email exists in the database
        user = CustomUser.objects.filter(email=email).first()

        if user is not None:
            # If the email exists, redirect to the login page
            return redirect('accounts:login', email=email)
        else:
            return redirect('accounts:register', email=email)
    else:
        return render(request, 'accounts/login_or_register.html')


@login_excluded('ecommerce:index')
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
                # Passwords match, store relevant details in the session until the registration process is complete
                request.session['registration_data'] = {
                    'email': email,
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
        email = registration_data['email']
        password = registration_data['password']

        # Create a new user
        user = CustomUser.objects.create_user(email=email, password=password)

        # Create personal details for the user
        PersonalDetails.objects.create(user=user, first_name=request.POST.get('first_name'),
                                       last_name=request.POST.get('last_name'))

        # Clear registration_data from the session
        del request.session['registration_data']

        return redirect('accounts:successful_registration')
    else:
        return render(request, 'accounts/personal_details.html',)


def login(request, email=None):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password1')

        # Authenticate user
        user = authenticate(request, email=email, password=password)
        if user is not None:
            # Log in the user
            auth_login(request, user)
            return redirect('ecommerce:index')
        else:
            messages.error(request, 'Invalid email or password')
            print("Authentication failed.")

    # If the authentication fails or it's a GET request, render the login form
    form = LoginForm(initial={'email': email})
    return render(request, 'accounts/login.html', {'form': form})


@login_excluded('ecommerce:index')
def successful_registration(request):
    return render(request, 'accounts/successful_registration.html')


class CustomLogoutView(LogoutView):
    next_page = '/'  # Redirect to home page after logout, change it according to your needs

    def get_next_page(self):
        next_page = super().get_next_page()
        # Additional logic if needed before redirecting
        return next_page


@login_required
def my_account(request):
    current_path = resolve(request.path_info).url_name
    user = request.user  # Get the logged-in user
    personal_details = user.personal_details  # Access the PersonalDetails related object
    return render(request, 'accounts/my_account.html',
                  {'current_path': current_path, 'user': user, 'personal_details': personal_details})


@login_required
def orders(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'accounts/orders.html', {'current_path': current_path})


@login_required
def closed_orders(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'accounts/closed_orders.html', {'current_path': current_path})


@login_required
def inbox(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'accounts/inbox.html', {'current_path': current_path})


@login_required
def saved_items(request):
    current_path = resolve(request.path_info).url_name
    return render(request, 'accounts/saved_items.html', {'current_path': current_path})


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
    user = request.user  # Get the logged-in user
    personal_details = user.personal_details

    if request.method == 'POST':
        # Extract form data
        first_name = request.POST.get('first-name')
        middle_name = request.POST.get('middle-name')
        last_name = request.POST.get('last-name')

        # Get the PersonalDetails instance associated with the current user
        personal_details = request.user.personal_details

        # Update the PersonalDetails model
        personal_details.first_name = first_name
        personal_details.middle_name = middle_name
        personal_details.last_name = last_name
        personal_details.save()

        # Redirect to a success page
        return redirect('accounts:basic_details')
    return render(request, 'accounts/edit_basic_details.html',
                  {'user': user, 'personal_details': personal_details})


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
            # Display an error message if the new password is the same as the current password
            messages.error(request, 'Your new password cannot be the same as your current password.')
        elif new_password != confirm_password:
            # Display an error message if the new password and confirmation don't match
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
    # Retrieve the user's addresses
    user_addresses = Address.objects.filter(user=request.user)

    context = {
        'user_addresses': user_addresses
    }
    return render(request, 'accounts/address_book.html', context)


@login_required
def address_book_create(request):
    if request.method == 'POST':
        # Bind form with POST data
        form = AddressForm(request.POST)

        if form.is_valid():
            # Get the logged-in user
            user = request.user
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
            # Render the form again with validation errors
            user = request.user
            personal_details = user.personal_details
            states = State.objects.all()
            context = {
                'user': user,
                'personal_details': personal_details,
                'states': states,
                'form': form,
            }
            return render(request, 'accounts/address_book_create.html', context)

    else:
        # Handle GET request, render the address book creation form
        form = AddressForm()
        user = request.user  # Get the logged-in user
        personal_details = user.personal_details
        initial_first_name = personal_details.first_name if personal_details else ''  # Initial first name
        initial_last_name = personal_details.last_name if personal_details else ''  # Initial last name
        initial_data = {'first_name': initial_first_name, 'last_name': initial_last_name}
        form = AddressForm(initial=initial_data)
        states = State.objects.all()
        context = {
            'user': user,
            'personal_details': personal_details,
            'states': states,
            'form': form,
        }
        return render(request, 'accounts/address_book_create.html', context)


def get_cities(request):
    state_id = request.GET.get('state_id')
    cities = City.objects.filter(state_id=state_id).values('id', 'name')
    return JsonResponse({'cities': list(cities)})


def terms_and_conditions(request):
    return render(request, 'accounts/terms_and_conditions.html')


'''class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'class': 'form-control bg-secondary text-white', 'readonly': 'readonly'}))
def forgot_password(request, email=None):
    # If the email is provided, initialize the form with the email
    initial_data = {'email': email} if email else {}
    form = ForgotPasswordForm(initial=initial_data)

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            # Redirect the user to a confirmation page or login page
            return redirect('accounts:security_code_reset')
    return render(request, 'accounts/forgot_password.html', {'form': form})


User = get_user_model()'''
'''def send_security_code(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        user = User.objects.filter(email=email).first()
        if user:
            # Generate a random 4-digit security code
            security_code = str(random.randint(1000, 9999))
            # Save the security code in the user's PersonalDetails model
            user.personal_details.security_code = security_code
            user.personal_details.save()
            # Send email with security code
            subject = 'Password Reset Security Code'
            message = f'Your security code is: {security_code}'
            from_email = 'stephenowabie@gmail.com'  # Update with your email
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list)
            # Redirect to the security_code_reset view
            return redirect('accounts:security_code_reset')

    # Handle the case where the form submission fails
    return render(request, 'accounts/forgot_password.html')

def security_code_reset(request):
    return render(request, 'accounts/security_code_reset.html')
'''


def address_book_edit(request):
    return render(request, 'accounts/address_book_edit.html')