from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login

from ecommerce.models import CartItem, Product


def cart_view(request):
    if request.user.is_authenticated:
        # Sum the quantities of all cart items for the authenticated user
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_quantity=Sum('quantity'))['total_quantity']
        # Get the list of products in the cart for the authenticated user
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
        if cart_count is None:
            cart_count = 0  # Set the count to 0 if no items are found

        # Calculate subtotal
        subtotal = sum(item.product.new_price * item.quantity for item in cart_items)

        # Format the price for each product in the cart
        for item in cart_items:
            item.product.formatted_price = intcomma(int(item.product.new_price))
            item.product.formatted_old_price = intcomma(int(item.product.old_price))

            # Calculate discount percentage
            if item.product.old_price != 0:
                discount = (item.product.old_price - item.product.new_price) / item.product.old_price * 100
                item.product.discount_percentage = round(discount, 2) * -1  # Make it negative
            else:
                item.product.discount_percentage = 0

            # Add product quantity to each item
            item.product.quantity = item.quantity

            # Add information about whether product count is 1 or not
            item.product.is_single_quantity = item.quantity == 1
        # Check if cart is empty
        is_cart_empty = cart_count == 0
        return render(request, 'cart/cart.html', {'cart_count': cart_count, 'cart_items': cart_items,
                                                  'is_cart_empty': is_cart_empty, 'subtotal': subtotal})
    else:
        # Handle the case when the user is not authenticated
        # You may want to redirect the user to the login page or display an error message
        return render(request, 'cart/cart.html', {'cart_count': 0, 'cart_items': None})


def remove_all_from_cart(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        # Check if the user has a cart and the product is in the cart
        cart_items = CartItem.objects.filter(cart__user=user, product=product)
        if cart_items.exists():
            # Delete all cart items related to the product
            cart_items.delete()

            # Get the updated cart count
            cart_count = CartItem.objects.filter(cart__user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity']
            if cart_count is None:
                cart_count = 0  # Set the count to 0 if no items are found

            return JsonResponse({'status': 'success', 'cart_quantity': cart_count})
        else:
            # If the product is not in the cart, return an error
            return JsonResponse({'status': 'error', 'message': 'Product not found in the cart'}, status=404)
    else:
        # If the request is not AJAX or not a POST request, return an error
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)