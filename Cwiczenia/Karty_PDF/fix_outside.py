import re

with open('Karta_Projektowa_Szablon.qmd', 'r') as f:
    lines = f.readlines()

commands = [
    'textcolor', 'frac', 'cdot', 'text', 'circ', 'rho', 'implies', 
    'Delta', 'dot', 'sqrt', 'ln', 'left', 'right', 'pi', 'eta', 'psi', '%'
]

for i in range(len(lines)):
    if 'sprintf' not in lines[i]:
        for cmd in commands:
            # Replace exactly two backslashes followed by cmd with one backslash
            lines[i] = re.sub(r'\\\\(' + cmd + r')', r'\\\1', lines[i])

with open('Karta_Projektowa_Szablon.qmd', 'w') as f:
    f.writelines(lines)

print("Fixed LaTeX commands outside sprintf.")
