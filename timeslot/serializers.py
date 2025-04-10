from rest_framework import serializers
from .models import Booking, TimeSlot

from rest_framework import serializers
from pytz import timezone
from .models import TimeSlot

from rest_framework import serializers
from pytz import timezone
from .models import TimeSlot

IST = timezone('Asia/Kolkata')

class TimeSlotSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    time_period = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'session_type', 'start_time', 'end_time', 'max_capacity', 'time_period','zoom_link']

    def get_start_time(self, obj):
        return obj.start_time.astimezone(IST).strftime("%I:%M %p")

    def get_end_time(self, obj):
        return obj.end_time.astimezone(IST).strftime("%I:%M %p")

    def get_time_period(self, obj):
        hour = obj.start_time.astimezone(IST).hour
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"
