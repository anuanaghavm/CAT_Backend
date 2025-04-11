from django.urls import path
from .views import CreateTimeSlotView, CreateBookingView, AvailableSlotsView,SessionBasedSlotView,CreatedSlotsListView,TimeSlotDetailView,BookingDetailView,BookingListView

urlpatterns = [
    path("slots/create/", CreateTimeSlotView.as_view(), name="create-slots"),
    path("slots/available/", AvailableSlotsView.as_view(), name="available-slots"),
    path("bookings/create/", CreateBookingView.as_view(), name="create-booking"),
    path("session-slots/", SessionBasedSlotView.as_view(), name="session-based-slots"),
    path("slots/list/", CreatedSlotsListView.as_view(), name="created-slots"),
    path("slots/<int:id>/", TimeSlotDetailView.as_view(), name="slot-detail"),  # ✅ For GET, PUT, PATCH, DELETE
    path("booking/<int:id>/", BookingDetailView.as_view(), name="booking-detail"),  # ✅ For GET, PUT, PATCH, DELETE
    path('bookings/', BookingListView.as_view(), name='booking-list'),



]
