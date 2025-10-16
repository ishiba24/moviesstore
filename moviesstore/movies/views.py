# movies/views.py - CORRECTED VERSION
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Region, UserProfile, MovieRating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import models
from cart.models import Order, Item
import json

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

def show(request, id):
    movie = Movie.objects.get(id=id)
    # CORRECTED: Use annotate to add like_count, then order by it
    reviews = Review.objects.filter(movie=movie).annotate(
        like_count=models.Count('likes')
    ).order_by('-like_count', '-date')

    # Get user's rating for this movie (if logged in)
    user_rating = None
    if request.user.is_authenticated:
        user_rating = movie.user_rating(request.user)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    template_data['user_rating'] = user_rating
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
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
def like_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    if request.user in review.likes.all():
        review.likes.remove(request.user)
        liked = False
    else:
        review.likes.add(request.user)
        liked = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'liked': liked,
            'like_count': review.like_count()
        })
    
    return redirect('movies.show', id=id)

def top_comments(request):
    # Get all reviews ordered by like count (descending)
    top_reviews = Review.objects.annotate(
        like_count=models.Count('likes')
    ).order_by('-like_count', '-date')[:20]  # Top 20 reviews
    
    template_data = {}
    template_data['title'] = 'Top Comments'
    template_data['reviews'] = top_reviews
    return render(request, 'movies/top_comments.html', {'template_data': template_data})

def local_popularity_map(request):
    """Display the Local Popularity Map page"""
    regions = Region.objects.all()

    # Convert regions to JSON format for JavaScript
    regions_json = []
    for region in regions:
        regions_json.append({
            'id': region.id,
            'name': region.name,
            'lat': float(region.latitude),
            'lng': float(region.longitude),
            'zoom': region.zoom_level
        })

    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    template_data['regions'] = json.dumps(regions_json)
    return render(request, 'movies/local_popularity_map.html', {'template_data': template_data})

def region_movies_api(request, region_id):
    """API endpoint to get trending movies for a specific region"""
    try:
        region = Region.objects.get(id=region_id)

        # Get all orders for this region
        region_orders = Order.objects.filter(region=region)

        # Get movie popularity data
        movie_popularity = {}
        for order in region_orders:
            items = Item.objects.filter(order=order)
            for item in items:
                movie = item.movie
                if movie.id not in movie_popularity:
                    movie_popularity[movie.id] = {
                        'movie': movie,
                        'total_quantity': 0,
                        'total_revenue': 0
                    }
                movie_popularity[movie.id]['total_quantity'] += item.quantity
                movie_popularity[movie.id]['total_revenue'] += item.price * item.quantity

        # Sort by total quantity (most popular first)
        sorted_movies = sorted(
            movie_popularity.values(),
            key=lambda x: x['total_quantity'],
            reverse=True
        )[:10]  # Top 10 movies

        # Format response
        response_data = {
            'region': {
                'id': region.id,
                'name': region.name,
                'latitude': region.latitude,
                'longitude': region.longitude
            },
            'trending_movies': [
                {
                    'id': movie_data['movie'].id,
                    'name': movie_data['movie'].name,
                    'price': movie_data['movie'].price,
                    'image': movie_data['movie'].image.url,
                    'total_quantity': movie_data['total_quantity'],
                    'total_revenue': movie_data['total_revenue']
                }
                for movie_data in sorted_movies
            ]
        }

        return JsonResponse(response_data)

    except Region.DoesNotExist:
        return JsonResponse({'error': 'Region not found'}, status=404)

@login_required
def rate_movie(request, id):
    """Rate a movie (1-5 stars)"""
    if request.method == 'POST':
        try:
            rating_value = int(request.POST.get('rating'))
            if rating_value < 1 or rating_value > 5:
                return JsonResponse({'error': 'Invalid rating value'}, status=400)
            
            movie = get_object_or_404(Movie, id=id)
            
            # Create or update rating
            rating, created = MovieRating.objects.get_or_create(
                user=request.user,
                movie=movie,
                defaults={'rating': rating_value}
            )
            
            if not created:
                rating.rating = rating_value
                rating.save()
            
            # Return updated movie rating data
            response_data = {
                'success': True,
                'user_rating': rating_value,
                'average_rating': movie.average_rating(),
                'rating_count': movie.rating_count()
            }
            
            return JsonResponse(response_data)
            
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid rating value'}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def remove_rating(request, id):
    """Remove user's rating for a movie"""
    if request.method == 'POST':
        try:
            movie = get_object_or_404(Movie, id=id)
            
            # Try to find and delete the user's rating
            try:
                rating = MovieRating.objects.get(user=request.user, movie=movie)
                rating.delete()
                
                # Return updated movie rating data
                response_data = {
                    'success': True,
                    'user_rating': None,
                    'average_rating': movie.average_rating(),
                    'rating_count': movie.rating_count()
                }
                
                return JsonResponse(response_data)
                
            except MovieRating.DoesNotExist:
                return JsonResponse({'error': 'No rating found to remove'}, status=404)
                
        except Exception as e:
            return JsonResponse({'error': 'Error removing rating'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)