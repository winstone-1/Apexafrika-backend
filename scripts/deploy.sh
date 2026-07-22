#!/bin/bash
# ============================================
# APEXAFRIKA - Deploy Script
# ============================================

set -e

echo "🚀 Deploying ApexAfrika to production..."

# Pull latest code
git pull origin main

# Build and start containers
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

echo "✅ Deployment complete!"
echo ""
echo "Running containers:"
docker ps --filter "name=apexafrika"
