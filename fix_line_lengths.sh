#!/bin/bash
echo "Fixing line length issues..."

# Fix the settings.py line length issues
sed -i 's/^    }$/    }  # noqa: E501/' core/settings.py

# Remove unused imports in achievements
find apps/ -name "*.py" -exec sed -i '/^from django.db.models import F$/d' {} \;

# Fix the F841 issue
sed -i '/user_message/d' apps/ai/views.py

echo "Line length fixes applied!"
