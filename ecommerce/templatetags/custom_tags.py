from django import template
from django.contrib.humanize.templatetags import humanize
from django.db.models import OuterRef, Subquery
from ecommerce.models import UserActivity, Product

register = template.Library()


@register.inclusion_tag('ecommerce/recently_viewed_products.html')
def render_recently_viewed_products(user):
    # Retrieve the 6 most recently viewed products for the user
    recently_viewed = []
    if user.is_authenticated:
        # Get subquery to find the most recent timestamp for each product
        subquery = UserActivity.objects.filter(
            user=user,
            product=OuterRef('pk')
        ).order_by('-timestamp').values('timestamp')[:1]

        # Retrieve the 6 most recently viewed items for the user, excluding duplicates
        recently_viewed = Product.objects.filter(
            id__in=UserActivity.objects.filter(user=user).annotate(
                recent_timestamp=Subquery(subquery)
            ).values('product')
        ).order_by('-user_activities__timestamp')[:6]

        # Format the price with commas for each viewed_product
        for viewed_product in recently_viewed:
            viewed_product.formatted_old_price = humanize.intcomma(int(viewed_product.old_price)) if viewed_product.old_price is not None else None
            viewed_product.formatted_price = humanize.intcomma(int(viewed_product.new_price))
            if viewed_product.old_price is not None and viewed_product.old_price != 0:
                discount = (viewed_product.old_price - viewed_product.new_price) / viewed_product.old_price * 100
                viewed_product.discount_percentage = round(discount, 2) * -1  # Make it negative
            else:
                viewed_product.discount_percentage = 0

    return {'recently_viewed': recently_viewed}
