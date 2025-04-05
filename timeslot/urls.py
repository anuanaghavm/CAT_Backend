from django.urls import path
from .views import CreateTimeSlotView, CreateBookingView, AvailableSlotsView

urlpatterns = [
    path("slots/create/", CreateTimeSlotView.as_view(), name="create-slots"),
    path("slots/available/", AvailableSlotsView.as_view(), name="available-slots"),
    path("bookings/create/", CreateBookingView.as_view(), name="create-booking"),
]
