import os
import re

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
    "Sprężarka": "bi-fan",
    "Pompa": "bi-water",
    "Bilans": "bi-scale",
}

DEFAULT_ICON = "bi-bookmark"

R_SETUP_BLOCK = """
```{r}
#| echo: false
#| warning: false
#| message: false
library(ggplot2)
theme_set(theme_minimal(base_size = 18))
```
"""

def get_icon(header_text):
    text = header_text.lower()
    for key, icon in ICON_MAP.items():
        if key.lower() in text:
            return icon
    return DEFAULT_ICON

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    # Track if we need to insert R setup
    has_r_setup = "theme_set(theme_minimal" in content
    yaml_end_index = -1
    
    # Pass 1: YAML detection and Header Icons
    formatted_lines = []
    in_yaml = False
    
    for i, line in enumerate(lines):
        # YAML block tracking
        if line.strip() == "---":
            if i == 0:
                in_yaml = True
            elif in_yaml:
                in_yaml = False
                yaml_end_index = len(formatted_lines) # Mark position after YAML
        
        # Header Processing
        if not in_yaml and line.strip().startswith("## ") and "<i class=\"bi" not in line:
            # It's a header
            header_content = line.strip()[3:].strip()
            # Clean attributes
            clean_text = re.sub(r'\{.*?\}', '', header_content).strip()
            
            if clean_text:
                icon = get_icon(clean_text)
                
                # Extract attributes if any
                attrs_match = re.search(r'(\{.*?\})$', line.strip())
                attrs = attrs_match.group(1) if attrs_match else ""
                
                text_part = header_content.replace(attrs, "").strip()
                
                new_line = f"## <i class=\"bi {icon}\"></i> {text_part} {attrs}"
                formatted_lines.append(new_line)
            else:
                formatted_lines.append(line)
        else:
            formatted_lines.append(line)

    # Pass 2: R Setup Injection
    final_lines = []
    if not has_r_setup and yaml_end_index != -1:
        # Insert R setup after YAML
        final_lines = formatted_lines[:yaml_end_index+1]
        final_lines.append(R_SETUP_BLOCK)
        final_lines.extend(formatted_lines[yaml_end_index+1:])
        print(f"  Inserted R setup chunk into {os.path.basename(filepath)}")
    else:
        final_lines = formatted_lines
        if has_r_setup:
             print(f"  R setup already present in {os.path.basename(filepath)}")

    # Write back
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(final_lines))
    print(f"Processed {filepath}")

# Main execution
if __name__ == "__main__":
    target_dir = "Wyklady"
    # Skip 01 and 02 as they are already manually polished
    skip = ["01_Wprowadzenie.qmd", "02_I_Zasada_Bilans.qmd"]
    
    files = sorted([f for f in os.listdir(target_dir) if f.endswith(".qmd")])
    
    for f in files:
        if f not in skip:
            process_file(os.path.join(target_dir, f))
