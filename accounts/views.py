from django.shortcuts import render

# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def login_view(request):
    return render(request, 'accounts/login.html')

