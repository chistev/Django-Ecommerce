from django.contrib import messages

from .forms import RegistrationForm
from .models import CustomUser, PersonalDetails

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate


def login_or_register(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            pass
            return redirect('')
        else:
            return redirect('accounts:register', email=email)
    else:
        return render(request, 'accounts/login.html')


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
                    'password1': form.cleaned_data['password1'],
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


def personal_details(request):
    # Retrieve stored details from the session
    registration_data = request.session.get('registration_data')

    if not registration_data:
        # If no registration data is found, redirect to login_or_register
        return redirect('accounts:login_or_register')

    if request.method == 'POST':
        email = registration_data['email']
        password = registration_data['password1']

        # Check if a user with the given email already exists
        existing_user = CustomUser.objects.filter(email=email).first()

        if existing_user:
            # If user already exists, handle accordingly (redirect, display error, etc.)
            messages.error(request, 'A user with this email already exists. Please log in.')
            return redirect('accounts:login_or_register')

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


def successful_registration(request):
    return render(request, 'accounts/successful_registration.html')
def my_account():
    return None


def orders():
    return None


def saved_items():
    return None



def login(request):
    return render(request, 'accounts/login.html')


