import re
import os

files_to_fix = [
    'apps/content/views.py',
    'apps/payments/views.py',
    'apps/tournaments/models.py',
]

for file_path in files_to_fix:
    if not os.path.exists(file_path):
        continue
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix line breaks before binary operators
    content = re.sub(r'\n\s+(and|or)\s+', r' \1 ', content)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Fixed: {file_path}")

print("Done!")
