from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_options, name='list_options'),
    path('book/<int:pk>/', views.book_option, name='book_option'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:pk>/', views.cancel_booking, name='cancel_booking'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
]


