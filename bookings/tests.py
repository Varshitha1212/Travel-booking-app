from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
from .models import TravelOption, Booking


class BookingFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('u', password='p')
        self.opt = TravelOption.objects.create(
            travel_id='T1', type='BUS', source='A', destination='B',
            departure_time=timezone.now(), price=Decimal('10.00'), available_seats=5
        )

    def test_cannot_overbook(self):
        self.client.login(username='u', password='p')
        self.client.post(f'/book/{self.opt.pk}/', {'seats': 10})
        self.opt.refresh_from_db()
        self.assertEqual(self.opt.available_seats, 5)

    def test_confirm_and_cancel(self):
        self.client.login(username='u', password='p')
        self.client.post(f'/book/{self.opt.pk}/', {'seats': 2})
        self.opt.refresh_from_db()
        self.assertEqual(self.opt.available_seats, 3)
        booking = Booking.objects.first()
        self.client.get(f'/cancel/{booking.pk}/')
        self.opt.refresh_from_db()
        self.assertEqual(self.opt.available_seats, 5)

# Create your tests here.
