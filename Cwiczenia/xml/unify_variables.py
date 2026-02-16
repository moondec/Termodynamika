#!/usr/bin/env python3
"""
Generate unified Moodle XML variable pool for all 7 exercises.
Adds ALL shared variables to the first question of Cw01,
and ensures consistency across all files.
"""
import xml.etree.ElementTree as ET
import random
import math
import os
import copy

random.seed(42)  # Reproducible

# ========================= VARIABLE DEFINITIONS =========================
# Each: (name, min, max, decimals, step)
# Step is used to generate "nice" values on a grid
VARS = [
    # Ćw.1 — Gazy (already in Cw01)
    ("pman",   6,    12,   1,  0.5),
    ("patm",   740,  770,  0,  5),
    ("V",      3,    8,    1,  0.5),
    ("t",      15,   35,   0,  5),
    ("tfire",  200,  400,  0,  50),
    ("yN2",    70,   85,   0,  1),
    ("pmix",   3,    8,    1,  0.5),
    ("tmix",   15,   30,   0,  5),
    ("Vmix",   1,    4,    1,  0.5),
    ("Tvalve", 200,  300,  0,  10),
    # Ćw.2 — Sprężarka (partially in Cw02)
    ("p2",     7,    12,   0,  1),
    ("t1",     15,   25,   0,  5),
    ("npoly",  1.25, 1.38, 2,  0.01),
    ("Vn",     60,   150,  0,  10),
    ("tchl",   25,   40,   0,  5),
    ("twic",   10,   20,   0,  5),     # NEW: woda chłodnicza wlot
    ("twoc",   35,   50,   0,  5),     # NEW: woda chłodnicza wylot
    ("t1p",    18,   28,   0,  2),     # NEW: temp ssania pomiar
    ("t2p",    180,  250,  0,  10),    # NEW: temp tłoczenia pomiar
    ("p2p",    6,    10,   1,  0.5),   # NEW: ciśn tłoczenia pomiar
    # Ćw.3 — Kocioł
    ("pk",     10,   15,   0,  1),     # NEW: ciśnienie kotła
    ("tp",     200,  300,  0,  25),    # NEW: temp pary
    ("md",     1.5,  3.0,  1,  0.5),
    ("tz",     40,   80,   0,  10),
    ("ek",     0.85, 0.95, 2,  0.01),
    ("pdl",    2,    6,    0,  1),     # NEW: ciśn dławienia
    ("hm",     2200, 2600, 0,  50),
    # Ćw.4 — Turbina
    ("p1t",    10,   15,   0,  1),     # NEW: ciśn wlot turbiny
    ("t1t",    200,  300,  0,  25),
    ("p2t",    0.5,  2.0,  1,  0.5),   # NEW: ciśn wylot turbiny
    ("mdt",    0.3,  0.8,  2,  0.05),
    ("eis",    0.75, 0.85, 2,  0.01),
    # Ćw.5 — Wymiennik
    ("ms5",    0.5,  2.0,  1,  0.1),
    ("tsi",    250,  350,  0,  25),
    ("tso",    120,  180,  0,  10),
    ("twi5",   15,   25,   0,  5),
    ("two5",   60,   90,   0,  10),
    ("T05",    15,   25,   0,  5),
    # Ćw.6 — Chłodnictwo
    ("to6",    -5,   5,    0,  1),
    ("tk6",    35,   45,   0,  1),
    ("Qo6",   200,  500,  0,  50),
    ("dr6",    50,   100,  0,  10),
    # Ćw.7 — HVAC
    ("tzz",    -15,  -5,   0,  1),
    ("tzl",    28,   36,   0,  2),
    ("tw8",    20,   24,   0,  1),
    ("Vd8",    15000,30000,0,  2500),
    ("Qj8",    30,   80,   0,  10),
    ("rec8",   60,   80,   0,  5),
    ("tn8",    14,   18,   0,  1),
]

N_ITEMS = 50

def gen_values(vmin, vmax, decimals, step, n=N_ITEMS):
    """Generate n random values on a grid [vmin, vmax] with given step."""
    if step <= 0:
        step = 10**(-decimals) if decimals > 0 else 1
    # Build list of possible values
    possible = []
    v = vmin
    while v <= vmax + step * 0.01:
        possible.append(round(v, decimals))
        v += step
    # Sample with replacement
    return [random.choice(possible) for _ in range(n)]

def format_val(val, decimals):
    """Format value with correct decimal places."""
    if decimals == 0:
        return str(int(round(val)))
    else:
        return f"{val:.{decimals}f}"

def make_dataset_def_xml(name, vmin, vmax, decimals, values, status="shared"):
    """Create a dataset_definition XML element."""
    dd = ET.SubElement(ET.Element("tmp"), "dataset_definition")
    
    st = ET.SubElement(dd, "status")
    st_t = ET.SubElement(st, "text")
    st_t.text = status
    
    nm = ET.SubElement(dd, "name")
    nm_t = ET.SubElement(nm, "text")
    nm_t.text = name
    
    tp = ET.SubElement(dd, "type")
    tp.text = "calculated"
    
    dist = ET.SubElement(dd, "distribution")
    dist_t = ET.SubElement(dist, "text")
    dist_t.text = "uniform"
    
    mn = ET.SubElement(dd, "minimum")
    mn_t = ET.SubElement(mn, "text")
    mn_t.text = format_val(vmin, decimals)
    
    mx = ET.SubElement(dd, "maximum")
    mx_t = ET.SubElement(mx, "text")
    mx_t.text = format_val(vmax, decimals)
    
    dec = ET.SubElement(dd, "decimals")
    dec_t = ET.SubElement(dec, "text")
    dec_t.text = str(decimals)
    
    ic = ET.SubElement(dd, "itemcount")
    ic.text = str(len(values))
    
    items = ET.SubElement(dd, "dataset_items")
    for i, v in enumerate(values, 1):
        item = ET.SubElement(items, "dataset_item")
        num = ET.SubElement(item, "number")
        num.text = str(i)
        val = ET.SubElement(item, "value")
        val.text = format_val(v, decimals)
    
    noi = ET.SubElement(dd, "number_of_items")
    noi.text = str(len(values))
    
    return dd

# ========================= GENERATE ALL VALUES =========================
print("Generating unified variable pool...")
all_values = {}
for name, vmin, vmax, dec, step in VARS:
    all_values[name] = gen_values(vmin, vmax, dec, step)
    print(f"  {name:10s}  [{vmin} .. {vmax}]  step={step}  dec={dec}  sample: {all_values[name][:5]}")

# ========================= PROCESS EACH XML FILE =========================
xml_dir = "/Users/marekurbaniak/Documents/R/Termodynamika_quatro/Cwiczenia/xml"

for fname in sorted(os.listdir(xml_dir)):
    if not fname.startswith("Cw0") or not fname.endswith(".xml"):
        continue
    
    fpath = os.path.join(xml_dir, fname)
    print(f"\n{'='*60}")
    print(f"Processing: {fname}")
    
    # Parse with ET, preserving structure
    tree = ET.parse(fpath)
    root = tree.getroot()
    
    is_cw01 = fname.startswith("Cw01")
    
    # Track which vars are already defined in this file
    existing_vars = set()
    for dd in root.findall('.//dataset_definition'):
        vname = dd.find('name/text').text
        existing_vars.add(vname)
    
    print(f"  Existing vars: {sorted(existing_vars)}")
    
    # For CW01: add ALL missing variables to the FIRST calculated question
    if is_cw01:
        first_q = None
        for q in root.findall('question'):
            if q.attrib.get('type') == 'calculated':
                first_q = q
                break
        
        if first_q is not None:
            dds_el = first_q.find('dataset_definitions')
            if dds_el is None:
                dds_el = ET.SubElement(first_q, 'dataset_definitions')
            
            # First, update existing variable definitions with new values
            for dd in dds_el.findall('dataset_definition'):
                vname = dd.find('name/text').text
                if vname in all_values:
                    # Update the dataset_items with our generated values
                    var_info = next((v for v in VARS if v[0] == vname), None)
                    if var_info:
                        _, vmin, vmax, dec, step = var_info
                        # Update min/max
                        dd.find('minimum/text').text = format_val(vmin, dec)
                        dd.find('maximum/text').text = format_val(vmax, dec)
                        dd.find('decimals/text').text = str(dec)
                        # Update items
                        items_el = dd.find('dataset_items')
                        if items_el is not None:
                            dd.remove(items_el)
                        items_el = ET.SubElement(dd, 'dataset_items')
                        for i, v in enumerate(all_values[vname], 1):
                            item = ET.SubElement(items_el, 'dataset_item')
                            num = ET.SubElement(item, 'number')
                            num.text = str(i)
                            val_el = ET.SubElement(item, 'value')
                            val_el.text = format_val(v, dec)
                        # Update counts
                        ic = dd.find('itemcount')
                        if ic is not None:
                            ic.text = str(N_ITEMS)
                        noi = dd.find('number_of_items')
                        if noi is not None:
                            noi.text = str(N_ITEMS)
                        print(f"  Updated: {vname}")
            
            # Add missing variables
            added = []
            for name, vmin, vmax, dec, step in VARS:
                if name not in existing_vars:
                    vals = all_values[name]
                    new_dd = make_dataset_def_xml(name, vmin, vmax, dec, vals)
                    dds_el.append(new_dd)
                    added.append(name)
            
            if added:
                print(f"  Added to Cw01 first question: {added}")
    
    else:
        # For Cw02-Cw07: update existing variable definitions with unified values
        for q in root.findall('question'):
            if q.attrib.get('type') != 'calculated':
                continue
            dds_el = q.find('dataset_definitions')
            if dds_el is None:
                continue
            
            for dd in dds_el.findall('dataset_definition'):
                vname = dd.find('name/text').text
                if vname in all_values:
                    var_info = next((v for v in VARS if v[0] == vname), None)
                    if var_info:
                        _, vmin, vmax, dec, step = var_info
                        dd.find('minimum/text').text = format_val(vmin, dec)
                        dd.find('maximum/text').text = format_val(vmax, dec)
                        dd.find('decimals/text').text = str(dec)
                        items_el = dd.find('dataset_items')
                        if items_el is not None:
                            dd.remove(items_el)
                        items_el = ET.SubElement(dd, 'dataset_items')
                        for i, v in enumerate(all_values[vname], 1):
                            item = ET.SubElement(items_el, 'dataset_item')
                            num = ET.SubElement(item, 'number')
                            num.text = str(i)
                            val_el = ET.SubElement(item, 'value')
                            val_el.text = format_val(v, dec)
                        ic = dd.find('itemcount')
                        if ic is not None:
                            ic.text = str(N_ITEMS)
                        noi = dd.find('number_of_items')
                        if noi is not None:
                            noi.text = str(N_ITEMS)
                        print(f"  Updated: {vname}")
    
    # Write back
    ET.indent(tree, space="    ")
    tree.write(fpath, encoding='UTF-8', xml_declaration=True)
    print(f"  Written: {fname}")

print("\n" + "="*60)
print("Done! All files updated with unified variable pool.")
print(f"Total variables: {len(VARS)}")
print(f"Values per variable: {N_ITEMS}")
