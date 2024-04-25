from django import template
from django.contrib.humanize.templatetags import humanize
from django.db.models import OuterRef, Subquery
from ecommerce.models import UserActivity, Product

register = template.Library()


@register.inclusion_tag('ecommerce/recently_viewed_products.html')
def render_recently_viewed_products(request):
    if not request.user.is_authenticated:
        recently_viewed_product_ids = request.session.get('recently_viewed', [])
        recently_viewed = Product.objects.filter(id__in=recently_viewed_product_ids)
    else:
        user = request.user
        subquery = UserActivity.objects.filter(
            user=user,
            product=OuterRef('pk')
        ).order_by('-timestamp').values('timestamp')[:1]
        recently_viewed = Product.objects.filter(
            id__in=UserActivity.objects.filter(user=user).annotate(
                recent_timestamp=Subquery(subquery)
            ).values('product')
        )[:6]

    for product in recently_viewed:
        if product.old_price is not None and product.old_price != 0:
            discount = (product.old_price - product.new_price) / product.old_price * 100
            product.discount_percentage = round(discount, 2) * -1  # Make it negative
        else:
            product.discount_percentage = 0

        product.formatted_old_price = humanize.intcomma(int(product.old_price)) if product.old_price is not None else \
            None
        product.formatted_price = humanize.intcomma(int(product.new_price))

    return {'recently_viewed': recently_viewed}