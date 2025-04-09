from django.core.mail import send_mail
from django.conf import settings
from pytz import timezone as pytz_timezone


IST = pytz_timezone("Asia/Kolkata")

def send_welcome_email(booking):
    subject = f"Welcome to Your {booking.session_type.title()} Session"
    start = booking.time_slot.start_time.astimezone(IST).strftime("%I:%M %p")
    end = booking.time_slot.end_time.astimezone(IST).strftime("%I:%M %p")

    message = f"""
Hi {booking.name},

Thank you for booking a {booking.session_type} session!

📅 Date: {booking.time_slot.start_time.astimezone(IST).strftime("%A, %d %B %Y")}
⏰ Time: {start} - {end}
🔗 Zoom Link: {booking.time_slot.zoom_link}

We look forward to seeing you!

Best regards,
The Team
    """

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.email],
        fail_silently=False,
    )
