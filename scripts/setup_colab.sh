#!/bin/bash

# MASUKA V2 - Colab Setup Script
# This script sets up the complete MASUKA V2 environment on Google Colab

set -e  # Exit on error

echo "========================================="
echo "MASUKA V2 - Colab Setup Script"
echo "========================================="

# Install system dependencies
echo "Installing system dependencies..."
apt-get update -qq
apt-get install -y -qq git postgresql postgresql-contrib redis-server > /dev/null 2>&1

# Start PostgreSQL
echo "Starting PostgreSQL..."
service postgresql start

# Create database and user
echo "Creating database and user..."
sudo -u postgres psql -c "DROP DATABASE IF EXISTS masuka;" > /dev/null 2>&1 || true
sudo -u postgres psql -c "CREATE DATABASE masuka;"
sudo -u postgres psql -c "CREATE USER masuka WITH PASSWORD 'password123';" > /dev/null 2>&1 || true
sudo -u postgres psql -c "ALTER USER masuka WITH PASSWORD 'password123';" > /dev/null 2>&1 || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE masuka TO masuka;"

# Start Redis
echo "Starting Redis..."
service redis-server start

# Clone SimpleTuner
echo "Setting up SimpleTuner..."
cd /content
if [ ! -d "SimpleTuner" ]; then
    echo "Cloning SimpleTuner repository..."
    git clone https://github.com/bghira/SimpleTuner.git
    cd SimpleTuner
    pip install -e . -q
else
    echo "SimpleTuner already exists, pulling latest changes..."
    cd SimpleTuner
    git pull
fi

# Clone MASUKA V2
echo "Setting up MASUKA V2..."
cd /content
if [ ! -d "masuka-v2" ]; then
    echo "Cloning MASUKA V2 repository..."
    git clone https://github.com/YOUR_USERNAME/masuka-v2.git
else
    echo "MASUKA V2 already exists, pulling latest changes..."
    cd masuka-v2
    git pull
fi

# Install Python dependencies
echo "Installing Python dependencies..."
cd /content/masuka-v2/backend
pip install -r requirements.txt -q

# Create required directories
echo "Creating working directories..."
mkdir -p /tmp/masuka/{training,generated,uploads,model_cache}

# Set environment variables
echo "Setting environment variables..."
export DATABASE_URL="postgresql://masuka:password123@localhost:5432/masuka"
export REDIS_URL="redis://localhost:6379/0"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
export SIMPLETUNER_PATH="/content/SimpleTuner"

# Run database migrations
echo "Running database migrations..."
cd /content/masuka-v2/backend
python -c "from app.models import Base, engine; Base.metadata.create_all(bind=engine)"

echo ""
echo "========================================="
echo "Setup complete!"
echo "========================================="
echo ""
echo "Database: PostgreSQL (localhost:5432)"
echo "Redis: localhost:6379"
echo "SimpleTuner: /content/SimpleTuner"
echo ""
echo "Next steps:"
echo "1. Set your AWS/S3 credentials in environment variables"
echo "2. Start Celery worker: celery -A app.tasks.celery_app worker --loglevel=info -Q training,generation"
echo "3. Start FastAPI: uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "========================================="
