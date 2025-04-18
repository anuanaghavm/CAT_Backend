from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta, datetime
from django.db.models import Count, F
from pytz import timezone as pytz_timezone
from django.utils.timezone import make_aware
from .zoom_utils import get_zoom_access_token, create_zoom_meeting
from .email_utils import send_welcome_email
from .models import TimeSlot, Booking
from .serializers import TimeSlotSerializer, BookingSerializer
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import ListAPIView


IST = pytz_timezone("Asia/Kolkata")
class CreateTimeSlotView(APIView):
    def post(self, request):
        session_type = request.data.get("session_type")
        start_time_str = request.data.get("start_time")
        end_time_str = request.data.get("end_time")
        max_capacity = request.data.get("max_capacity")
        date_str = request.data.get("date")
        course_name = request.data.get("course_name")  # ✅ Required
        time_duration = request.data.get("time_duration")  # ✅ Required

        # 🔍 Check for missing fields
        missing_fields = []
        for field_name, value in {
            "session_type": session_type,
            "start_time": start_time_str,
            "end_time": end_time_str,
            "max_capacity": max_capacity,
            "date": date_str,
            "course_name": course_name,
            "time_duration": time_duration
        }.items():
            if not value:
                missing_fields.append(field_name)

        if missing_fields:
            return Response(
                {"error": f"Missing required field(s): {', '.join(missing_fields)}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_dt = datetime.strptime(f"{slot_date} {start_time_str}", "%Y-%m-%d %I:%M %p")
            end_dt = datetime.strptime(f"{slot_date} {end_time_str}", "%Y-%m-%d %I:%M %p")

            if end_dt <= start_dt:
                end_dt += timedelta(days=1)

            start_dt = IST.localize(start_dt)
            end_dt = IST.localize(end_dt)

            time_duration = int(time_duration)
            max_capacity = int(max_capacity)

            slots = []
            current_time = start_dt
            while current_time < end_dt:
                next_time = current_time + timedelta(minutes=time_duration)

                if next_time > end_dt:
                    break

                slot = TimeSlot.objects.create(
                    session_type=session_type,
                    start_time=current_time,
                    end_time=next_time,
                    max_capacity=max_capacity,
                    date=slot_date,
                    course_name=course_name,
                    time_duration=time_duration
                )

                access_token = get_zoom_access_token()
                meeting = create_zoom_meeting(
                    access_token,
                    topic=f"{course_name} - {session_type}",
                    start_time=slot.start_time
                )
                slot.zoom_link = meeting.get("join_url")
                slot.save()

                slots.append(slot)
                current_time = next_time

            return Response({
                "message": f"{time_duration}-minute slots created successfully.",
                "slots": TimeSlotSerializer(slots, many=True).data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
            # ✅ Only check for slot capacity now
            if time_slot.bookings.count() >= time_slot.max_capacity:
                return Response({"error": "This time slot is already full."}, status=400)

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

            booking = serializer.save()
            send_welcome_email(booking)  # ✅ Send email here

            start = booking.time_slot.start_time.astimezone(IST).strftime("%I:%M %p")
            end = booking.time_slot.end_time.astimezone(IST).strftime("%I:%M %p")

            return Response({
                "message": "Booking successful!",
                "booking": {
                    **serializer.data,
                    "start_time": start,
                    "end_time": end,
                    "date": booking.time_slot.date.strftime("%Y-%m-%d"),

                    "zoom_link": booking.time_slot.zoom_link
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SessionBasedSlotView(APIView):
    def get(self, request):
        session_type = request.query_params.get("session_type")

        if session_type not in ["one_to_one", "group", None]:
            return Response({"error": "Invalid session_type. Choose 'one_to_one', 'group', or leave empty."}, status=400)

        # Base queryset
        slots = TimeSlot.objects.filter(start_time__gt=timezone.now())

        # Filter by session_type if specified
        if session_type:
            slots = slots.filter(session_type=session_type)

        # Annotate with booked count and filter available
        available_slots = slots.annotate(
            booked_count=Count("bookings")
        ).filter(
            booked_count__lt=F("max_capacity")
        ).order_by("start_time")

        result = {}
        for slot in available_slots:
            slot_type = slot.session_type
            if slot_type not in result:
                result[slot_type] = []

            result[slot_type].append({
                "id": slot.id,
                "start_time": slot.start_time.astimezone(IST).strftime("%I:%M %p"),
                "end_time": slot.end_time.astimezone(IST).strftime("%I:%M %p"),
                "remaining": slot.max_capacity - slot.bookings.count()
            })

        return Response({
            "message": "Filtered session slots fetched.",
            "slots": result
        }, status=200)
class CreatedSlotsListView(APIView):
    def get(self, request):
        slots = TimeSlot.objects.all().order_by("start_time")  # You can change to '-start_time' if needed

        serializer = TimeSlotSerializer(slots, many=True)
        return Response({
            "message": "List of all created slots.",
            "slots": serializer.data
        }, status=status.HTTP_200_OK)
class TimeSlotDetailView(RetrieveUpdateDestroyAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    lookup_field = 'id'
class BookingDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    lookup_field = 'id'


class BookingListView(ListAPIView):
    queryset = Booking.objects.all().order_by('-created_at')  # Optional: order by latest bookings
    serializer_class = BookingSerializer
class BookingDetailView(APIView):
    def get(self, request):
        bookings = Booking.objects.all().order_by("created_at")
        serializer = BookingSerializer(bookings, many=True)
        return Response({
            "message": "List of all bookings with time slot details.",
            "bookings": serializer.data
        }, status=status.HTTP_200_OK)