from django.contrib.humanize.templatetags.humanize import intcomma
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from django.shortcuts import render

from ecommerce.models import CartItem, Product


def cart_view(request):
    # An aggregate expression specifies the operation to perform (e.g., Sum, Avg, Count) and the field to perform
    # it on.
    # If user is authenticated, filter by user's cart; otherwise, include all carts
    # Get the list of products in the cart for the authenticated user
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user).select_related('product')
        cart_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_quantity=Sum('quantity'))[
            'total_quantity']
    else:
        # For non-authenticated users, retrieve cart items from session
        cart_data = request.session.get('cart', {})
        product_ids = cart_data.keys()
        # Retrieve products using product IDs from the session
        cart_items = [CartItem(product_id=product_id, quantity=cart_data[product_id]) for product_id in product_ids]
        cart_count = sum(cart_data.values())

    if cart_count is None:
        cart_count = 0  # Set the count to 0 if no items are found

    # Calculate subtotal
    subtotal = sum(item.product.new_price * item.quantity for item in cart_items)

    # Format the price for each product in the cart
    for item in cart_items:
        item.product.formatted_price = intcomma(int(item.product.new_price))
        item.product.formatted_old_price = intcomma(int(item.product.old_price)) if item.product.old_price is not None else None

        # Calculate discount percentage
        if item.product.old_price is not None and item.product.old_price != 0:
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


def remove_all_from_cart(request):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        product_id = request.POST.get('product_id')
        product = get_object_or_404(Product, pk=product_id)
        user = request.user

        # Check if the user is authenticated
        if user.is_authenticated:
            # For authenticated users, remove the item from the database cart
            cart_items = CartItem.objects.filter(cart__user=user, product=product)
            if cart_items.exists():
                cart_items.delete()

                cart_count = CartItem.objects.filter(cart__user=user).aggregate(total_quantity=Sum('quantity'))['total_quantity']
                if cart_count is None:
                    cart_count = 0

                return JsonResponse({'status': 'success', 'cart_quantity': cart_count})
            else:
                return JsonResponse({'status': 'error', 'message': 'Product not found in the cart'}, status=404)
        else:
            # For non-authenticated users, remove the item from the session cart
            session_cart = request.session.get('cart', {})
            if str(product_id) in session_cart:
                del session_cart[str(product_id)]
                request.session['cart'] = session_cart

                cart_count = sum(session_cart.values())
                return JsonResponse({'status': 'success', 'cart_quantity': cart_count})
            else:
                return JsonResponse({'status': 'error', 'message': 'Product not found in the cart'}, status=404)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

