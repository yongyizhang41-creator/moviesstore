from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item, Region
from django.db import transaction
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required



@require_POST
@login_required(login_url='accounts.login')
def purchase(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart.index')

    region_id = request.POST.get('region')
    if not region_id or not region_id.isdecimal():
        return redirect('cart.index')

    region = get_object_or_404(Region, id=int(region_id))
    movies_in_cart = list(Movie.objects.filter(id__in=cart.keys()))

    if not movies_in_cart:
        return redirect('cart.index')

    try:
        quantities = {
            movie.id: int(cart[str(movie.id)])
            for movie in movies_in_cart
        }
    except (ValueError, TypeError, KeyError):
        return redirect('cart.index')

    if any(not 1 <= quantity <=10 for quantity in quantities.values()):
        return redirect('cart.index')


    cart_total = sum(
        movie.price * quantities[movie.id]
        for movie in movies_in_cart
    )

    with transaction.atomic():
        order = Order.objects.create(
            user = request.user,
            total = cart_total,
            region = region
        )
        for movie in movies_in_cart:
            Item.objects.create(
                movie = movie, 
                price = movie.price, 
                order = order, 
                quantity = quantities[movie.id]
            )

    request.session['cart'] = {}

    template_data = {
        'title': 'Purchase confirmation',
        'order_id': order.id
    }
    return render(
        request,
        'cart/purchase.html', 
        {'template_data': template_data}
    )




def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    template_data['regions'] = Region.objects.order_by('name')
    return render(request, 'cart/index.html',
        {'template_data': template_data})



@require_POST
def add(request, id):
    get_object_or_404(Movie, id=id)

    try:
        quantity = int(request.POST.get('quantity', ''))
    except (ValueError, TypeError):
        return redirect('movies.show', id=id)
    if not 1<= quantity <= 10:
        return redirect('movies.show', id=id)
    
    cart = request.session.get('cart', {})
    cart[str(id)] = quantity
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')