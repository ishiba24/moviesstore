# movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review, name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('<int:id>/review/<int:review_id>/like/', views.like_review, name='movies.like_review'),
    path('top-comments/', views.top_comments, name='movies.top_comments'),
    path('local-popularity-map/', views.local_popularity_map, name='movies.local_popularity_map'),
    path('api/region/<int:region_id>/movies/', views.region_movies_api, name='movies.region_movies_api'),
    path('<int:id>/rate/', views.rate_movie, name='movies.rate_movie'),
    path('<int:id>/remove-rating/', views.remove_rating, name='movies.remove_rating'),
]