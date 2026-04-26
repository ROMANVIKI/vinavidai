# vinavidai-backend

NearCart hyperlocal product discovery platform — Django backend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 5 + Django REST Framework |
| Database | PostgreSQL 16 + PostGIS (geospatial) |
| Cache | Redis 7 |
| Task Queue | Celery |
| Storage | Cloudflare R2 via django-storages + boto3 |
| Auth | JWT via djangorestframework-simplejwt |
| Server | Gunicorn (production) / Django runserver (dev) |
| Container | Docker + Docker Compose |
| Package Manager | uv |

---

## Packages

### Core Django

| Package | Purpose |
|---|---|
| `django` | Web framework |
| `djangorestframework` | REST API layer |
| `djangorestframework-simplejwt` | JWT authentication (access + refresh tokens) |
| `django-environ` | Load environment variables from `.env` file |
| `django-cors-headers` | CORS headers for frontend ↔ backend requests |
| `django-filter` | Filter querysets in DRF views (search filters) |

### Database

| Package | Purpose |
|---|---|
| `psycopg2-binary` | PostgreSQL driver for Django |

### Cache & Task Queue

| Package | Purpose |
|---|---|
| `redis` | Redis Python client |
| `django-redis` | Django cache backend for Redis |
| `celery` | Async task queue — CSV imports, email alerts, analytics logging |

### File Storage

| Package | Purpose |
|---|---|
| `django-storages` | Django storage backend — routes file uploads to R2/S3 instead of local disk |
| `boto3` | AWS/Cloudflare R2 SDK — handles actual file transfer (used internally by django-storages) |
| `pillow` | Image processing — validation, resizing before upload |

### Production

| Package | Purpose |
|---|---|
| `gunicorn` | WSGI server for running Django in production |

### Dev & Testing

| Package | Purpose |
|---|---|
| `ruff` | Linter + formatter (replaces flake8, black, isort) |
| `pytest` | Test runner |
| `pytest-django` | Django plugin for pytest |
| `factory-boy` | Model factories for generating test data |
| `ipython` | Enhanced Django shell (`manage.py shell`) |

---

## Prerequisites

Make sure these are installed on your machine before starting:

- Docker
- Docker Compose
- uv (Python package manager)
- Git

---

## Project Structure

```
vinavidai-backend/
├── apps/
│   ├── accounts/        # CustomUser, StaffMembership, JWT auth
│   ├── shops/           # Shop, ShopCategory, ShopImage
│   ├── inventory/       # Product, Variant, LocationNode, StockMovement
│   ├── search/          # Geo-search, autocomplete, compare endpoints
│   ├── analytics/       # SearchEvent, DirectionClick, impressions
│   └── notifications/   # Wishlist, PriceAlert, RecentlySeen
├── config/
│   ├── settings/
│   │   ├── base.py      # shared settings
│   │   ├── local.py     # dev overrides
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── .env                 # environment variables (never commit this)
├── .env.example         # template for env vars
├── Dockerfile
├── manage.py
├── pyproject.toml
└── uv.lock
```

---

## Setup & Installation

### 1. Clone the repo

```bash
git clone https://github.com/your-org/vinavidai-backend.git
cd vinavidai-backend
```

### 2. Create your `.env` file

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DATABASE_URL=postgis://nearcart:yourpassword@db:5432/nearcart
REDIS_URL=redis://redis:6379/0

# Leave these empty for local dev — only needed for production
R2_ACCESS_KEY_ID=
R2_SECRET_ACCESS_KEY=
R2_BUCKET_NAME=
R2_ENDPOINT_URL=
```

### 3. Start Docker daemon (Arch Linux)

```bash
sudo systemctl start docker

# To start Docker automatically on every boot
sudo systemctl enable docker

# Add yourself to docker group (run once, then log out and back in)
sudo usermod -aG docker $USER
newgrp docker
```

### 4. Build and start all services

```bash
docker compose up --build
```

This starts three containers:

- `nearcart_db` — PostgreSQL 16 + PostGIS
- `nearcart_redis` — Redis 7
- `nearcart_backend` — Django dev server on port 8000

---

## Running Migrations

Open a new terminal while services are running:

```bash
# Make migrations for each app in dependency order
docker compose exec backend uv run python manage.py makemigrations accounts
docker compose exec backend uv run python manage.py makemigrations shops
docker compose exec backend uv run python manage.py makemigrations inventory
docker compose exec backend uv run python manage.py makemigrations analytics
docker compose exec backend uv run python manage.py makemigrations notifications

# Apply all migrations to the database
docker compose exec backend uv run python manage.py migrate
```

---

## Create Superuser

```bash
docker compose exec backend uv run python manage.py createsuperuser
```

You will be prompted for:

```
Email: admin@nearcart.com
Full name: Admin
Password:
Password (again):
Superuser created successfully.
```

---

## Verify Setup

```bash
# Check Django config — should print 0 issues
docker compose exec backend uv run python manage.py check

# Open Django admin in browser
http://localhost:8000/admin
```

Login with your superuser credentials. If the admin panel loads, everything is working correctly.

---

## Daily Development Commands

```bash
# Start all services
docker compose up

# Start in background
docker compose up -d

# Stop all services
docker compose down

# Rebuild after Dockerfile or pyproject.toml changes
docker compose up --build

# View backend logs
docker compose logs -f backend

# View database logs
docker compose logs -f db

# Open a shell inside the backend container
docker compose exec backend bash

# Django shell (interactive Python with Django loaded)
docker compose exec backend uv run python manage.py shell

# Run any manage.py command
docker compose exec backend uv run python manage.py <command>

# Run tests
docker compose exec backend uv run pytest

# Lint and format code
docker compose exec backend uv run ruff check .
docker compose exec backend uv run ruff format .

# Wipe the database and start fresh (careful — deletes all data)
docker compose down -v
docker compose up --build
```

---

## Adding New Packages

```bash
# Add a production dependency
uv add <package-name>

# Add a dev-only dependency
uv add --dev <package-name>

# After adding packages, rebuild Docker to apply
docker compose up --build
```

Always commit both `pyproject.toml` and `uv.lock` after adding packages.

---

## Environment Variables Reference

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | Django secret key — generate a strong random string for production |
| `DEBUG` | Yes | `True` for local dev, `False` for production |
| `ALLOWED_HOSTS` | Yes | Comma-separated list of allowed hostnames |
| `DATABASE_URL` | Yes | PostgreSQL connection string — must use `postgis://` scheme |
| `REDIS_URL` | Yes | Redis connection string |
| `R2_ACCESS_KEY_ID` | Production | Cloudflare R2 access key |
| `R2_SECRET_ACCESS_KEY` | Production | Cloudflare R2 secret key |
| `R2_BUCKET_NAME` | Production | R2 bucket name |
| `R2_ENDPOINT_URL` | Production | R2 endpoint URL |

---

## Common Errors & Fixes

**Docker daemon not running**

```bash
sudo systemctl start docker
```

**Cannot connect to database**

```
Wait 10 seconds for the db container to finish starting, then retry.
```

**`No module named 'apps.accounts'`**

```bash
docker compose exec backend bash -c "touch apps/__init__.py"
```

**`AUTH_USER_MODEL refers to model that has not been installed`**

```
Make sure apps.accounts is in INSTALLED_APPS in config/settings/base.py
```

**`postgis` extension not found**

```bash
docker compose exec db psql -U nearcart -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

---

## API Base URL

```
http://localhost:8000/api/v1/
```

Django Admin:

```
http://localhost:8000/admin/
```

---

## Notes

- Never commit your `.env` file — it is in `.gitignore`
- Always use `postgis://` (not `postgresql://`) in `DATABASE_URL` — GeoDjango requires it
- File uploads go to local `media/` folder in dev and Cloudflare R2 in production
