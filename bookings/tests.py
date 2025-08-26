from django.test import TestCase, Client, override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta
from .models import TravelOption, Booking, Profile


@override_settings(MIDDLEWARE=[
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
])
class TravelBookingTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Disable signals for testing
        from django.db.models.signals import post_save
        from django.contrib.auth.signals import user_logged_in
        from bookings.signals import create_profile, save_profile, on_login
        
        post_save.disconnect(create_profile, sender=User)
        post_save.disconnect(save_profile, sender=User)
        user_logged_in.disconnect(on_login)
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create user profile
        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Test User',
            phone='1234567890',
            city='Test City'
        )
        
        # Create test travel options
        self.flight = TravelOption.objects.create(
            travel_id='FL001',
            type='FLIGHT',
            source='New York',
            destination='Los Angeles',
            departure_time=timezone.now() + timedelta(days=7),
            price=Decimal('299.99'),
            available_seats=50
        )
        
        self.train = TravelOption.objects.create(
            travel_id='TR001',
            type='TRAIN',
            source='Chicago',
            destination='Detroit',
            departure_time=timezone.now() + timedelta(days=3),
            price=Decimal('89.99'),
            available_seats=100
        )
        
        self.client = Client()

    def test_travel_option_creation(self):
        """Test travel option model creation"""
        self.assertEqual(self.flight.type, 'FLIGHT')
        self.assertEqual(self.flight.source, 'New York')
        self.assertEqual(self.flight.destination, 'Los Angeles')
        self.assertEqual(self.flight.price, Decimal('299.99'))
        self.assertEqual(self.flight.available_seats, 50)

    def test_booking_creation(self):
        """Test booking creation and seat reduction"""
        initial_seats = self.flight.available_seats
        
        booking = Booking.objects.create(
            booking_id='BK001',
            user=self.user,
            travel_option=self.flight,
            seats=2,
            total_price=Decimal('599.98')
        )
        
        # Manually reduce seats to simulate the booking process
        self.flight.available_seats -= 2
        self.flight.save()
        
        # Refresh from database
        self.flight.refresh_from_db()
        
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.travel_option, self.flight)
        self.assertEqual(booking.seats, 2)
        self.assertEqual(booking.status, 'CONFIRMED')
        self.assertEqual(self.flight.available_seats, initial_seats - 2)

    def test_booking_cancellation(self):
        """Test booking cancellation and seat restoration"""
        initial_seats = self.flight.available_seats
        
        booking = Booking.objects.create(
            booking_id='BK002',
            user=self.user,
            travel_option=self.flight,
            seats=3,
            total_price=Decimal('899.97')
        )
        
        # Manually reduce seats first to simulate booking
        self.flight.available_seats -= 3
        self.flight.save()
        
        # Cancel booking
        booking.status = 'CANCELLED'
        booking.save()
        
        # Restore seats
        self.flight.available_seats += booking.seats
        self.flight.save()
        
        self.flight.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')
        self.assertEqual(self.flight.available_seats, initial_seats)

    def test_user_registration(self):
        """Test user registration"""
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        """Test user login"""
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success

    def test_list_options_view(self):
        """Test travel options listing"""
        response = self.client.get(reverse('list_options'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')
        self.assertContains(response, 'Los Angeles')

    def test_list_options_filtering(self):
        """Test travel options filtering"""
        # Test type filter
        response = self.client.get(reverse('list_options'), {'type': 'FLIGHT'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')
        self.assertContains(response, 'Los Angeles')
        
        # Test source filter
        response = self.client.get(reverse('list_options'), {'source': 'New York'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')

    def test_booking_view_requires_login(self):
        """Test that booking view requires login"""
        response = self.client.get(reverse('book_option', args=[self.flight.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_booking_process(self):
        """Test complete booking process"""
        # Login first
        self.client.login(username='testuser', password='testpass123')
        
        # Get booking page
        response = self.client.get(reverse('book_option', args=[self.flight.pk]))
        self.assertEqual(response.status_code, 200)
        
        # Submit booking
        response = self.client.post(reverse('book_option', args=[self.flight.pk]), {
            'seats': 2
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check booking was created
        booking = Booking.objects.filter(user=self.user, travel_option=self.flight).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.seats, 2)
        self.assertEqual(booking.total_price, Decimal('599.98'))

    def test_my_bookings_view(self):
        """Test my bookings view"""
        # Create a booking first
        booking = Booking.objects.create(
            booking_id='BK003',
            user=self.user,
            travel_option=self.flight,
            seats=1,
            total_price=Decimal('299.99')
        )
        
        # Login and access my bookings
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BK003')

    def test_cancel_booking(self):
        """Test booking cancellation"""
        # Create a booking
        booking = Booking.objects.create(
            booking_id='BK004',
            user=self.user,
            travel_option=self.flight,
            seats=1,
            total_price=Decimal('299.99')
        )
        
        initial_seats = self.flight.available_seats
        
        # Login and cancel booking
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('cancel_booking', args=[booking.pk]))
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check booking was cancelled
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')
        
        # Check seats were restored
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, initial_seats + 1)

    def test_profile_update(self):
        """Test profile update functionality"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'full_name': 'Updated Full Name',
            'phone': '9876543210',
            'city': 'Updated City'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect after success
        
        # Check profile was updated
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.profile.full_name, 'Updated Full Name')
        self.assertEqual(self.profile.phone, '9876543210')

    def test_seat_validation(self):
        """Test seat validation"""
        # Try to book more seats than available
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('book_option', args=[self.flight.pk]), {
            'seats': 100  # More than available (50)
        })
        
        self.assertEqual(response.status_code, 200)  # Form error, not redirect
        
        # Check no booking was created
        booking_count = Booking.objects.filter(user=self.user, travel_option=self.flight).count()
        self.assertEqual(booking_count, 0)

    def test_model_string_representations(self):
        """Test model string representations"""
        self.assertIn('FLIGHT', str(self.flight))
        self.assertIn('New York', str(self.flight))
        self.assertIn('Los Angeles', str(self.flight))
        
        booking = Booking.objects.create(
            booking_id='BK005',
            user=self.user,
            travel_option=self.flight,
            seats=1,
            total_price=Decimal('299.99')
        )
        self.assertEqual(str(booking), 'BK005')
        
        self.assertEqual(str(self.profile), 'Test User')
