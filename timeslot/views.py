from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, F
from pytz import timezone as pytz_timezone

from .zoom_utils import get_zoom_access_token, create_zoom_meeting
from .models import TimeSlot, Booking
from .serializers import TimeSlotSerializer, BookingSerializer

IST = pytz_timezone("Asia/Kolkata")


class CreateTimeSlotView(APIView):
    def post(self, request):
        session_type = request.data.get("session_type")
        start_hour = int(request.data.get("start_hour", 10))
        end_hour = int(request.data.get("end_hour", 17))
        date = timezone.now().date()

        slots = []
        for hour in range(start_hour, end_hour):
            start_time = timezone.make_aware(datetime.combine(date, datetime.min.time())) + timedelta(hours=hour)
            end_time = start_time + timedelta(hours=1)
            slot = TimeSlot.objects.create(
                session_type=session_type,
                start_time=start_time,
                end_time=end_time,
                max_capacity=1 if session_type == "one_to_one" else 2
            )
            slots.append(slot)

        return Response({
            "message": "Slots created successfully.",
            "slots": TimeSlotSerializer(slots, many=True).data
        }, status=status.HTTP_201_CREATED)


class AvailableSlotsView(APIView):
    def get(self, request):
        session_type = request.query_params.get("type")
        if not session_type:
            return Response({"error": "Session type is required"}, status=400)

        available_slots = TimeSlot.objects.filter(
            session_type=session_type,
            start_time__gt=timezone.now()
        ).annotate(
            booked_count=Count("bookings")
        ).filter(
            booked_count__lt=F("max_capacity")
        ).order_by("start_time")

        slots_data = [
            {
                "id": slot.id,
                "start_time": slot.start_time.astimezone(IST).strftime("%I:%M %p"),
                "end_time": slot.end_time.astimezone(IST).strftime("%I:%M %p"),
                "session_type": slot.session_type,
                "remaining": slot.max_capacity - slot.bookings.count()
            }
            for slot in available_slots
        ]

        return Response({
            "message": "Available slots fetched.",
            "slots": slots_data
        })


class CreateBookingView(APIView):
    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            mobile = serializer.validated_data["mobile"]
            time_slot = serializer.validated_data["time_slot"]

            # Check if the user has a pending booking
            existing_booking = Booking.objects.filter(
                email=email,
                mobile=mobile,
                time_slot__end_time__gt=timezone.now()
            ).first()

            if existing_booking:
                return Response({
                    "error": "You already have a booking. Please wait until it’s completed to book again."
                }, status=400)

            if time_slot.bookings.count() >= time_slot.max_capacity:
                return Response({"error": "This time slot is already full."}, status=400)

            # Generate Zoom Meeting
            try:
                access_token = get_zoom_access_token()
                if not access_token:
                    raise Exception("Zoom access token not retrieved")

                meeting = create_zoom_meeting(
                    access_token,
                    topic=f"Session with {serializer.validated_data['name']}",
                    start_time=time_slot.start_time
                )

                zoom_link = meeting.get("join_url")
                if not zoom_link:
                    raise Exception(meeting.get("error", "Zoom meeting creation failed."))

            except Exception as e:
                print("❌ Zoom Error:", str(e))
                return Response({
                    "error": f"Zoom meeting creation failed. Reason: {str(e)}"
                }, status=500)

            # Save Booking
            booking = serializer.save(zoom_link=zoom_link)

            return Response({
                "message": "Booking successful!",
                "booking": {
                    "id": booking.id,
                    "name": booking.name,
                    "email": booking.email,
                    "mobile": booking.mobile,
                    "zoom_link": zoom_link,
                    "start_time": booking.time_slot.start_time.astimezone(IST).strftime("%I:%M %p"),
                    "end_time": booking.time_slot.end_time.astimezone(IST).strftime("%I:%M %p"),
                    "session_type": booking.time_slot.session_type
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
