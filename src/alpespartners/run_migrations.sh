#!/bin/bash

echo "🚀 Running database migrations for Saga Pattern..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "alpespartners_db_1.*Up"; then
    echo "🔧 Starting database container..."
    docker-compose up -d db
    sleep 5
fi

# Run migrations inside the app container
echo "📊 Running Alembic migrations..."
docker-compose run --rm app bash -c "cd /app && python -m alembic upgrade head"

if [ $? -eq 0 ]; then
    echo "✅ Migrations completed successfully!"
    echo "📋 Saga tables created:"
    echo "   - sagas"
    echo "   - pasos_saga" 
    echo "   - compensaciones_saga"
    echo "   - saga_logs"
else
    echo "❌ Migration failed. Check the error messages above."
    exit 1
fi

echo "🎯 Ready to test the Saga Pattern!"
echo "💡 Run: python test_saga_simple.py"
