from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class TravelOption(models.Model):
    TYPE_CHOICES = [
        ('FLIGHT', 'Flight'),
        ('TRAIN', 'Train'),
        ('BUS', 'Bus'),
    ]
    travel_id = models.CharField(max_length=32, unique=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    source = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    departure_time = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    available_seats = models.PositiveIntegerField(validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.type} {self.source}→{self.destination} @ {self.departure_time}"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    booking_id = models.CharField(max_length=32, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    travel_option = models.ForeignKey(TravelOption, on_delete=models.CASCADE)
    seats = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    total_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='CONFIRMED')

    def __str__(self):
        return self.booking_id


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.full_name or self.user.username

# Create your models here.
