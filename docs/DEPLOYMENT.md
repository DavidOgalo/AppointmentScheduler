# Healthcare Appointment Scheduler - Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [Application Deployment](#application-deployment)
5. [Monitoring and Maintenance](#monitoring-and-maintenance)
6. [Troubleshooting](#troubleshooting)
7. [Security Considerations](#security-considerations)

## Prerequisites

### System Requirements
- Linux/Windows Server 2019 or later
- Docker and Docker Compose
- PostgreSQL 13 or later
- Python 3.8 or later
- Node.js 14 or later (for frontend)
- Nginx or Apache (for production)

### Required Software
- Git
- Docker Engine
- Docker Compose
- Python virtual environment
- Node.js and npm
- PostgreSQL client tools

## Environment Setup

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/appointment-scheduler.git
cd appointment-scheduler
```

### 2. Environment Variables
Create a `.env` file in the root directory with the following variables:
```env
# Application
APP_NAME=Healthcare Appointment Scheduler
APP_ENV=production
DEBUG=false
SECRET_KEY=your-secret-key
API_V1_STR=/api/v1

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_DB=appointment_scheduler
SQLALCHEMY_DATABASE_URI=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}/${POSTGRES_DB}

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password

# RabbitMQ
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=admin
RABBITMQ_PASSWORD=your-rabbitmq-password
RABBITMQ_VHOST=/

# Email
SMTP_TLS=true
SMTP_PORT=587
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-email-password
EMAILS_FROM_EMAIL=your-email@gmail.com
EMAILS_FROM_NAME=Healthcare Appointment Scheduler

# CORS
BACKEND_CORS_ORIGINS=["http://localhost:3000","https://your-domain.com"]
```

### 3. Docker Setup
```bash
# Build the Docker images
docker-compose build

# Start the services
docker-compose up -d
```

## Database Setup

### 1. Initial Setup
```bash
# Create the database
docker-compose exec db psql -U postgres -c "CREATE DATABASE appointment_scheduler;"

# Run migrations
docker-compose exec app alembic upgrade head

# Initialize the database
docker-compose exec app python -m app.db.init_db
```

### 2. Database Backup
```bash
# Create a backup
docker-compose exec db pg_dump -U postgres appointment_scheduler > backup.sql

# Restore from backup
docker-compose exec -T db psql -U postgres appointment_scheduler < backup.sql
```

## Application Deployment

### 1. Backend Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. Frontend Deployment
```bash
# Install dependencies
cd frontend
npm install

# Build the application
npm run build

# Serve the built files
npm run start
```

### 3. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        root /path/to/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring and Maintenance

### 1. Logging
```bash
# View application logs
docker-compose logs -f app

# View database logs
docker-compose logs -f db

# View RabbitMQ logs
docker-compose logs -f rabbitmq
```

### 2. Health Checks
```bash
# Check application health
curl http://localhost:8000/health

# Check database health
docker-compose exec db pg_isready -U postgres

# Check RabbitMQ health
curl -u admin:password http://localhost:15672/api/health/checks/alarms
```

### 3. Performance Monitoring
```bash
# Monitor database performance
docker-compose exec db pg_stat_activity

# Monitor application performance
docker-compose exec app python -m app.core.monitoring
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check PostgreSQL service status
   - Verify connection string
   - Check firewall settings

2. **Application Startup Issues**
   - Check environment variables
   - Verify dependencies
   - Check log files

3. **RabbitMQ Connection Issues**
   - Check RabbitMQ service status
   - Verify credentials
   - Check network connectivity

### Debugging Tools
```bash
# Database debugging
docker-compose exec db psql -U postgres appointment_scheduler

# Application debugging
docker-compose exec app python -m pdb -m app.main

# RabbitMQ debugging
docker-compose exec rabbitmq rabbitmqctl status
```

## Security Considerations

### 1. SSL/TLS Configuration
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
}
```

### 2. Firewall Configuration
```bash
# Allow necessary ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5432/tcp
sudo ufw allow 5672/tcp
sudo ufw allow 15672/tcp
```

### 3. Regular Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Update Docker images
docker-compose pull

# Update application dependencies
pip install -r requirements.txt --upgrade
cd frontend && npm update
```

### 4. Backup Strategy
```bash
# Daily database backup
0 0 * * * docker-compose exec -T db pg_dump -U postgres appointment_scheduler > /backups/db-$(date +\%Y\%m\%d).sql

# Weekly full backup
0 0 * * 0 tar -czf /backups/full-$(date +\%Y\%m\%d).tar.gz /path/to/application
```

### 5. Security Monitoring
```bash
# Monitor failed login attempts
docker-compose exec app python -m app.core.security_monitoring

# Check for vulnerabilities
docker-compose exec app python -m app.core.vulnerability_scanning
``` 