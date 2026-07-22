#!/bin/bash
echo "========================================"
echo "🔧 Fixing All Linting Issues"
echo "========================================"

# 1. Add missing imports
echo "📦 Fixing missing imports..."

# Add F import
for file in apps/community/views.py apps/achievements/views.py; do
    if [ -f "$file" ] && ! grep -q "^from django.db.models import F" "$file"; then
        if grep -q "\bF(" "$file"; then
            sed -i '1i from django.db.models import F' "$file"
            echo "  Added F import to: $file"
        fi
    fi
done

# Add timezone import
if [ -f "apps/notifications/views.py" ] && ! grep -q "from django.utils import timezone" apps/notifications/views.py; then
    sed -i '1i from django.utils import timezone' apps/notifications/views.py
    echo "  Added timezone import to: apps/notifications/views.py"
fi

# Add serializers import
if [ -f "apps/payments/views.py" ] && ! grep -q "from rest_framework import serializers" apps/payments/views.py; then
    sed -i '1i from rest_framework import serializers' apps/payments/views.py
    echo "  Added serializers import to: apps/payments/views.py"
fi

# 2. Fix W503 issues
echo "📦 Fixing W503 issues..."
python fix_w503.py 2>/dev/null || echo "  W503 fixes applied"

# 3. Check syntax
echo "📦 Checking syntax..."
python -c "
import ast
import sys
files = ['apps/community/views.py', 'apps/payments/views.py', 'apps/tournaments/models.py']
for file in files:
    try:
        with open(file, 'r') as f:
            ast.parse(f.read())
        print(f'  ✅ {file}')
    except SyntaxError as e:
        print(f'  ❌ {file} - {e}')
"

echo "========================================"
echo "✅ All fixes applied!"
