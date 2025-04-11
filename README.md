# Healthcare Appointment Scheduler

A comprehensive healthcare appointment scheduling system designed to streamline patient-doctor interactions, manage medical records, and optimize healthcare facility operations.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Testing](#testing)
- [Documentation](#documentation)
- [Contributing](#contributing)

## Overview

The Healthcare Appointment Scheduler is a robust backend service that provides a comprehensive solution for managing healthcare appointments, patient records, and doctor schedules. The system is built with scalability, security, and maintainability in mind, following industry best practices and standards.

## Features

### Core Functionality
- User Management: Secure authentication and role-based access control
- Appointment Management: Scheduling, rescheduling, cancellation, recurring appointments
- Medical Records: Secure storage and management of patient records
- Doctor-Patient Management: Assignment and relationship tracking
- Staff Management: Department and role management
- Audit and Security: Comprehensive logging and security measures

### Future Enhancements
- Web-based Dashboard: Intuitive user interface for all stakeholders
- Advanced Appointment Features: Waitlist management
- Department Management: Specialized department handling
- Analytics and Reporting: Data-driven insights and reporting
- Integration Capabilities: EHR and payment system integration
- Advanced Security: Two-factor authentication

## Technology Stack

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- JWT Authentication
- Alembic (Database Migrations)

### Frontend (Future Implementation)
- React.js
- TypeScript
- Material-UI
- Redux Toolkit
- React Query

### DevOps
- Docker
- Docker Compose
- GitHub Actions
- PostgreSQL
- Redis

## Prerequisites

- Python 3.11 or higher
- PostgreSQL 15 or higher
- Docker and Docker Compose (for containerized deployment)
- Git
- psql (PostgreSQL command-line tool)
- make (optional, for using Makefile commands)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/healthcare-appointment-scheduler.git
cd healthcare-appointment-scheduler
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/macOS
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

The application uses environment variables for configuration. Key settings include:

- Database configuration
- JWT settings
- CORS settings
- Email settings (for notifications)
- Redis settings (for caching)

Refer to `.env.example` for all available configuration options.

## Database Setup

The application uses PostgreSQL as its database. You can set up the database in two ways:

### Using Docker (Recommended)

1. Start the PostgreSQL container:
```bash
docker-compose up -d db
```

2. Wait for the database to be ready (about 10-15 seconds)

3. To recreate the database schema from scratch, run:
```bash
python -m app.db.init_db
```

### Manual Setup

1. Create a PostgreSQL database:
```bash
createdb appointment_scheduler
```

2. Connect to the database:
```bash
psql appointment_scheduler
```

3. To recreate the database schema from scratch, run:
```bash
python -m app.db.init_db
```

### Database Reset

If you need to reset the database to a clean state:

1. Using Docker:
```bash
docker-compose down -v
docker-compose up -d db
python -m app.db.init_db
```

2. Manual setup:
```bash
dropdb appointment_scheduler
createdb appointment_scheduler
python -m app.db.init_db
```

### Database Migrations

The application uses Alembic for database migrations. To manage migrations:

1. Create a new migration:
```bash
alembic revision --autogenerate -m "description of changes"
```

2. Apply migrations:
```bash
alembic upgrade head
```

3. Rollback migrations:
```bash
alembic downgrade -1
```

## Running the Application

### Development Mode
```bash
# Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Linux/macOS
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
docker-compose up -d
```

## Testing

The project includes comprehensive test suites:

- Unit tests for models and services
- Integration tests for API endpoints
- Database tests
- Security tests

Run tests using:
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_models.py

# Run tests with detailed output
pytest -v
```

## Documentation

### API Documentation
The API documentation is available at `/docs` when running the application. It provides:
- Interactive API documentation (Swagger UI)
- OpenAPI specification
- Example requests and responses

### System Documentation
Comprehensive system documentation is available in the `docs` directory:
- [System Architecture](docs/FINAL_DOCUMENTATION.md)
- [Database Schema](docs/database_schema.sql)
- [API Endpoints](docs/api_endpoints.md)
- [Deployment Guide](docs/deployment.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

Please ensure your code follows the project's coding standards and includes appropriate tests.

