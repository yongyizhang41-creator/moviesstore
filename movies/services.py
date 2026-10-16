from django.db.models import Sum
from cart.models import Item

def get_region_top_movies(region, limit=5):
    return list(
        Item.objects
        .filter(order__region=region, quantity__gt=0)
        .values('movie_id', 'movie__name')
        .annotate(purchase_count=Sum('quantity'))
        .order_by('-purchase_count','movie_id')[:limit]
    )