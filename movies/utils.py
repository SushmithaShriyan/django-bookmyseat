from django.utils import timezone
from datetime import timedelta
from .models import Seat


def release_expired_seats():
    expiry_time = timezone.now() - timedelta(minutes=5)

    expired_seats = Seat.objects.filter(
        is_reserved=True,
        reserved_at__lt=expiry_time
    )

    for seat in expired_seats:
        seat.is_reserved = False
        seat.reserved_at = None
        seat.reserved_by = None
        seat.save()
