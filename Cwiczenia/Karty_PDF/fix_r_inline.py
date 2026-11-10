import re

with open('Karta_Projektowa_Szablon.qmd', 'r') as f:
    content = f.read()

def fix_r_inline(match):
    s = match.group(0)
    commands = [
        'textcolor', 'frac', 'cdot', 'text', 'circ', 'rho', 'implies', 
        'Delta', 'dot', 'sqrt', 'ln', 'left', 'right', 'pi', 'eta', 'psi', '%'
    ]
    for cmd in commands:
        s = re.sub(r'\\+' + cmd, r'\\\\' + cmd, s)
    return s

# Match inline R code blocks
new_content = re.sub(r'`r .*?`', fix_r_inline, content, flags=re.DOTALL)

with open('Karta_Projektowa_Szablon.qmd', 'w') as f:
    f.write(new_content)

print("Fixed LaTeX commands inside all inline R blocks.")
