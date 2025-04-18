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
    date = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'session_type', 'start_time', 'end_time', 'max_capacity', 'time_period','zoom_link','date','created_at','course_name','time_duration']
        read_only_fields = ['created_at']

    def get_start_time(self, obj):
        return obj.start_time.astimezone(IST).strftime("%I:%M %p")

    def get_end_time(self, obj):
        return obj.end_time.astimezone(IST).strftime("%I:%M %p")
    

    def get_date(self, obj):
        return obj.start_time.astimezone(IST).strftime("%Y-%m-%d")


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
    def get_created_at(self, obj):
        return obj.created_at.astimezone(IST).strftime("%I:%M %p") if obj.created_at else None

class BookingSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    time_slot = TimeSlotSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'uuid', 'name', 'last_name', 'target', 'email', 'mobile',
            'session_type', 'created_at', 'zoom_link', 'time_slot'
        ]

    def get_created_at(self, obj):
        if obj.created_at:
            return obj.created_at.astimezone(IST).strftime("%Y-%m-%d")
        return None
