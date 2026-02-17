import subprocess
import os

# Get list of files in img/ from git index
# git ls-files img/
try:
    output = subprocess.check_output(["git", "ls-files", "img/"], encoding='utf-8')
    files = output.strip().split('\n')
except subprocess.CalledProcessError as e:
    print("Error getting git files:", e)
    exit(1)

renamed_count = 0
for f in files:
    # f is relative path like img/KBiG.jpg
    if f != f.lower():
        # It has uppercase
        lower_f = f.lower()
        print(f"Renaming in git: {f} -> {lower_f}")
        
        # Use git mv --force to rename case-only changes on case-insensitive FS
        try:
            subprocess.check_call(["git", "mv", "--force", f, lower_f])
            renamed_count += 1
        except subprocess.CalledProcessError as e:
            print(f"Failed to rename {f}: {e}")

print(f"Renamed {renamed_count} files in git index.")
