# EventHub — Django Event Management System 🎟️

A full-featured event management platform built with Django 4.2+ featuring role-based dashboards, Stripe payments, QR code tickets, event creation/booking/check-in, and Crispy Bootstrap5 forms. Supports MySQL/PostgreSQL.

See **Event Management System.pdf** for detailed system design and requirements.

## 🚀 Quick Start

```bash
# 1. Enter project directory
cd event_management

# 2. Create & activate virtual environment
python -m venv venv
# Linux/Mac: source venv/bin/activate
# Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy & configure environment (create .env from .env.example if exists)
# Add DATABASE_URL, STRIPE_SECRET_KEY, etc.

# 5. Apply migrations
python manage.py migrate

# 6. Create superuser
python manage.py createsuperuser

# 7. Load sample data (optional)
python manage.py loaddata fixtures/sample_categories.json

# 8. Run server
python manage.py runserver
```

Visit: http://127.0.0.1:8000

**Admin login:** `/admin/`

## 📁 Project Structure

```
event_management/                    # Root
├── manage.py
├── requirements.txt
├── README.md
├── TODO.md                          # Task tracking
├── db.sqlite3                       # Dev DB
├── Procfile, runtime.txt            # Heroku deployment
├── fixtures/                        # Sample data
├── media/                           # User uploads (QR codes, posters)
├── static/                          # CSS/JS/images
├── event_management/                # Django settings
├── accounts/                        # Authentication & roles
├── events/                          # Event CRUD
├── tickets/                         # Ticket types
├── bookings/                        # Orders & QR generation
├── payments/                        # Stripe/Paystack
└── dashboard/                       # Role-based panels (cleaned: templates only)
    ├── templates/dashboard/         # All views
    └── views.py, forms.py, etc.
├── templates/                       # Base layouts & partials
```

*Recent cleanup: Removed duplicate HTML files from `dashboard/` (now only in `templates/`).*

## 🔐 User Roles & Features

| Role | Dashboard | Key Features |
|------|-----------|--------------|
| **Attendee** | `/dashboard/attendee/` | Browse/book events, view QR tickets |
| **Organizer** | `/dashboard/organizer/` | Create/manage events, attendee lists, QR check-in |
| **Admin** | `/dashboard/admin/` | Full control, user/event management |

**Core Flows:**
- Event discovery → Booking → Stripe payment → QR ticket
- Organizer: Event setup → Attendee check-in scanner

## 📱 Pages & URLs

**Public:**
- `/` - Home (featured events)
- `/events/` - List with filters
- `/events/<slug>/` - Details & book tickets

**Authenticated:**
- `/dashboard/...` - Role-specific
- `/checkout/` - Cart & payment
- `/booking/success/` - QR download

## 📸 Screenshots

*Add screenshots here: home page, dashboards, checkout flow*

## 🔧 Troubleshooting

- **Migrations fail:** `python manage.py makemigrations && migrate`
- **Static files 404:** `python manage.py collectstatic` (DEBUG=False)
- **Stripe errors:** Check `.env` keys
- **QR codes missing:** Ensure Pillow & qrcode installed
- **Templates not found:** Verify TEMPLATES.DIRS in settings.py

**Windows users:** Use `venv\Scripts\activate.bat`

## ☁️ Deployment

**Heroku:**
```bash
heroku create
heroku addons:create cleardb:ignite  # MySQL
git push heroku main
heroku run python manage.py migrate
```

**Production settings:** DEBUG=False, ALLOWED_HOSTS, S3 for media/static.

**Docker:** See `Dockerfile` (if added).

## 🤝 Contributing

1. Fork & clone
2. Create venv, install reqs
3. Branch: `git checkout -b feature/xyz`
4. PR to `main`

## 📄 Documentation

- [Event Management System.pdf](Event%20Management%20System.pdf) - Full specs
- `/admin/doc/` - Django docs (if enabled)

## 📦 Dependencies

See [requirements.txt](requirements.txt) for full list.
