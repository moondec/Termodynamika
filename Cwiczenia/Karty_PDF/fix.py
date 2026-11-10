import re

with open('Karta_Projektowa_Szablon.qmd', 'r') as f:
    content = f.read()

def fix_sprintf(match):
    s = match.group(0)
    commands = [
        'textcolor', 'frac', 'cdot', 'text', 'circ', 'rho', 'implies', 
        'Delta', 'dot', 'sqrt', 'ln', 'left', 'right', 'pi', 'eta', 'psi', '%%'
    ]
    for cmd in commands:
        # replace any number of backslashes before cmd with exactly 2 backslashes
        # For '%%', we want '\\%%'
        s = re.sub(r'\\+' + cmd, r'\\\\' + cmd, s)
    return s

# Find all sprintf("...")
new_content = re.sub(r'sprintf\(".*?"\)', fix_sprintf, content, flags=re.DOTALL)

with open('Karta_Projektowa_Szablon.qmd', 'w') as f:
    f.write(new_content)

print("Fixed LaTeX commands in sprintf.")
