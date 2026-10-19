from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from cart.models import Region
from .services import (
    get_most_purchased_movie,
    get_most_reviewed_movie,
    get_region_top_movies,
)
from .forms import RatingForm
from django.contrib import messages
from django.db.models import Avg, Count
from django.contrib.admin.views.decorators import staff_member_required

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})
# Create your views here.

def show(request, id):
    movie = get_object_or_404(Movie, id=id)
    reviews = Review.objects.filter(movie=movie)

    rating_stats = movie.ratings.aggregate(
        average = Avg('score'),
        count = Count('id'),
    )

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            movie = movie,
            user = request.user,
        ).first()

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['rating_form'] = RatingForm(instance = user_rating)
    template_data['user_rating'] = user_rating
    template_data['average_rating'] = rating_stats['average']
    template_data['rating_count'] = rating_stats['count']
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
@require_POST
def rate_movie(request, id):
    movie = get_object_or_404(Movie, id = id)
    form = RatingForm(request.POST)
    if not form.is_valid():
        messages.error(
            request,
            'Please select a whole-number rating from 1 to 5.',
        )
        return redirect('movies.show', id = id)

    rating, created = Rating.objects.update_or_create(
        movie = movie,
        user = request.user,
        defaults = {'score': form.cleaned_data['score']},
    )

    if created:
        messages.success(request, 'Your rating has been saved.')
    else:
        messages.success(request, 'Your rating has been updated.')

    return redirect('movies.show', id = id)

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
@require_POST
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie_id=id)
    review.delete()
    return redirect('movies.show', id=id)


@login_required(login_url='accounts.login')
def popularity_map(request):
    regions = list(Region.objects.order_by('name'))
    selected_region = None

    region_id = request.GET.get('region')
    if region_id:
        if not region_id.isdecimal():
            return redirect('movies.popularity_map')
        selected_region = get_object_or_404(Region, id=int(region_id))
    elif regions:
        selected_region = regions[0]

    top_movies = (
        get_region_top_movies(selected_region)
        if selected_region else []
    )

    map_regions = [
        {
            'id': region.id,
            'name': region.name,
            'latitude': region.latitude,
            'longitude': region.longitude
        }
        for region in regions
    ]

    template_data = {
        'title': 'Local Popularity Map',
        'regions': regions,
        'selected_region':selected_region,
        'top_movies': top_movies,
        "map_regions": map_regions
    }

    return render (
        request,
        'movies/popularity_map.html',
        {'template_data': template_data}
    )

@staff_member_required(login_url='accounts.login')
def admin_statistics(request):
    template_data = {
        'title': 'Movie Statistics',
        'most_purchased_movie': get_most_purchased_movie(),
        'most_reviewed_movie': get_most_reviewed_movie(),
    }

    return render (
        request,
        'movies/admin_statistics.html',
        {'template_data': template_data}
    )

@staff_member_required(login_url='accounts.login')
def top_commenter(request):
    top = (
        Review.objects
        .values('user__username')
        .annotate(total=Count('id'))
        .order_by('-total', 'user__username')
        .first()
    )

    template_data = {}
    template_data['title'] = 'Top Commenter'
    template_data['top'] = top
    return render(request, 'movies/top_commenter.html', {'template_data': template_data})
