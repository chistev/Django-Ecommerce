from django.shortcuts import render


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login


def cart_view(request):
    return render(request, 'cart/cart.html')

