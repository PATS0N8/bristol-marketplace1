# Bristol Marketplace
 
A local food marketplace connecting Bristol producers with customers, built with Django and Docker.
 
## Features
 
### Customers
- Browse products by category or search by name/description
- View product details including allergen info, harvest dates, best before dates, organic certification, and seasonal availability
- Add items to cart and checkout across multiple producers
- View order history and status timeline
- Account settings including delivery postcode
### Producers
- Register and manage a producer profile with business name, location, and farm story
- Add and manage products with full details (price, stock, unit, allergens, organic status, harvest/best before dates)
- View and fulfil incoming orders with status updates (Paid → Preparing → Dispatched → Delivered)
- View earnings breakdown with 5% commission and payout calculations
### Admin
- Dashboard with user, product, and order stats
- View settlement and commission reports across all producers
- Full access via Django admin panel
## Tech Stack
 
- Python 3.11 / Django 4.2
- PostgreSQL 15
- Docker & Docker Compose
## Run
 
```bash
docker compose up --build
```
 
## Open
 
http://127.0.0.1:8000
 
## Admin Panel
 
http://127.0.0.1:8000/django-admin/
 
To create a superuser:
 
```bash
docker compose exec web python manage.py createsuperuser
```
 
## Project Structure
 
```
bristol-marketplace/
├── accounts/       # User, ProducerProfile, CustomerProfile models
├── products/       # Product, Category models, all views and URLs
├── orders/         # Order, OrderItem, OrderStatusHistory models
├── config/         # Django settings, URLs, WSGI/ASGI
├── templates/      # All HTML templates
└── manage.py
```
 
## Notes
 
- Payment is currently a demo form — Stripe/PayPal sandbox integration is planned
- Products with zero stock are automatically hidden from the storefront
- 5% platform commission is calculated automatically on all orders
 