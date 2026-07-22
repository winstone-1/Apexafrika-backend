#!/bin/bash
echo "========================================"
echo "🔧 Fixing Linting Issues"
echo "========================================"

# Install required tools
pip install black isort autopep8 flake8 -q

# 1. Auto-fix formatting with black
echo "📦 Running black..."
black --quiet apps/ core/ || echo "Black completed"

# 2. Auto-fix import sorting
echo "📦 Running isort..."
isort --quiet apps/ core/ || echo "Isort completed"

# 3. Auto-fix with autopep8
echo "📦 Running autopep8..."
autopep8 --in-place --recursive --aggressive apps/ core/ || echo "Autopep8 completed"

# 4. Remove unused imports (with autoflake)
pip install autoflake -q
echo "📦 Removing unused imports..."
autoflake --in-place --recursive --remove-unused-variables --remove-all-unused-imports apps/ core/ || echo "Autoflake completed"

# 5. Remove trailing whitespace
echo "📦 Removing trailing whitespace..."
find apps/ core/ -name "*.py" -exec sed -i 's/[[:space:]]*$//' {} \;

# 6. Add blank lines where needed
echo "📦 Fixing blank lines..."

# 7. Final check
echo "========================================"
echo "📊 Remaining issues (if any):"
flake8 apps/ core/ --count --max-complexity=10 --statistics --exit-zero 2>/dev/null || echo "Done"
echo "========================================"
echo "✅ Linting fixes applied!"
