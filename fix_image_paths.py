import os
import re

# 1. Get all actual image filenames in img/ (should be lowercase now)
img_dir = "img"
actual_images = set(os.listdir(img_dir))
# Create a map of lowercased names to actual (which should be same, but good for safety)
img_map = {f.lower(): f for f in actual_images}

print(f"Found {len(actual_images)} images in {img_dir}/")

# 2. Define regex to find image paths
# Capture groups: 1=prefix (../ or empty), 2=filename
# Markdown: ![alt](path)
# HTML: <img src="path">
patterns = [
    re.compile(r'!\[.*?\]\(((\.\./)?img/)([^)]+)\)'),
    re.compile(r'<img[^>]+src=["\']((\.\./)?img/)([^"\']+市内)["\']')
]

# Simple text replacement might be safer to avoid breaking markup
# We will read file, find "img/Something.jpg", check if "something.jpg" exists, and replace.

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = content
    # Find all occurrences of img/Filename.ext or ../img/Filename.ext
    # We look for the pattern "img/" followed by non-whitespace/non-quote characters
    
    # Regex for path ending with typical image extensions
    # This captures the full relative path e.g. "../img/KBiG.jpg" or "img/Picture.PNG"
    matches = re.finditer(r'((\.\./)?img/)([\w.-]+)', content, re.IGNORECASE)
    
    replacements = 0
    for m in matches:
        full_match = m.group(0) # e.g. ../img/KBiG.jpg
        prefix = m.group(1)     # e.g. ../img/
        filename = m.group(3)   # e.g. KBiG.jpg
        
        filename_lower = filename.lower()
        
        if filename_lower in img_map:
            actual_name = img_map[filename_lower]
            if filename != actual_name:
                # Replace EXACT MATCH of this path
                # Be careful not to replace partial matches if not intended, but here we replace specific strings
                new_path = f"{prefix}{actual_name}"
                # We use simple string replace for safety, assuming paths are unique enough or we process sequentially
                # Actually, regex substitution is better on the content
                # But to avoid re-replacing, let's just do a pass.
                
                # Let's simple-replace this specific instance in the string? 
                # No, global replace of this specific incorrect string is safer
                if full_match != new_path:
                    new_content = new_content.replace(full_match, new_path)
                    print(f"  Fixed: {full_match} -> {new_path}")
                    replacements += 1
        else:
             print(f"  Warning: Referenced image not found in img/: {filename}")

    if replacements > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {filepath} ({replacements} fixes)")

# 3. Walk through directories
target_dirs = ["Wyklady", "Cwiczenia"]
for d in target_dirs:
    if os.path.exists(d):
        for root, _, files in os.walk(d):
            for file in files:
                if file.endswith(".qmd") or file.endswith(".md"):
                    fix_file(os.path.join(root, file))
