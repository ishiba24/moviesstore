# cart/models.py
from django.db import models
from django.contrib.auth.models import User
from movies.models import Movie, Region

class Order(models.Model):
    id = models.AutoField(primary_key=True)
    total = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.user.username

class Item(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.IntegerField()
    quantity = models.IntegerField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class CheckoutFeedback(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)  # Optional name field
    feedback_text = models.TextField(max_length=500)  # User's thoughts on checkout process
    date_submitted = models.DateTimeField(auto_now_add=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)  # Link to order
    
    def __str__(self):
        if self.name:
            return f"Feedback by {self.name} - {self.date_submitted.date()}"
        else:
            return f"Anonymous feedback - {self.date_submitted.date()}"
    
    def display_name(self):
        return self.name if self.name else "Anonymous"