BookMySeat – Movie Ticket Booking System

BookMySeat is a Django-based movie ticket booking application where users can browse movies, select theaters and seats, make payments using Stripe, and receive booking confirmation emails.

##  Features

- User authentication (login/logout)
- Admin panel for managing movies, theaters, shows, and seats
- Seat selection & booking
- Stripe payment integration
- Email confirmation after successful booking
- Admin dashboard for quick overview

##  Important URLs
### Home Page
http://127.0.0.1:8000/

### Django Admin Panel
http://127.0.0.1:8000/admin/

### Admin Dashboard
http://127.0.0.1:8000/movies/admin-dashboard/ Create Superuser (Admin Access)

### Run the following commands:
venv\Scripts\activate
python manage.py migrate
python manage.py createsuperuser

### After creation, log in at:
http://127.0.0.1:8000/admin/

### Run the Project Locally
venv\Scripts\activate
python manage.py runserver

## Stripe Test Card Details
Card Number: 4242 4242 4242 4242
Expiry Date: Any future date (MM/YY)
CVV: Any 3 digits

