from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Booking, Seat

@receiver(post_save, sender=Booking)
def mark_seat_booked(sender, instance, created, **kwargs):
    if created:
        seat = instance.seat
        seat.is_booked = True
        seat.save()

@receiver(post_delete, sender=Booking)
def release_seat_if_no_other_bookings(sender, instance, **kwargs):
    seat = instance.seat

    # Check if ANY booking still exists for this seat
    if not Booking.objects.filter(seat=seat).exists():
        seat.is_booked = False
        seat.save()
