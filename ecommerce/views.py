from django.shortcuts import render


def index(request):
    return render(request, 'ecommerce/index.html')


def supermarket(request):
    return render(request, 'ecommerce/supermarket.html')


def grains_and_rice(request):
    return render(request, 'ecommerce/grains_and_rice.html')