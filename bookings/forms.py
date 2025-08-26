from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Booking, Profile


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['seats']

    def __init__(self, *args, **kwargs):
        self.travel_option = kwargs.pop('travel_option', None)
        super().__init__(*args, **kwargs)
        if self.travel_option:
            self.fields['seats'].widget.attrs.update({'min': 1, 'max': self.travel_option.available_seats})

    def clean_seats(self):
        seats = self.cleaned_data['seats']
        if self.travel_option and seats > self.travel_option.available_seats:
            raise ValidationError('Not enough seats available.')
        return seats


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['full_name', 'phone', 'city']

