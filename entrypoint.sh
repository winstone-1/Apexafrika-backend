#!/bin/bash
# ============================================
# APEXAFRIKA - Entrypoint Script
# ============================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 APEXAFRIKA - Starting Application${NC}"
echo -e "${GREEN}========================================${NC}"

# Wait for PostgreSQL to be ready
echo -e "${YELLOW}📦 Waiting for PostgreSQL...${NC}"
while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
    sleep 1
done
echo -e "${GREEN}✅ PostgreSQL is ready${NC}"

# Wait for Redis to be ready
echo -e "${YELLOW}📦 Waiting for Redis...${NC}"
while ! nc -z ${REDIS_HOST:-redis} ${REDIS_PORT:-6379}; do
    sleep 1
done
echo -e "${GREEN}✅ Redis is ready${NC}"

# Run migrations
echo -e "${YELLOW}📦 Running migrations...${NC}"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Create superuser if not exists (using environment variables)
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo -e "${YELLOW}👤 Creating superuser...${NC}"
    echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists() or User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')" | python manage.py shell
    echo -e "${GREEN}✅ Superuser created${NC}"
fi

# Start the appropriate server
if [ "$DJANGO_ENV" = "production" ]; then
    echo -e "${GREEN}🔥 Starting Gunicorn server...${NC}"
    exec gunicorn --bind 0.0.0.0:8000 \
        --workers ${GUNICORN_WORKERS:-4} \
        --threads ${GUNICORN_THREADS:-2} \
        --worker-class sync \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        --timeout 60 \
        --access-logfile - \
        --error-logfile - \
        core.wsgi:application
else
    echo -e "${GREEN}🔥 Starting Django development server...${NC}"
    exec python manage.py runserver 0.0.0.0:8000
fi
