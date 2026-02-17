import os
import re

# Icon Mapping based on common thermodynamics keywords
ICON_MAP = {
    "Wstęp": "bi-door-open",
    "Definicja": "bi-book",
    "Energia": "bi-lightning-charge",
    "Ciepło": "bi-fire",
    "Praca": "bi-gear-wide-connected",
    "I Zasada": "bi-1-circle",
    "II Zasada": "bi-2-circle",
    "Entropia": "bi-shuffle",
    "Egzergia": "bi-battery-half",
    "Obieg": "bi-arrow-repeat",
    "Cykl": "bi-arrow-repeat",
    "Sprawność": "bi-percent",
    "Gazy": "bi-cloud",
    "Para": "bi-cloud-fog",
    "Mieszanina": "bi-diagram-3",
    "Właściwości": "bi-list-check",
    "Wykres": "bi-graph-up",
    "Tablice": "bi-table",
    "Przykład": "bi-calculator",
    "Zadanie": "bi-pencil",
    "Podsumowanie": "bi-clipboard-check",
    "Wnioski": "bi-lightbulb",
    "Literatura": "bi-journal-bookmark",
    "Agenda": "bi-list-ol",
    "Klimatyzacja": "bi-snow",
    "Chłodnictwo": "bi-thermometer-snow",
    "Spalanie": "bi-fire",
    "Wilgotne": "bi-droplet",
    "Wymiana": "bi-arrow-left-right",
    "Paliwa": "bi-fuel-pump",
    "Turbina": "bi-fan",
    "Sprężarka": "bi-风扇", # Wait, fan is better
    "Pompa": "bi-water",
    "Bilans": "bi-scale",
}

# Default icon if no keyword matches
DEFAULT_ICON = "bi-bookmark"

def get_icon(header_text):
    text_lower = header_text.lower()
    for key, icon in ICON_MAP.items():
        if key.lower() in text_lower:
            return icon
    return DEFAULT_ICON

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    changed = False
    
    for line in lines:
        # Check for Level 2 headers: ## Title
        # Avoid existing icons: <i class="bi
        if line.strip().startswith("## ") and "<i class=\"bi" not in line:
            header_content = line.strip()[3:].strip()
            # Ignore special headers like {data-menu-title...} or existing spans if complex
            if header_content:
                # Clean attributes for matching
                clean_text = re.sub(r'\{.*?\}', '', header_content).strip()
                icon_class = get_icon(clean_text)
                
                # Construct new line
                # Preserve attributes at the end
                match = re.search(r'(\{.*?\})$', line.strip())
                attrs = match.group(1) if match else ""
                
                # If attrs exist, remove them from header_content to putting icon before text
                text_part = header_content.replace(attrs, "").strip()
                
                new_line = f"## <i class=\"bi {icon_class}\"></i> {text_part} {attrs}\n"
                new_lines.append(new_line)
                changed = True
                print(f"  Added icon {icon_class} to: {clean_text}")
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Updated {filepath}")

# Main loop
target_dir = "Wyklady"
skip_files = ["01_Wprowadzenie.qmd", "02_I_Zasada_Bilans.qmd"]

for filename in sorted(os.listdir(target_dir)):
    if filename.endswith(".qmd") and filename not in skip_files:
        print(f"Processing {filename}...")
        process_file(os.path.join(target_dir, filename))
