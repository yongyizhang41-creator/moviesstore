from django.db.models import Sum, Count
from cart.models import Item
from .models import Review

def get_region_top_movies(region, limit=5):
    return list(
        Item.objects
        .filter(order__region=region, quantity__gt=0)
        .values('movie_id', 'movie__name')
        .annotate(purchase_count=Sum('quantity'))
        .order_by('-purchase_count','movie_id')[:limit]
    )
def get_most_purchased_movie():
    return (
        Item.objects
        .values('movie_id', 'movie__name')
        .annotate(purchase_count=Sum('quantity'))
        .order_by('-purchase_count', 'movie_id')
        .first()
    )

def get_most_reviewed_movie():
    return (
        Review.objects
        .values('movie_id', 'movie__name')
        .annotate(review_count=Count('id'))
        .order_by('-review_count', 'movie_id')    
        .first()
    )