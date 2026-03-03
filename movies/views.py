from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db.models import Count
from django.http import HttpResponse

import logging

from .models import Movie, Theater, Seat, Booking
from .utils import release_expired_seats

PRICE_PER_SEAT = 200
logger = logging.getLogger(__name__)


# ======================
# MOVIES
# ======================

def movie_list(request):
    movies = Movie.objects.all()

    if request.GET.get("search"):
        movies = movies.filter(name__icontains=request.GET["search"])
    if request.GET.get("genre"):
        movies = movies.filter(genre__iexact=request.GET["genre"])
    if request.GET.get("language"):
        movies = movies.filter(language__iexact=request.GET["language"])

    return render(request, "movies/movie_list.html", {"movies": movies})


def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    return render(request, "movies/movie_detail.html", {"movie": movie})


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)
    return render(request, "movies/theater_list.html", {
        "movie": movie,
        "theaters": theaters
    })


# ======================
# SEAT BOOKING
# ======================

@login_required
def book_seats(request, theater_id):
    release_expired_seats()
    theater = get_object_or_404(Theater, id=theater_id)

    if request.method == "POST":
        seat_ids = request.POST.getlist("seats")

        for seat in Seat.objects.filter(id__in=seat_ids, theater=theater):
            if not seat.is_booked and not seat.is_reserved:
                seat.is_reserved = True
                seat.reserved_by = request.user
                seat.reserved_at = timezone.now()
                seat.save()

        return redirect("confirm_booking", theater_id=theater.id)

    seats = Seat.objects.filter(theater=theater)
    return render(request, "movies/seat_selection.html", {
        "theater": theater,
        "seats": seats
    })


@login_required
def confirm_booking(request, theater_id):
    release_expired_seats()
    theater = get_object_or_404(Theater, id=theater_id)

    seats = Seat.objects.filter(
        theater=theater,
        is_reserved=True,
        reserved_by=request.user
    )

    if not seats.exists():
        return redirect("movie_list")

    total_amount = seats.count() * PRICE_PER_SEAT

    if request.method == "POST":
        return redirect("make_payment", theater_id=theater.id)

    return render(request, "movies/confirm_booking.html", {
        "theater": theater,
        "seats": seats,
        "total_amount": total_amount
    })


# ======================
# PAYMENT
# ======================

@login_required
def make_payment(request, theater_id):
    release_expired_seats()

    seats = Seat.objects.filter(
        theater_id=theater_id,
        is_reserved=True,
        reserved_by=request.user
    )

    if not seats.exists():
        return redirect("movie_list")

    return redirect("payment_success", theater_id=theater_id)


@login_required
def payment_success(request, theater_id):
    release_expired_seats()

    seats = Seat.objects.filter(
        theater_id=theater_id,
        is_reserved=True,
        reserved_by=request.user
    )

    if not seats.exists():
        return redirect("movie_list")

    seats = list(seats)
    first_seat = seats[0]
    movie = first_seat.theater.movie
    theater = first_seat.theater

    seat_numbers = []

    for seat in seats:
        Booking.objects.create(
            user=request.user,
            seat=seat,
            movie=movie,
            theater=theater,
            price=PRICE_PER_SEAT   # 🔥 FIX
        )

        seat.is_booked = True
        seat.is_reserved = False
        seat.reserved_by = None
        seat.reserved_at = None
        seat.save()

        seat_numbers.append(seat.seat_number)

    try:
        if request.user.email and settings.DEFAULT_FROM_EMAIL:
            send_mail(
                subject="🎟 Ticket Booking Confirmation",
                message=f"""Hi {request.user.username},

Your booking is confirmed!

Movie: {movie.name}
Theater: {theater.name}
Seats: {', '.join(seat_numbers)}
Total: ₹{len(seat_numbers) * PRICE_PER_SEAT}

Enjoy your show!

- BookMySeat Team
""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
    except Exception:
        pass

    return redirect("profile")


# ======================
# ADMIN DASHBOARD
# ======================

@staff_member_required
def admin_dashboard(request):
    context = {
        "total_bookings": Booking.objects.count(),
        "total_revenue": Booking.objects.aggregate(total=models.Sum("price"))["total"] or 0,
        "popular_movies": Movie.objects.annotate(
            bookings=Count("booking")
        ).order_by("-bookings")[:5],
        "busy_theaters": Theater.objects.annotate(
            bookings=Count("booking")
        ).order_by("-bookings")[:5],
    }
    return render(request, "movies/admin_dashboard.html", context)