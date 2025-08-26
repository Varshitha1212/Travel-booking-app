from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from decimal import Decimal
from .models import TravelOption, Booking, Profile


class TravelOptionModelTest(TestCase):
    def setUp(self):
        self.travel_option = TravelOption.objects.create(
            travel_id='FL001',
            type='FLIGHT',
            source='New York',
            destination='Los Angeles',
            departure_time=timezone.now() + timezone.timedelta(days=1),
            price=Decimal('299.99'),
            available_seats=100
        )

    def test_travel_option_creation(self):
        self.assertEqual(self.travel_option.travel_id, 'FL001')
        self.assertEqual(self.travel_option.type, 'FLIGHT')
        self.assertEqual(self.travel_option.source, 'New York')
        self.assertEqual(self.travel_option.destination, 'Los Angeles')
        self.assertEqual(self.travel_option.price, Decimal('299.99'))
        self.assertEqual(self.travel_option.available_seats, 100)

    def test_travel_option_str(self):
        expected_str = f"FLIGHT New York→Los Angeles @ {self.travel_option.departure_time}"
        self.assertEqual(str(self.travel_option), expected_str)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='FL001',
            type='FLIGHT',
            source='New York',
            destination='Los Angeles',
            departure_time=timezone.now() + timezone.timedelta(days=1),
            price=Decimal('299.99'),
            available_seats=100
        )
        self.booking = Booking.objects.create(
            booking_id='BK001',
            user=self.user,
            travel_option=self.travel_option,
            seats=2,
            total_price=Decimal('599.98'),
            status='CONFIRMED'
        )

    def test_booking_creation(self):
        self.assertEqual(self.booking.booking_id, 'BK001')
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.travel_option, self.travel_option)
        self.assertEqual(self.booking.seats, 2)
        self.assertEqual(self.booking.total_price, Decimal('599.98'))
        self.assertEqual(self.booking.status, 'CONFIRMED')

    def test_booking_str(self):
        self.assertEqual(str(self.booking), 'BK001')


class ProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = Profile.objects.create(
            user=self.user,
            full_name='Test User',
            phone='1234567890',
            city='New York'
        )

    def test_profile_creation(self):
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.full_name, 'Test User')
        self.assertEqual(self.profile.phone, '1234567890')
        self.assertEqual(self.profile.city, 'New York')

    def test_profile_str(self):
        self.assertEqual(str(self.profile), 'Test User')


class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='FL001',
            type='FLIGHT',
            source='New York',
            destination='Los Angeles',
            departure_time=timezone.now() + timezone.timedelta(days=1),
            price=Decimal('299.99'),
            available_seats=100
        )

    def test_list_options_view(self):
        response = self.client.get(reverse('list_options'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Travel Options')
        self.assertContains(response, 'New York')

    def test_list_options_with_filters(self):
        response = self.client.get(reverse('list_options'), {
            'type': 'FLIGHT',
            'source': 'New York'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')

    def test_book_option_view_requires_login(self):
        response = self.client.get(reverse('book_option', args=[self.travel_option.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_book_option_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_option', args=[self.travel_option.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'New York')

    def test_booking_process(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('book_option', args=[self.travel_option.pk]), {
            'seats': 2
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        
        # Check if booking was created
        booking = Booking.objects.filter(user=self.user).first()
        self.assertIsNotNone(booking)
        self.assertEqual(booking.seats, 2)
        self.assertEqual(booking.total_price, Decimal('599.98'))

    def test_my_bookings_view_requires_login(self):
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_my_bookings_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'My Bookings')

    def test_cancel_booking(self):
        self.client.login(username='testuser', password='testpass123')
        
        # Create a booking first
        booking = Booking.objects.create(
            booking_id='BK001',
            user=self.user,
            travel_option=self.travel_option,
            seats=2,
            total_price=Decimal('599.98'),
            status='CONFIRMED'
        )
        
        # Update available seats
        self.travel_option.available_seats = 98
        self.travel_option.save()
        
        # Cancel the booking
        response = self.client.get(reverse('cancel_booking', args=[booking.pk]))
        self.assertEqual(response.status_code, 302)  # Redirect after cancellation
        
        # Check if booking was cancelled
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'CANCELLED')
        
        # Check if seats were restored
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, 100)

    def test_signup_view(self):
        response = self.client.get(reverse('signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign up')

    def test_signup_process(self):
        response = self.client.post(reverse('signup'), {
            'username': 'newuser',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        
        # Check if user was created
        user = User.objects.filter(username='newuser').first()
        self.assertIsNotNone(user)

    def test_profile_view_requires_login(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Profile')


class FormValidationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            travel_id='FL001',
            type='FLIGHT',
            source='New York',
            destination='Los Angeles',
            departure_time=timezone.now() + timezone.timedelta(days=1),
            price=Decimal('299.99'),
            available_seats=5  # Limited seats for testing
        )

    def test_booking_form_validation_exceeds_available_seats(self):
        from .forms import BookingForm
        
        form_data = {'seats': 10}  # More than available
        form = BookingForm(data=form_data, travel_option=self.travel_option)
        
        self.assertFalse(form.is_valid())
        self.assertIn('seats', form.errors)

    def test_booking_form_validation_valid_seats(self):
        from .forms import BookingForm
        
        form_data = {'seats': 3}  # Within available seats
        form = BookingForm(data=form_data, travel_option=self.travel_option)
        
        self.assertTrue(form.is_valid())
