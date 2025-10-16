from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from movies.models import Movie, Region, UserProfile
from cart.models import Order, Item
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Populate the database with continents and clean up dummy data'

    def handle(self, *args, **options):
        self.stdout.write('Cleaning up dummy data...')
        
        # Remove all existing dummy orders
        Order.objects.all().delete()
        self.stdout.write('Removed all existing orders')
        
        # Create the 6 specified continents/regions
        regions_data = [
            {'name': 'South America', 'latitude': -15.7801, 'longitude': -47.9292, 'zoom_level': 3},
            {'name': 'Europe', 'latitude': 54.5260, 'longitude': 15.2551, 'zoom_level': 3},
            {'name': 'Asia', 'latitude': 35.8617, 'longitude': 104.1954, 'zoom_level': 3},
            {'name': 'North America', 'latitude': 45.5017, 'longitude': -73.5673, 'zoom_level': 3},
            {'name': 'Africa', 'latitude': 8.7832, 'longitude': 34.5085, 'zoom_level': 3},
            {'name': 'Australia', 'latitude': -25.2744, 'longitude': 133.7751, 'zoom_level': 3},
        ]
        
        regions = []
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data['name'],
                defaults=region_data
            )
            regions.append(region)
            if created:
                self.stdout.write(f'Created region: {region.name}')
            else:
                self.stdout.write(f'Region already exists: {region.name}')
        
        # Get existing movies
        movies = list(Movie.objects.all())
        if not movies:
            self.stdout.write('No movies found. Please add some movies first.')
            return
        
        self.stdout.write('Regions created successfully!')
        self.stdout.write(f'Created {len(regions)} regions')
        self.stdout.write('')
        self.stdout.write('Next steps:')
        self.stdout.write('1. Users need to select their region during signup')
        self.stdout.write('2. When users make purchases, their region will be tracked')
        self.stdout.write('3. The map will show real purchase data by region')
        self.stdout.write('')
        self.stdout.write('To test with sample data, create some users and make purchases!')
