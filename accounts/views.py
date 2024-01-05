from django.contrib import messages

from .forms import RegistrationForm
from .models import CustomUser

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

def my_account():
    return None


def orders():
    return None


def saved_items():
    return None



def login(request):
    return render(request, 'accounts/login.html')


def personal_details(request):
    return render(request, 'accounts/personal_details.html')