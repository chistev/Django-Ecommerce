from django.shortcuts import render


def index(request):
    return render(request, 'ecommerce/index.html')


def supermarket(request):
    return render(request, 'ecommerce/supermarket.html')