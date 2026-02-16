import re
import random
import requests
import CoolProp.CoolProp as CP
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuration
HTML_FILE = "/Users/marekurbaniak/Documents/R/Termodynamika_quatro/Cwiczenia/xml/tablice_termodynamiczne.html"
NIST_BASE_URL = "https://webbook.nist.gov/cgi/fluid.cgi"

# Mapping: HTML Fluid Name -> NIST ID
FLUID_MAP = {
    "Woda": "C7732185",
    "R134a": "C811972",
    "R290": "C74986"
}

def clean_val(s):
    """Clean HTML string to float."""
    if not s or "—" in s or "?" in s: return None
    # Remove HTML tags if any
    s = re.sub(r'<[^>]+>', '', s)
    s = s.replace(',', '.').replace(' ', '').strip()
    try:
        if '·10' in s: # scientific notation handling if needed
             parts = s.split('·10')
             return float(parts[0]) * (10**int(parts[1]))
        return float(s)
    except:
        return None

def get_nist_data(fluid_id, prop_type, p_bar=None, t_c=None):
    """Query NIST WebBook.
    prop_type: 'SatP', 'SatT', 'IsoBar'
    """
    params = {
        "Action": "Data",
        "Wide": "on",
        "ID": fluid_id,
        "Type": prop_type,
        "RefState": "DEF",
        "TUnit": "C",
        "PUnit": "bar",
        "DUnit": "kg/m3",
        "HUnit": "kJ/kg",
        "SUnit": "kJ/kg/K",
        "WUnit": "m/s",
        "VisUnit": "uPa*s",
        "STUnit": "N/m"
    }
    
    if prop_type == 'SatP':
        params['PLow'] = p_bar
        params['PHigh'] = p_bar
    elif prop_type == 'SatT':
        params['TLow'] = t_c
        params['THigh'] = t_c
    elif prop_type == 'IsoBar':
        params['P'] = p_bar # NIST uses P for IsoBar, TL/TH for range
        params['TLow'] = t_c
        params['THigh'] = t_c

    try:
        r = requests.get(NIST_BASE_URL, params=params, timeout=10)
        r.raise_for_status()
        # Parse TSV response
        lines = r.text.splitlines()
        
        # Find header line
        header_idx = -1
        for i, line in enumerate(lines):
            if '\t' in line and "Temperature" in line:
                header_idx = i
                break
        
        if header_idx == -1:
            print(f"DEBUG: No header found in NIST response. URL: {r.url}")
            return None
            
        headers = lines[header_idx].split('\t')
        
        # Parse all data rows
        data_rows = []
        for line in lines[header_idx+1:]:
            parts = line.split('\t')
            if len(parts) == len(headers):
                try:
                    row_dict = dict(zip(headers, parts))
                    # Convert key numeric columns to float for searching
                    if "Temperature (C)" in row_dict:
                        row_dict["_T"] = float(row_dict["Temperature (C)"])
                    if "Pressure (bar)" in row_dict:
                        row_dict["_P"] = float(row_dict["Pressure (bar)"])
                    data_rows.append(row_dict)
                except:
                    continue

        if not data_rows:
            return None
            
        # Find best match
        best_row = None
        if prop_type == 'SatT' and t_c is not None:
             # Find row with T closest to t_c
             best_row = min(data_rows, key=lambda r: abs(r.get("_T", -9999) - t_c))
        elif prop_type == 'SatP' and p_bar is not None:
             best_row = min(data_rows, key=lambda r: abs(r.get("_P", -9999) - p_bar))
        elif prop_type == 'IsoBar':
             # For IsoBar, we might have multiple rows if T scan. Find closest T.
              best_row = min(data_rows, key=lambda r: abs(r.get("_T", -9999) - t_c))
        else:
             best_row = data_rows[0]
             
        return best_row

    except Exception as e:
        print(f"Error fetching NIST data: {e}")
        return None

def verify_tables():
    print("Reading HTML...")
    # ... (rest of function as before, no changes needed for debug usually, but let's just update the get_nist_data logic)
    
    with open(HTML_FILE, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
        
    tables = soup.find_all("div", class_="table-container")
    samples = []
    
    # 1. Collect potential rows
    print(f"Found {len(tables)} tables.")
    
    for t_idx, container in enumerate(tables):
        header_text = container.find("h3").get_text()
        
        # Identify Fluid
        fluid = None
        if "Woda" in header_text or "Para wodna" in header_text: fluid = "Woda"
        elif "R134a" in header_text: fluid = "R134a"
        elif "R290" in header_text: fluid = "R290"
        
        # Identify Type
        t_type = None
        if "nasycona (wg ciśnienia)" in header_text or "nasycony (wg ciśnienia)" in header_text: t_type = "SatP"
        elif "nasycona (wg temperatury)" in header_text or "nasycony (wg temperatury)" in header_text: t_type = "SatT"
        elif "przegrzana" in header_text or "przegrzany" in header_text: t_type = "IsoBar"
        
        if not fluid or not t_type: continue
        
        # Parse Rows
        rows = container.find_all("tr")
        data_rows = [r for r in rows if r.find("td")]
        
        for r in data_rows:
            cols = r.find_all("td")
            if not cols: continue
            
            try:
                item = {
                    "fluid": fluid,
                    "type": t_type,
                    "table_name": header_text,
                    "raw_row": r
                }
                
                if t_type == "SatP":
                    item["p_bar"] = clean_val(cols[0].text)
                    item["vals"] = {
                        "v''": (clean_val(cols[3].text), "Volume (v)"), 
                        "h''": (clean_val(cols[6].text), "Enthalpy (v)"), # Fixed key
                        "s''": (clean_val(cols[9].text), "Entropy (v)")   # Fixed key
                    }
                    
                elif t_type == "SatT":
                    item["t_c"] = clean_val(cols[0].text)
                    # HTML Col 1 is p_sat in kPa.
                    p_kpa = clean_val(cols[1].text)
                    
                    item["vals"] = {
                         "p_sat": (p_kpa/100.0 if p_kpa else None, "Pressure"),
                         "h''": (clean_val(cols[6].text), "Enthalpy (v)"),
                         "s''": (clean_val(cols[9].text), "Entropy (v)")
                    }

                if item.get("p_bar") or item.get("t_c") is not None:
                     samples.append(item)
            except Exception as e:
                # print(e) 
                continue

    # 2. Select 20 random
    if len(samples) < 20: 
        selected = samples
    else:
        selected = random.sample(samples, 20)
        
    print(f"Selected {len(selected)} rows for verification.\n")
    
    # 3. Verify
    results = []
    for i, item in enumerate(selected):
        fluid_id = FLUID_MAP[item["fluid"]]
        prop_type = item["type"]
        
        # Delay to be nice to NIST
        time.sleep(0.5)
        
        nist_data = get_nist_data(fluid_id, prop_type, 
                                  p_bar=item.get("p_bar"), 
                                  t_c=item.get("t_c"))
        
        if not nist_data:
            print(f"Failed to fetch NIST data for {item['fluid']} {item.get('t_c') or item.get('p_bar')}")
            continue
            
        # Compare
        for prop_name, (val_html, nist_key_part) in item["vals"].items():
            if val_html is None: continue
            
            # Find matching NIST key in the dict
            # NIST headers are tricky. Let's look for partial match in keys.
            nist_val = None
            nist_key_found = None
            
            for k in nist_data.keys():
                if nist_key_part in k:
                    nist_key_found = k
                    break
            
            # Special logic for Density -> Volume
            if not nist_key_found and "Volume" in prop_name:
                # Try finding Density
                for k in nist_data.keys():
                    if "Density (v)" in k or "Density (vapor)" in k:
                        try:
                            rho = float(nist_data[k])
                            nist_val = 1.0/rho if rho != 0 else 0
                            nist_key_found = "Calculated 1/rho"
                        except: pass
                        break
            
            if nist_key_found and nist_val is None:
                try:
                    nist_val = float(nist_data[nist_key_found])
                except:
                    nist_val = None
                    
            if nist_val is not None:
                diff_abs = abs(val_html - nist_val)
                avg = (abs(val_html) + abs(nist_val)) / 2
                if avg == 0: avg = 1
                diff_rel = (diff_abs / avg) * 100
                
                results.append({
                    "Table": item["table_name"],
                    "Point": f"p={item.get('p_bar')} bar" if item.get('p_bar') else f"t={item.get('t_c')} C",
                    "Property": prop_name,
                    "HTML Value": val_html,
                    "NIST Value": round(nist_val, 5),
                    "Diff (%)": round(diff_rel, 4)
                })
            else:
                # Debug missing keys
                # print(f"Missing key for {prop_name} ({nist_key_part}). Available: {list(nist_data.keys())}")
                pass
    
    # 4. Report
    print("\n\nVerification Results (Top discrepancies):")
    df = pd.DataFrame(results)
    if not df.empty:
        print(df.sort_values(by="Diff (%)", ascending=False).to_markdown(index=False))
        df.to_csv("nist_verification_results.csv", index=False)
    else:
        print("No valid comparisons made.")

if __name__ == "__main__":
    verify_tables()
