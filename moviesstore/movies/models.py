# movies/models.py
from django.db import models
from django.contrib.auth.models import User

class Region(models.Model):
    """Continents/Regions for tracking movie popularity by location"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    zoom_level = models.IntegerField(default=3)

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    """Extended user profile to include region location"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.region}"

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')

    def __str__(self):
        return str(self.id) + ' - ' + self.name
    
    def average_rating(self):
        """Calculate average rating for this movie"""
        from django.db.models import Avg
        avg_rating = self.movierating_set.aggregate(Avg('rating'))['rating__avg']
        return round(avg_rating, 1) if avg_rating else 0
    
    def rating_count(self):
        """Get total number of ratings for this movie"""
        return self.movierating_set.count()
    
    def user_rating(self, user):
        """Get user's rating for this movie"""
        try:
            rating = self.movierating_set.get(user=user)
            return rating.rating
        except MovieRating.DoesNotExist:
            return None

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_reviews', blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name
    
    def like_count(self):
        return self.likes.count()

class MovieRating(models.Model):
    """User ratings for movies (1-5 stars)"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'movie')  # One rating per user per movie
    
    def __str__(self):
        return f"{self.user.username} - {self.movie.name} ({self.rating} stars)"