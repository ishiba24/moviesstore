# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from movies.models import Movie, UserProfile
from .utils import calculate_cart_total
from .models import Order, Item, CheckoutFeedback
from .forms import CheckoutFeedbackForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if (movie_ids == []):
        return redirect('cart.index')
    
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)

    order = Order()
    order.user = request.user
    order.total = cart_total
    
    # Get user's region from their profile
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        order.region = user_profile.region
    except UserProfile.DoesNotExist:
        # If user doesn't have a profile, region will be None
        pass
    
    order.save()

    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()

    request.session['cart'] = {}
    
    # Create feedback form for the popup
    feedback_form = CheckoutFeedbackForm()
    
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    template_data['feedback_form'] = feedback_form
    template_data['order'] = order
    return render(request, 'cart/purchase.html', {'template_data': template_data})

@login_required
def submit_feedback(request):
    if request.method == 'POST':
        form = CheckoutFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            # Try to link to the most recent order by this user
            try:
                recent_order = Order.objects.filter(user=request.user).latest('date')
                feedback.order = recent_order
            except Order.DoesNotExist:
                pass
            feedback.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Thank you for your feedback!'})
            else:
                messages.success(request, 'Thank you for your feedback!')
                return redirect('home.index')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    
    return redirect('home.index')

def feedback_list(request):
    # Get all feedback ordered by most recent
    feedback_list = CheckoutFeedback.objects.all().order_by('-date_submitted')
    
    template_data = {}
    template_data['title'] = 'Customer Feedback'
    template_data['feedback_list'] = feedback_list
    return render(request, 'cart/feedback_list.html', {'template_data': template_data})