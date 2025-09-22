#!/bin/bash

echo "🚀 Starting Alpes Partners with Saga Pattern locally..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start only database and Pulsar
echo "🔧 Starting database and Pulsar..."
docker-compose up -d db pulsar pulsar-setup

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 15

# Run migrations
echo "📊 Running database migrations..."
docker-compose run --rm app bash -c "cd /app && alembic upgrade head"

# Start the application locally
echo "🎯 Starting application locally..."
cd alpespartners
python -m main
