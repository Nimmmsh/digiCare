# Patient Management System

A minimal, beginner-friendly patient management system built with Flask and MySQL.

## Features

- **Role-based access control** with three user types:
  - **Admin**: View all users and all patients
  - **Doctor**: View and edit only assigned patients
  - **Patient**: View only their own health information

- **Simple architecture**:
  - Python/Flask backend
  - Plain HTML templates (Jinja2)
  - MySQL database
  - Session-based authentication

## Project Structure

```
patientManagmentSystem/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── auth.py              # Simple auth decorators
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # All routes in one file
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html
│       ├── login.html
│       ├── admin_dashboard.html
│       ├── doctor_dashboard.html
│       ├── patient_dashboard.html
│       ├── patient_view.html
│       └── patient_edit.html
├── migrations/
│   └── init.sql             # Database schema (reference only)
├── Containerfile            # Podman/Docker build file
├── podman-compose.yml       # Container orchestration
├── pyproject.toml           # Poetry dependencies
├── run.py                   # Flask entry point
├── seed_db.py               # Database seeding script
└── README.md
```

## Quick Start with Podman

### Prerequisites

- [Podman](https://podman.io/) installed
- [podman-compose](https://github.com/containers/podman-compose) installed

### 1. Start the containers

```bash
# Navigate to project directory
cd patientManagmentSystem

# Start MySQL and Flask containers
podman-compose up -d

# Wait for containers to be ready (about 30 seconds for MySQL)
podman-compose logs -f
```

### 2. Seed the database

Once the containers are running:

```bash
# Run the seed script inside the Flask container
podman exec -it patient_flask python seed_db.py
```

### 3. Access the application

Open http://localhost:5000 in your browser.

### Demo Credentials

| Role    | Username    | Password    |
|---------|-------------|-------------|
| Admin   | admin       | admin123    |
| Doctor  | dr_smith    | doctor123   |
| Doctor  | dr_jones    | doctor123   |
| Patient | john_doe    | patient123  |
| Patient | jane_wilson | patient123  |
| Patient | bob_brown   | patient123  |

### Stop the containers

```bash
podman-compose down
```

To also remove the database volume (reset all data):

```bash
podman-compose down -v
```

## Local Development (without containers)

### Prerequisites

- Python 3.11+
- [Poetry](https://python-poetry.org/) installed
- MySQL 8 running locally

### 1. Install dependencies

```bash
poetry install
```

### 2. Set environment variables

```bash
export SECRET_KEY="your-secret-key"
export DATABASE_URL="mysql+pymysql://user:password@localhost:3306/patient_db"
```

Or create a `.env` file (see `.env.example`).

### 3. Create the database

```bash
mysql -u root -p -e "CREATE DATABASE patient_db;"
mysql -u root -p -e "CREATE USER 'patient_user'@'localhost' IDENTIFIED BY 'patient_pass';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON patient_db.* TO 'patient_user'@'localhost';"
```

### 4. Seed the database

```bash
poetry run python seed_db.py
```

### 5. Run the application

```bash
poetry run python run.py
```

Visit http://localhost:5000

## Database Schema

```
┌─────────────┐     ┌─────────────┐
│   roles     │     │    users    │
├─────────────┤     ├─────────────┤
│ id          │◄────│ role_id     │
│ name        │     │ id          │
└─────────────┘     │ username    │
                    │ password    │
                    │ full_name   │
                    │ email       │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
│ patient_details │ │doctor_patient│ │doctor_patient│
├─────────────────┤ ├─────────────┤ ├─────────────┤
│ user_id (FK)    │ │ doctor_id   │ │ patient_id  │
│ date_of_birth   │ │ patient_id  │ │ (many-to-many)│
│ medical_notes   │ └─────────────┘ └─────────────┘
│ phone           │
└─────────────────┘
```

## Design Decisions

1. **Single User table**: All users (admin, doctor, patient) are in one table. Roles determine access. This simplifies auth and is easier to extend.

2. **Session-based auth**: We use Flask's built-in session for authentication. No JWT, no OAuth—just simple cookie-based sessions.

3. **No frontend framework**: Plain HTML with Jinja2 templates. Easy to understand, no build step, works everywhere.

4. **One routes file**: For a small app, having all routes in one file is easier to navigate than scattered across multiple files.

5. **Podman over Docker**: Same functionality, but rootless by default. All Docker commands work with Podman.

## Security Notes

⚠️ This is a demo application. For production:

- Change `SECRET_KEY` to a random string
- Use HTTPS
- Use stronger passwords
- Add rate limiting
- Add CSRF protection
- Store secrets in environment variables or a secrets manager
- Use a production WSGI server (gunicorn, uwsgi)

## License

MIT

