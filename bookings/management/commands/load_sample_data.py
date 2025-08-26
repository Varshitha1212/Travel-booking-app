from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
import random
from bookings.models import TravelOption


class Command(BaseCommand):
    help = 'Load sample travel options data'

    def handle(self, *args, **options):
        # Clear existing data
        TravelOption.objects.all().delete()
        
        # Sample cities
        cities = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
            'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose', 
            'Austin', 'Jacksonville', 'Fort Worth', 'Columbus', 'Charlotte', 
            'San Francisco', 'Indianapolis', 'Seattle', 'Denver', 'Washington', 
            'Boston', 'El Paso', 'Nashville', 'Detroit', 'Portland', 'Memphis',
            'Oklahoma City', 'Las Vegas', 'Louisville', 'Baltimore', 'Milwaukee'
        ]
        
        # Travel types with base prices
        travel_types = [
            ('FLIGHT', 200, 50),
            ('TRAIN', 80, 100),
            ('BUS', 40, 150)
        ]
        
        # Create sample travel options
        created_count = 0
        for i in range(30):  # Create 30 travel options
            source = random.choice(cities)
            destination = random.choice([city for city in cities if city != source])
            travel_type, base_price, base_seats = random.choice(travel_types)
            
            # Generate departure time (next 30 days)
            days_ahead = random.randint(1, 30)
            hours = random.randint(0, 23)
            minutes = random.randint(0, 59)
            departure_time = timezone.now() + timedelta(days=days_ahead, hours=hours, minutes=minutes)
            
            # Generate price based on type and distance
            price = base_price + random.randint(0, 300)
            
            # Generate available seats
            available_seats = base_seats + random.randint(-20, 30)
            available_seats = max(10, available_seats)  # Ensure minimum 10 seats
            
            # Create travel option
            TravelOption.objects.create(
                travel_id=f"{travel_type[:2]}{i+1:03d}",
                type=travel_type,
                source=source,
                destination=destination,
                departure_time=departure_time,
                price=price,
                available_seats=available_seats
            )
            created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} travel options!')
        )
        
        # Show some statistics
        flight_count = TravelOption.objects.filter(type='FLIGHT').count()
        train_count = TravelOption.objects.filter(type='TRAIN').count()
        bus_count = TravelOption.objects.filter(type='BUS').count()
        
        self.stdout.write(f'Flights: {flight_count}')
        self.stdout.write(f'Trains: {train_count}')
        self.stdout.write(f'Buses: {bus_count}')
        
        # Show some examples
        self.stdout.write('\nSample travel options:')
        for option in TravelOption.objects.all()[:5]:
            self.stdout.write(f'- {option}')
