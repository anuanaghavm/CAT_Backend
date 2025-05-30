import uuid
from django.db import models
from django.utils.timezone import make_naive
from pytz import timezone
IST = timezone('Asia/Kolkata')

SESSION_TYPE_CHOICES = (
    ("group", "Group"),
    ("one_to_one", "One to One"),
)

class TimeSlot(models.Model):
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.IntegerField(default=1)
    zoom_link = models.URLField(blank=True, null=True)  # ADD THIS LINE
    date = models.DateField()  # optional if you want it separately
    created_at = models.DateTimeField(auto_now_add=True)
    course_name = models.CharField(max_length=100, blank=True, null=True)  # optional if you want it separately
    time_duration = models.IntegerField(default=30)  # in minutes
    def __str__(self):
        return f"{self.session_type} | {self.start_time.strftime('%b %d %I:%M %p')}"
    
    def start_time_ist(self):
        return make_naive(self.start_time, IST).strftime('%I:%M %p')

    def end_time_ist(self):
        return make_naive(self.end_time, IST).strftime('%I:%M %p')


class Booking(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    target = models.TextField()
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name="bookings")
    created_at = models.DateTimeField(auto_now_add=True)
    zoom_link = models.URLField(blank=True, null=True)  
    def __str__(self):
        return f"{self.name} | {self.session_type} | {self.time_slot}"



