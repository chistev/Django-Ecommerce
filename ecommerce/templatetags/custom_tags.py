from django import template
from django.contrib.humanize.templatetags import humanize
from django.db.models import OuterRef, Subquery
from ecommerce.models import UserActivity, Product

register = template.Library()

@register.inclusion_tag('ecommerce/recently_viewed_products.html')
def render_recently_viewed_products(request):
    # Retrieve recently viewed products
    recently_viewed = []

    if not request.user.is_authenticated:
        # For non-authenticated users, retrieve recently viewed products from session
        recently_viewed_product_ids = request.session.get('recently_viewed', [])
        recently_viewed = Product.objects.filter(id__in=recently_viewed_product_ids)[:6]
    else:
        # For authenticated users, retrieve recently viewed products using UserActivity
        user = request.user
        recently_viewed_product_ids = UserActivity.objects.filter(user=user).order_by('-timestamp').values_list('product', flat=True)[:6]
        recently_viewed = Product.objects.filter(id__in=recently_viewed_product_ids)

    # Format the price with commas for each viewed product
    for product in recently_viewed:
        if product.old_price is not None and product.old_price != 0:
            discount = (product.old_price - product.new_price) / product.old_price * 100
            product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            product.discount_percentage = 0

        product.formatted_old_price = humanize.intcomma(int(product.old_price)) if product.old_price is not None else None
        product.formatted_price = humanize.intcomma(int(product.new_price))

    return {'recently_viewed': recently_viewed}


def update_recently_viewed(request, product):
    if not request.user.is_authenticated:
        recently_viewed_product_ids = request.session.get('recently_viewed', [])
        if product.id in recently_viewed_product_ids:
            recently_viewed_product_ids.remove(product.id)
        recently_viewed_product_ids.insert(0, product.id)
        # Ensure the list doesn't exceed 6 items
        request.session['recently_viewed'] = recently_viewed_product_ids[:6]
    else:
        user = request.user
        # Update or create UserActivity record
        user_activity, created = UserActivity.objects.get_or_create(user=user, product=product)
        # Set saved status to False if not already saved
        if created:
            user_activity.saved = False
            user_activity.save()
        # Retrieve the 6 most recent activities
        recent_activities = UserActivity.objects.filter(user=user).order_by('-timestamp')[:6]
        # Extract product IDs from the recent activities
        recently_viewed_product_ids = [activity.product_id for activity in recent_activities]

    # Retrieve the products based on the IDs
    recently_viewed = Product.objects.filter(id__in=recently_viewed_product_ids)

    # Format the price with commas for each viewed product
    for product in recently_viewed:
        if product.old_price is not None and product.old_price != 0:
            discount = (product.old_price - product.new_price) / product.old_price * 100
            product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            product.discount_percentage = 0

        product.formatted_old_price = humanize.intcomma(
            int(product.old_price)) if product.old_price is not None else None
        product.formatted_price = humanize.intcomma(int(product.new_price))

        # Check if the product is saved by the user and update saved status
        if request.user.is_authenticated:
            product.saved = UserActivity.objects.filter(user=user, product=product, saved=True).exists()
        else:
            product.saved = False  # Default to False if user is not authenticated

    return recently_viewed
