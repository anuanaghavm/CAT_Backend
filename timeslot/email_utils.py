from django.core.mail import EmailMessage
from django.conf import settings
from pytz import timezone as pytz_timezone
from datetime import datetime

IST = pytz_timezone("Asia/Kolkata")

def send_welcome_email(booking):
    subject = f"Welcome to Your {booking.session_type.title()} Session"
    start = booking.time_slot.start_time.astimezone(IST)
    end = booking.time_slot.end_time.astimezone(IST)

    zoom_link = booking.time_slot.zoom_link
    name = booking.name or "Participant"

    # Email body
    message = f"""
Hi {name},

Thank you for booking a {booking.session_type} session!

📅 Date: {start.strftime('%A, %d %B %Y')}
⏰ Time: {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}
🔗 Zoom Link: {zoom_link}

This invite includes a calendar event you can save.

Best regards,
The Team
"""

    # iCalendar (.ics) content
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//PixelBoho//Session Booking//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
DTSTART:{start.strftime('%Y%m%dT%H%M%S')}
DTEND:{end.strftime('%Y%m%dT%H%M%S')}
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%S')}
ORGANIZER;CN=PixelBoho:mailto:{settings.DEFAULT_FROM_EMAIL}
UID:{booking.id}@pixelboho.in
SUMMARY:{booking.session_type.title()} Zoom Session
DESCRIPTION:Join Zoom Meeting: {zoom_link}
LOCATION:Zoom
SEQUENCE:0
STATUS:CONFIRMED
BEGIN:VALARM
TRIGGER:-PT10M
DESCRIPTION:Reminder
ACTION:DISPLAY
END:VALARM
END:VEVENT
END:VCALENDAR
"""

    # Send email with .ics calendar invite attached
    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.email],
    )

    email.attach('invite.ics', ics_content, 'text/calendar')
    email.send()
