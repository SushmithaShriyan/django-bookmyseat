from django.urls import path
from . import views

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("<int:movie_id>/theaters/", views.theater_list, name="theater_list"),
    path("theater/<int:theater_id>/seats/book/", views.book_seats, name="book_seats"),
    path("theater/<int:theater_id>/confirm/", views.confirm_booking, name="confirm_booking"),
    path("theater/<int:theater_id>/payment/", views.make_payment, name="make_payment"),
    path("theater/<int:theater_id>/success/", views.payment_success, name="payment_success"),
   
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),

    path("movie/<int:movie_id>/", views.movie_detail, name="movie_detail"),

      

]
