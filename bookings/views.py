from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import TravelOption, Booking
from .forms import BookingForm, UserForm, ProfileForm


def list_options(request):
    qs = TravelOption.objects.all()
    t = request.GET.get('type')
    s = request.GET.get('source')
    d = request.GET.get('destination')
    date = request.GET.get('date')
    if t:
        qs = qs.filter(type=t)
    if s:
        qs = qs.filter(source__icontains=s)
    if d:
        qs = qs.filter(destination__icontains=d)
    if date:
        qs = qs.filter(departure_time__date=date)
    return render(request, 'bookings/list_options.html', {'options': qs})


@login_required
def book_option(request, pk):
    option = get_object_or_404(TravelOption, pk=pk)
    form = BookingForm(request.POST or None, travel_option=option)
    if request.method == 'POST' and form.is_valid():
        seats = form.cleaned_data['seats']
        total = Decimal(seats) * option.price
        Booking.objects.create(
            booking_id=str(timezone.now().timestamp()).replace('.', ''),
            user=request.user,
            travel_option=option,
            seats=seats,
            total_price=total,
        )
        option.available_seats -= seats
        option.save(update_fields=['available_seats'])
        messages.success(request, 'Booking confirmed.')
        return redirect('my_bookings')
    return render(request, 'bookings/book_option.html', {'option': option, 'form': form})


@login_required
def my_bookings(request):
    qs = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'bookings/my_bookings.html', {'bookings': qs})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, user=request.user)
    if booking.status != 'CANCELLED':
        booking.status = 'CANCELLED'
        booking.save(update_fields=['status'])
        opt = booking.travel_option
        opt.available_seats += booking.seats
        opt.save(update_fields=['available_seats'])
        messages.info(request, 'Booking cancelled.')
    return redirect('my_bookings')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def profile(request):
    user_form = UserForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=getattr(request.user, 'profile', None))
    if request.method == 'POST' and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'bookings/profile.html', {'user_form': user_form, 'profile_form': profile_form})
