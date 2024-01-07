from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from .forms import RegistrationForm, LoginForm
from .models import CustomUser, PersonalDetails
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
def my_account():
    return None


def orders():
    return None


def saved_items():
    return None




def terms_and_conditions(request):
    return render(request, 'accounts/terms_and_conditions.html')