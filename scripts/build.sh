#!/bin/bash
# ============================================
# APEXAFRIKA - Build Script
# ============================================

set -e

echo "🔨 Building ApexAfrika Docker images..."

# Build production image
docker-compose -f docker-compose.yml build

echo "✅ Build complete!"
echo ""
echo "To start in development mode:"
echo "  docker-compose up"
echo ""
echo "To start in production mode:"
echo "  docker-compose -f docker-compose.prod.yml up -d"
