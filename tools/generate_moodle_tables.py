import CoolProp
import CoolProp.CoolProp as CP
import numpy as np

# Configuration
OUTPUT_FILE = "/Users/marekurbaniak/Documents/R/Termodynamika_quatro/Cwiczenia/xml/tablice_termodynamiczne_moodle.html"

# Common Inline Styles
STYLE_TABLE = "width: 100%; border-collapse: collapse; font-family: 'Segoe UI', Arial, sans-serif; font-size: 13px; margin: 0 auto;"
STYLE_TH = "border: 1px solid #666; padding: 8px; position: sticky; top: 0; z-index: 10; font-weight: bold; background-color: #f0f0f0; color: #000;"
STYLE_TD = "border: 1px solid #999; padding: 6px; text-align: center; vertical-align: middle;"
STYLE_STICKY_COL_TH = "position: sticky; left: 0; z-index: 20; border-right: 2px solid #444;"
STYLE_STICKY_COL_TD = "position: sticky; left: 0; z-index: 5; border-right: 2px solid #444; font-weight: bold;"
STYLE_DETAILS = "margin-bottom: 20px; border: 1px solid #ccc; border-radius: 5px; overflow: hidden; background: #fff;"
STYLE_SUMMARY = "cursor: pointer; padding: 10px; background-color: #eee; font-weight: bold; list-style: none;"
STYLE_WRAPPER = "overflow-x: auto; max-height: 700px; overflow-y: auto; position: relative;"

# Theme Colors (Background for headers, striped rows)
THEMES = {
    "blue":   {"head": "#2980b9", "stripe": "#eaf2f8", "th_bg": "#d4e6f1"},
    "green":  {"head": "#27ae60", "stripe": "#e9f7ef", "th_bg": "#d5f5e3"},
    "cyan":   {"head": "#17a2b8", "stripe": "#e0f7fa", "th_bg": "#b2ebf2"},
    "orange": {"head": "#e67e22", "stripe": "#fcece0", "th_bg": "#fad7a0"},
    "red":    {"head": "#c0392b", "stripe": "#fadbd8", "th_bg": "#f9e79f"}
}

def fmt(val, precision=4):
    if val is None or np.isnan(val): return "—"
    if abs(val) < 0.001 and val != 0: s = f"{val:.6f}"
    elif abs(val) < 0.1 and val != 0: s = f"{val:.5f}"
    elif abs(val) >= 1000: s = f"{val:.0f}"
    else: s = f"{val:.{precision}f}"
    s = s.replace('.', ',')
    if ',' in s: s = s.rstrip('0').rstrip(',')
    return s

def get_prop(fluid, prop, p=None, t=None, q=None):
    try:
        args = []
        if p is not None: args.extend(['P', p])
        if t is not None: args.extend(['T', t + 273.15])
        if q is not None: args.extend(['Q', q])
        return CP.PropsSI(prop, *args, fluid)
    except: return None

def get_row_style(idx, theme_key):
    # Group by 5: 0-4 white, 5-9 colored
    bg = "#ffffff"
    if (idx // 5) % 2 == 1:
        bg = THEMES[theme_key]["stripe"]
    return f"background-color: {bg};"

def generate_sat_p_table(fluid, title, fluid_name_display, p_range, theme_key="blue"):
    theme = THEMES[theme_key]
    th_style = f"{STYLE_TH} background-color: {theme['th_bg']}; border-color: {theme['head']};"
    sticky_th = f"{th_style} {STYLE_STICKY_COL_TH} background-color: {theme['th_bg']};"
    
    html = f"""
    <details style="{STYLE_DETAILS}">
        <summary style="{STYLE_SUMMARY} background-color: {theme['head']}; color: white;">
            <span style="font-size: 1.1em;">{title} ({fluid_name_display})</span>
        </summary>
        <div style="{STYLE_WRAPPER}">
            <table style="{STYLE_TABLE}">
                <thead>
                    <tr>
                        <th style="{sticky_th}">p [bar]</th>
                        <th style="{th_style}">t_sat [°C]</th>
                        <th style="{th_style}">v' [dm³/kg]</th>
                        <th style="{th_style}">v'' [m³/kg]</th>
                        <th style="{th_style}">ρ'' [kg/m³]</th>
                        <th style="{th_style}">h' [kJ/kg]</th>
                        <th style="{th_style}">h'' [kJ/kg]</th>
                        <th style="{th_style}">r [kJ/kg]</th>
                        <th style="{th_style}">s' [kJ/kgK]</th>
                        <th style="{th_style}">s'' [kJ/kgK]</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for i, p_bar in enumerate(p_range):
        row_bg = get_row_style(i, theme_key)
        p_pa = p_bar * 1e5
        try:
            ts = get_prop(fluid, 'T', p=p_pa, q=0) - 273.15
            vl = get_prop(fluid, 'D', p=p_pa, q=0)**-1 * 1000
            vv = get_prop(fluid, 'D', p=p_pa, q=1)**-1
            rho = get_prop(fluid, 'D', p=p_pa, q=1)
            hl = get_prop(fluid, 'H', p=p_pa, q=0) / 1000
            hv = get_prop(fluid, 'H', p=p_pa, q=1) / 1000
            r = hv - hl
            sl = get_prop(fluid, 'S', p=p_pa, q=0) / 1000
            sv = get_prop(fluid, 'S', p=p_pa, q=1) / 1000
            
            html += f"""<tr style="{row_bg}">
                <td style="{STYLE_TD} {STYLE_STICKY_COL_TD} {row_bg}">{fmt(p_bar, 3)}</td>
                <td style="{STYLE_TD}">{fmt(ts, 2)}</td>
                <td style="{STYLE_TD} background-color: rgba(255,255,0,0.05);">{fmt(vl, 4)}</td>
                <td style="{STYLE_TD} background-color: rgba(255,255,0,0.05);">{fmt(vv, 4)}</td>
                <td style="{STYLE_TD} background-color: rgba(255,255,0,0.05); color: #d35400;">{fmt(rho, 3)}</td>
                <td style="{STYLE_TD} background-color: rgba(0,255,255,0.05);">{fmt(hl, 1)}</td>
                <td style="{STYLE_TD} background-color: rgba(0,255,255,0.05);">{fmt(hv, 1)}</td>
                <td style="{STYLE_TD} background-color: rgba(0,255,255,0.05); font-weight:bold;">{fmt(r, 1)}</td>
                <td style="{STYLE_TD}">{fmt(sl, 4)}</td>
                <td style="{STYLE_TD}">{fmt(sv, 4)}</td>
            </tr>"""
        except: continue

    html += "</tbody></table></div></details>"
    return html

def generate_sat_t_table(fluid, title, fluid_name_display, t_range, theme_key="green"):
    theme = THEMES[theme_key]
    th_style = f"{STYLE_TH} background-color: {theme['th_bg']}; border-color: {theme['head']};"
    sticky_th = f"{th_style} {STYLE_STICKY_COL_TH} background-color: {theme['th_bg']};"
    
    html = f"""
    <details style="{STYLE_DETAILS}">
        <summary style="{STYLE_SUMMARY} background-color: {theme['head']}; color: white;">
            <span style="font-size: 1.1em;">{title} ({fluid_name_display})</span>
        </summary>
        <div style="{STYLE_WRAPPER}">
            <table style="{STYLE_TABLE}">
                <thead>
                    <tr>
                        <th style="{sticky_th}">t [°C]</th>
                        <th style="{th_style}">p_sat [kPa/bar]</th>
                        <th style="{th_style}">v' [dm³/kg]</th>
                        <th style="{th_style}">v'' [m³/kg]</th>
                        <th style="{th_style}">ρ'' [kg/m³]</th>
                        <th style="{th_style}">h' [kJ/kg]</th>
                        <th style="{th_style}">h'' [kJ/kg]</th>
                        <th style="{th_style}">r [kJ/kg]</th>
                        <th style="{th_style}">s' [kJ/kgK]</th>
                        <th style="{th_style}">s'' [kJ/kgK]</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for i, t_c in enumerate(t_range):
        row_bg = get_row_style(i, theme_key)
        try:
            p_sat = get_prop(fluid, 'P', t=t_c, q=0) / 1000 # kPa
            # For header display, standard is kPa, but let's conform
            vl = get_prop(fluid, 'D', t=t_c, q=0)**-1 * 1000
            vv = get_prop(fluid, 'D', t=t_c, q=1)**-1
            rho = get_prop(fluid, 'D', t=t_c, q=1)
            hl = get_prop(fluid, 'H', t=t_c, q=0) / 1000
            hv = get_prop(fluid, 'H', t=t_c, q=1) / 1000
            r = hv - hl
            sl = get_prop(fluid, 'S', t=t_c, q=0) / 1000
            sv = get_prop(fluid, 'S', t=t_c, q=1) / 1000
            
            html += f"""<tr style="{row_bg}">
                <td style="{STYLE_TD} {STYLE_STICKY_COL_TD} {row_bg}">{fmt(t_c, 1)}</td>
                <td style="{STYLE_TD}">{fmt(p_sat, 3)}</td>
                <td style="{STYLE_TD} background-color: rgba(255,255,0,0.05);">{fmt(vl, 4)}</td>
                <td style="{STYLE_TD} background-color: rgba(255,255,0,0.05);">{fmt(vv, 4)}</td>
                <td style="{STYLE_TD} background-color: rgba(255,255,0,0.05); color: #d35400;">{fmt(rho, 3)}</td>
                <td style="{STYLE_TD} background-color: rgba(0,255,255,0.05);">{fmt(hl, 1)}</td>
                <td style="{STYLE_TD} background-color: rgba(0,255,255,0.05);">{fmt(hv, 1)}</td>
                <td style="{STYLE_TD} background-color: rgba(0,255,255,0.05); font-weight:bold;">{fmt(r, 1)}</td>
                <td style="{STYLE_TD}">{fmt(sl, 4)}</td>
                <td style="{STYLE_TD}">{fmt(sv, 4)}</td>
            </tr>"""
        except: continue
        
    html += "</tbody></table></div></details>"
    return html

def generate_superheated_table(fluid, title, fluid_name_display, p_range, t_range, theme_key="red"):
    theme = THEMES[theme_key]
    th_style = f"{STYLE_TH} background-color: {theme['th_bg']}; border-color: {theme['head']};"
    sticky_th = f"{th_style} {STYLE_STICKY_COL_TH} background-color: {theme['th_bg']}; z-index: 30;"
    
    # Headers
    header_cols = ""
    sub_header = ""
    for p_bar in p_range:
        ts_val = get_prop(fluid, 'T', p=p_bar*1e5, q=1)
        ts_str = f"t_s={fmt(ts_val-273.15, 1)}" if ts_val else "Nadkryt."
        header_cols += f'<th colspan="3" style="{th_style} border-bottom: 2px solid #555;">p={fmt(p_bar, 3)} bar<br><small>{ts_str}</small></th>'
        sub_header += f'<th style="{th_style} background-color:rgba(255,255,0,0.1);">v</th><th style="{th_style} background-color:rgba(0,255,255,0.1);">h</th><th style="{th_style}">s</th>'

    html = f"""
    <details style="{STYLE_DETAILS}">
        <summary style="{STYLE_SUMMARY} background-color: {theme['head']}; color: white;">
            <span style="font-size: 1.1em;">{title} ({fluid_name_display})</span>
        </summary>
        <div style="{STYLE_WRAPPER}">
            <table style="{STYLE_TABLE}">
                <thead>
                    <tr>
                        <th rowspan="2" style="{sticky_th}">t [°C]</th>
                        {header_cols}
                    </tr>
                    <tr>{sub_header}</tr>
                </thead>
                <tbody>
    """
    
    # Saturation Line
    html += f'<tr style="font-weight:bold; background-color: #fff5e6; border-bottom: 2px solid #aaa;"><td style="{STYLE_TD} {STYLE_STICKY_COL_TD} background-color: #fff5e6;">Stan nas.</td>'
    for p_bar in p_range:
        try:
            p_pa = p_bar*1e5
            if get_prop(fluid, 'T', p=p_pa, q=1) is None:
                html += f'<td colspan="3" style="{STYLE_TD}">(Nadkryt.)</td>'
            else:
                vv = get_prop(fluid, 'D', p=p_pa, q=1)**-1
                hv = get_prop(fluid, 'H', p=p_pa, q=1)/1000
                sv = get_prop(fluid, 'S', p=p_pa, q=1)/1000
                html += f'<td style="{STYLE_TD} background-color:rgba(255,255,0,0.05);">{fmt(vv,4)}</td><td style="{STYLE_TD} background-color:rgba(0,255,255,0.05);">{fmt(hv,1)}</td><td style="{STYLE_TD}">{fmt(sv,4)}</td>'
        except: html += f'<td colspan="3" style="{STYLE_TD}">-</td>'
    html += '</tr>'
    
    # Temp Rows
    for i, t_c in enumerate(t_range):
        row_bg = get_row_style(i, theme_key)
        html += f'<tr style="{row_bg}"><td style="{STYLE_TD} {STYLE_STICKY_COL_TD} {row_bg}">{fmt(t_c, 0)}</td>'
        
        for p_bar in p_range:
            p_pa = p_bar * 1e5
            ts_val = get_prop(fluid, 'T', p=p_pa, q=1)
            ts = ts_val - 273.15 if ts_val else None
            
            if ts is not None and t_c < ts:
                html += f'<td colspan="3" style="{STYLE_TD} color:#ccc;">—</td>'
            else:
                try:
                    v = get_prop(fluid, 'D', t=t_c, p=p_pa)**-1
                    h = get_prop(fluid, 'H', t=t_c, p=p_pa)/1000
                    s = get_prop(fluid, 'S', t=t_c, p=p_pa)/1000
                    html += f'<td style="{STYLE_TD} background-color:rgba(255,255,0,0.05);">{fmt(v,4)}</td><td style="{STYLE_TD} background-color:rgba(0,255,255,0.05);">{fmt(h,1)}</td><td style="{STYLE_TD}">{fmt(s,4)}</td>'
                except: html += f'<td colspan="3" style="{STYLE_TD}">?</td>'
        html += '</tr>'
        
    html += "</tbody></table></div></details>"
    return html

def main():
    content = ""
    # Water Sat P
    p_bars = [x*10 for x in [*np.arange(0.001,0.01,0.001), *np.arange(0.01,0.1,0.01), *np.arange(0.1,1.0,0.1), *np.arange(1.0,22.1,0.5)]]
    content += generate_sat_p_table("Water", "Tablica 1. Woda nasycona", "Woda", p_bars, "blue")
    
    # Water Sat T
    content += generate_sat_t_table("Water", "Tablica 2. Woda nasycona", "Woda", np.arange(0.01, 374, 1.0), "green")
    
    # Superheated
    p_sup = [0.1, 0.5, 1, 2, 5, 8, 10, 12, 15, 17, 20, 30, 40, 50, 70, 100, 120, 150, 200, 250]
    content += generate_superheated_table("Water", "Tablica 3. Para przegrzana", "Woda", p_sup, np.arange(0, 801, 10.0), "red")
    
    # R134a
    content += generate_sat_t_table("R134a", "Tablica 4. R134a Sat", "R134a", np.arange(-50, 101, 1.0), "cyan")
    content += generate_sat_p_table("R134a", "Tablica 5. R134a Sat", "R134a", [0.1,0.2,0.3,0.4,0.5,0.6,0.8,1,1.5,2,3,4,5,6,8,10,12,14,16,18,20,25,30,35,40], "cyan")
    
    # R290
    content += generate_sat_t_table("R290", "Tablica 6. R290 Sat", "Propan", np.arange(-50, 96, 1.0), "orange")
    content += generate_sat_p_table("R290", "Tablica 7. R290 Sat", "Propan", [0.1,0.2,0.3,0.4,0.5,0.6,0.8,1,1.5,2,3,4,5,6,8,10,12,14,16,18,20,25,30,35,40], "orange")
    content += generate_superheated_table("R290", "Tablica 8. R290 Przegrzany", "Propan", [1,5,15], np.arange(-50, 150, 10.0), "orange")

    html = f"""<!-- Moodle Output -->
<div style="font-family: Arial, sans-serif; padding: 10px; background-color: #f9f9f9;">
<h2 style="border-bottom: 2px solid #333; padding-bottom: 10px;">Tablice Termodynamiczne (Moodle-Safe)</h2>
{content}
</div>"""
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
