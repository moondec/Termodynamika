import CoolProp
import CoolProp.CoolProp as CP
import numpy as np

# Configuration
OUTPUT_FILE = "/Users/marekurbaniak/Documents/R/Termodynamika_quatro/Cwiczenia/xml/tablice_termodynamiczne.html"

# CSS Styles
CSS = """
<style>
    body { font-family: 'Segoe UI', Arial, sans-serif; color: #333; margin: 20px; font-size: 13px; }
    
    /* Container Styles */
    .table-container { margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-radius: 8px; overflow: hidden; page-break-inside: avoid; transition: all 0.3s ease; }
    .header-bar { padding: 15px; border-bottom: 3px solid; color: white; cursor: pointer; user-select: none; display: flex; justify-content: space-between; align-items: center; }
    .header-bar h3 { margin: 0; font-size: 1.2rem; font-weight: 600; }
    .header-bar p { margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.9; }
    .header-bar::after { content: '▼'; font-size: 1.2em; transition: transform 0.3s; }
    
    /* Accordion State */
    .table-container.active .header-bar::after { transform: rotate(180deg); }
    .table-wrapper { display: none; overflow-x: auto; max-height: 800px; overflow-y: auto; border: 1px solid #ddd; border-top: none; animation: fadeIn 0.3s; }
    .table-container.active .table-wrapper { display: block; }
    
    @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

    /* Table Styles */
    table { width: 100%; border-collapse: collapse; text-align: center; white-space: nowrap; }
    
    /* Header Cells */
    th { padding: 10px 6px; border-right: 1px solid #ddd; position: sticky; top: 0; z-index: 10; font-weight: bold; }
    th.sticky-col { position: sticky; left: 0; z-index: 20; border-right: 2px solid #ddd; }
    
    /* Data Cells */
    td { padding: 6px; border-right: 1px solid #ddd; vertical-align: middle; }
    td.sticky-col { position: sticky; left: 0; z-index: 5; background-color: inherit; font-weight: bold; border-right: 2px solid #ddd; }
    
    /* 5-row Grouping */
    tr:nth-child(10n+1), tr:nth-child(10n+2), tr:nth-child(10n+3), tr:nth-child(10n+4), tr:nth-child(10n+5) { background-color: #ffffff; }
    tr:nth-child(10n+6), tr:nth-child(10n+7), tr:nth-child(10n+8), tr:nth-child(10n+9), tr:nth-child(10n+10) { background-color: #fcece0; }

    /* Specific Table Colors */
    /* Water Sat P - Blue */
    .theme-blue .header-bar { background-color: #2980b9; border-color: #1a5276; }
    .theme-blue th { background-color: #f1f8fc; border-bottom: 2px solid #2980b9; }
    .theme-blue th.sticky-col { background-color: #f1f8fc; }
    .theme-blue tbody tr:nth-child(10n+6), .theme-blue tbody tr:nth-child(10n+7), .theme-blue tbody tr:nth-child(10n+8), .theme-blue tbody tr:nth-child(10n+9), .theme-blue tbody tr:nth-child(10n+10) { background-color: #f1f8fc; }
    
    /* Water Sat T - Green */
    .theme-green .header-bar { background-color: #27ae60; border-color: #1e8449; }
    .theme-green th { background-color: #eafaf1; border-bottom: 2px solid #27ae60; }
    .theme-green th.sticky-col { background-color: #eafaf1; }
    .theme-green tbody tr:nth-child(10n+6), .theme-green tbody tr:nth-child(10n+7), .theme-green tbody tr:nth-child(10n+8), .theme-green tbody tr:nth-child(10n+9), .theme-green tbody tr:nth-child(10n+10) { background-color: #eafaf1; }

    /* R134a - Cyan */
    .theme-cyan .header-bar { background-color: #17a2b8; border-color: #117a8b; }
    .theme-cyan th { background-color: #e0f7fa; border-bottom: 2px solid #17a2b8; }
    .theme-cyan th.sticky-col { background-color: #e0f7fa; }
    .theme-cyan tbody tr:nth-child(10n+6), .theme-cyan tbody tr:nth-child(10n+7), .theme-cyan tbody tr:nth-child(10n+8), .theme-cyan tbody tr:nth-child(10n+9), .theme-cyan tbody tr:nth-child(10n+10) { background-color: #e0f7fa; }

    /* R290 - Orange */
    .theme-orange .header-bar { background-color: #e67e22; border-color: #b3540d; }
    .theme-orange th { background-color: #fcece0; border-bottom: 2px solid #e67e22; }
    .theme-orange th.sticky-col { background-color: #fcece0; }
    .theme-orange tbody tr:nth-child(10n+6), .theme-orange tbody tr:nth-child(10n+7), .theme-orange tbody tr:nth-child(10n+8), .theme-orange tbody tr:nth-child(10n+9), .theme-orange tbody tr:nth-child(10n+10) { background-color: #fcece0; }

    /* Superheated - Red/Orange */
    .theme-red .header-bar { background-color: #d35400; border-color: #a04000; }
    .theme-red th { background-color: #fdf2e9; border-bottom: 2px solid #d35400; }
    .theme-red th.sticky-col { background-color: #fdf2e9; }
    .theme-red tbody tr:nth-child(10n+6), .theme-red tbody tr:nth-child(10n+7), .theme-red tbody tr:nth-child(10n+8), .theme-red tbody tr:nth-child(10n+9), .theme-red tbody tr:nth-child(10n+10) { background-color: #fdf2e9; }
    
    /* Utility */
    .unit { font-weight: normal; font-size: 11px; color: #555; display: block; }
    .val-rho { color: #d35400; }
    .bg-v { background-color: rgba(255, 255, 0, 0.05); }
    .bg-h { background-color: rgba(0, 255, 255, 0.05); }
</style>
<script>
document.addEventListener("DOMContentLoaded", function() {
    const headers = document.querySelectorAll(".header-bar");
    
    headers.forEach(header => {
        header.addEventListener("click", function() {
            const container = this.parentElement;
            const isActive = container.classList.contains("active");
            
            // Close all
            document.querySelectorAll(".table-container").forEach(c => c.classList.remove("active"));
            
            // Open clicked if it wasn't open
            if (!isActive) {
                container.classList.add("active");
            }
        });
    });
    
    // Open first by default
    if(document.querySelector(".table-container")) {
        document.querySelector(".table-container").classList.add("active");
    }
});
</script>
"""

def fmt(val, precision=4, sci=False):
    """Format float to string with comma decimal. Fixes integer stripping issue."""
    if val is None or np.isnan(val):
        return "—"
    if sci:
        s = f"{val:.2e}".replace('.', ',')
        base, exponent = s.split('e')
        return f"{base}·10<sup>{int(exponent)}</sup>"
    
    # Adaptive precision
    if abs(val) < 0.001 and val != 0:
         s = f"{val:.6f}"
    elif abs(val) < 0.1 and val != 0:
         s = f"{val:.5f}"
    elif abs(val) >= 1000:
         s = f"{val:.0f}"
    else:
         s = f"{val:.{precision}f}"
         
    s = s.replace('.', ',')
    
    # Only remove trailing zeros if there is a decimal separator
    if ',' in s:
        s = s.rstrip('0').rstrip(',')
        
    return s

def get_prop(fluid, prop, p=None, t=None, q=None):
    """Wrapper for CoolProp PropsSI."""
    try:
        args = []
        if p is not None: args.extend(['P', p])
        if t is not None: args.extend(['T', t + 273.15])
        if q is not None: args.extend(['Q', q])
        
        return CP.PropsSI(prop, *args, fluid)
    except:
        return None

def generate_sat_p_table(fluid, title, fluid_name_display, p_range, theme="theme-blue"):
    """Generate Saturation Table (Pressure based)."""
    
    html = f"""
    <div class="table-container {theme}">
        <div class="header-bar">
            <h3>{title}</h3>
            <p>Czynnik: {fluid_name_display}. Stan nasycenia (wg ciśnienia).</p>
        </div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th class="sticky-col">p<span class="unit">[bar]</span></th>
                        <th>t<sub>sat</sub><span class="unit">[°C]</span></th>
                        <th class="bg-v">v'<span class="unit">[dm³/kg]</span></th>
                        <th class="bg-v">v''<span class="unit">[m³/kg]</span></th>
                        <th class="bg-v"><span class="val-rho">ρ''</span><span class="unit val-rho">[kg/m³]</span></th>
                        <th class="bg-h">h'<span class="unit">[kJ/kg]</span></th>
                        <th class="bg-h">h''<span class="unit">[kJ/kg]</span></th>
                        <th class="bg-h">r<span class="unit">[kJ/kg]</span></th>
                        <th>s'<span class="unit">[kJ/kgK]</span></th>
                        <th>s''<span class="unit">[kJ/kgK]</span></th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for p_bar in p_range:
        p_pa = p_bar * 1e5
        
        # Props
        try:
            t_sat = get_prop(fluid, 'T', p=p_pa, q=0) - 273.15
            v_liq = get_prop(fluid, 'D', p=p_pa, q=0)**-1 * 1000 # dm3/kg
            v_vap = get_prop(fluid, 'D', p=p_pa, q=1)**-1
            rho_vap = get_prop(fluid, 'D', p=p_pa, q=1)
            h_liq = get_prop(fluid, 'H', p=p_pa, q=0) / 1000
            h_vap = get_prop(fluid, 'H', p=p_pa, q=1) / 1000
            r = h_vap - h_liq
            s_liq = get_prop(fluid, 'S', p=p_pa, q=0) / 1000
            s_vap = get_prop(fluid, 'S', p=p_pa, q=1) / 1000
        except:
            continue
            
        html += f"""
        <tr>
            <td class="sticky-col">{fmt(p_bar, 3)}</td>
            <td>{fmt(t_sat, 2)}</td>
            <td class="bg-v">{fmt(v_liq, 4)}</td>
            <td class="bg-v">{fmt(v_vap, 4)}</td>
            <td class="bg-v val-rho">{fmt(rho_vap, 3)}</td>
            <td class="bg-h">{fmt(h_liq, 1)}</td>
            <td class="bg-h">{fmt(h_vap, 1)}</td>
            <td class="bg-h"><b>{fmt(r, 1)}</b></td>
            <td>{fmt(s_liq, 4)}</td>
            <td>{fmt(s_vap, 4)}</td>
        </tr>
        """
        
    html += "</tbody></table></div></div>"
    return html

def generate_sat_t_table(fluid, title, fluid_name_display, t_range, theme="theme-green"):
    """Generate Saturation Table (Temperature based)."""
    
    html = f"""
    <div class="table-container {theme}">
        <div class="header-bar">
            <h3>{title}</h3>
            <p>Czynnik: {fluid_name_display}. Stan nasycenia (wg temperatury).</p>
        </div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th class="sticky-col">t<span class="unit">[°C]</span></th>
                        <th>p<sub>sat</sub><span class="unit">[kPa]</span></th>
                        <th class="bg-v">v'<span class="unit">[dm³/kg]</span></th>
                        <th class="bg-v">v''<span class="unit">[m³/kg]</span></th>
                        <th class="bg-v"><span class="val-rho">ρ''</span><span class="unit val-rho">[kg/m³]</span></th>
                        <th class="bg-h">h'<span class="unit">[kJ/kg]</span></th>
                        <th class="bg-h">h''<span class="unit">[kJ/kg]</span></th>
                        <th class="bg-h">r<span class="unit">[kJ/kg]</span></th>
                        <th>s'<span class="unit">[kJ/kgK]</span></th>
                        <th>s''<span class="unit">[kJ/kgK]</span></th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for t_c in t_range:
        # Props
        try:
            p_sat = get_prop(fluid, 'P', t=t_c, q=0) / 1000 # kPa
            v_liq = get_prop(fluid, 'D', t=t_c, q=0)**-1 * 1000
            v_vap = get_prop(fluid, 'D', t=t_c, q=1)**-1
            rho_vap = get_prop(fluid, 'D', t=t_c, q=1)
            h_liq = get_prop(fluid, 'H', t=t_c, q=0) / 1000
            h_vap = get_prop(fluid, 'H', t=t_c, q=1) / 1000
            r = h_vap - h_liq
            s_liq = get_prop(fluid, 'S', t=t_c, q=0) / 1000
            s_vap = get_prop(fluid, 'S', t=t_c, q=1) / 1000
        except:
            continue
            
        html += f"""
        <tr>
            <td class="sticky-col">{fmt(t_c, 1)}</td>
            <td>{fmt(p_sat, 3)}</td>
            <td class="bg-v">{fmt(v_liq, 4)}</td>
            <td class="bg-v">{fmt(v_vap, 4)}</td>
            <td class="bg-v val-rho">{fmt(rho_vap, 3)}</td>
            <td class="bg-h">{fmt(h_liq, 1)}</td>
            <td class="bg-h">{fmt(h_vap, 1)}</td>
            <td class="bg-h"><b>{fmt(r, 1)}</b></td>
            <td>{fmt(s_liq, 4)}</td>
            <td>{fmt(s_vap, 4)}</td>
        </tr>
        """
        
    html += "</tbody></table></div></div>"
    return html

def generate_superheated_table(fluid, title, fluid_name_display, p_range, t_range, theme="theme-red"):
    """Generate Superheated Table (Cross-tab: P cols x T rows)."""
    
    # Header row with Pressures
    header_cols = ""
    for p_bar in p_range:
        # Saturation temp for this pressure
        ts_val = get_prop(fluid, 'T', p=p_bar*1e5, q=1)
        
        if ts_val is not None:
            ts = ts_val - 273.15
            sub_text = f'(t<sub>s</sub>={fmt(ts, 2)}°C)'
        else:
            ts = None
            sub_text = '(Nadkryt.)'
            
        header_cols += f'<th colspan="3" style="border-bottom:1px solid #ddd">p = {fmt(p_bar, 3)} bar <br><span style="font-weight:normal">{sub_text}</span></th>'
        
    # Sub-header row (v, h, s)
    sub_header = ""
    for _ in p_range:
        sub_header += '<th class="bg-v">v</th><th class="bg-h">h</th><th>s</th>'
        
    html = f"""
    <div class="table-container {theme}">
        <div class="header-bar">
            <h3>{title}</h3>
            <p>Czynnik: {fluid_name_display}. Para Przegrzana.</p>
        </div>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr>
                        <th rowspan="2" class="sticky-col" style="z-index: 25;">t<span class="unit">[°C]</span></th>
                        {header_cols}
                    </tr>
                    <tr>
                        {sub_header}
                    </tr>
                </thead>
                <tbody>
    """
    
    # Rows (Temperatures)
    
    # 1. Saturation Line
    html += '<tr style="font-weight:bold; color:#a04000; background-color: #fff5e6"><td class="sticky-col">Stan nas.</td>'
    for p_bar in p_range:
        p_pa = p_bar * 1e5
        try:
            # Only generate saturation line properties if sub-critical
            if get_prop(fluid, 'T', p=p_pa, q=1) is None:
                 html += '<td colspan="3" style="font-weight:normal; font-size:0.9em">(Nadkryt.)</td>'
            else:
                v_vap = get_prop(fluid, 'D', p=p_pa, q=1)**-1
                h_vap = get_prop(fluid, 'H', p=p_pa, q=1) / 1000
                s_vap = get_prop(fluid, 'S', p=p_pa, q=1) / 1000
                html += f'<td class="bg-v">{fmt(v_vap, 4)}</td><td class="bg-h">{fmt(h_vap, 1)}</td><td>{fmt(s_vap, 4)}</td>'
        except:
             html += '<td colspan="3">—</td>'
    html += '</tr>'
    
    # 2. Temperature Rows
    for t_c in t_range:
        html += f'<tr><td class="sticky-col">{fmt(t_c, 0)}</td>'
        for p_bar in p_range:
            p_pa = p_bar * 1e5
            
            # Recalculate ts safely for logic
            ts_val = get_prop(fluid, 'T', p=p_pa, q=1)
            ts = ts_val - 273.15 if ts_val else None
            
            # If T < Tsat, it's liquid -> show dash (unless supercritical, then show value if valid)
            if ts is not None and t_c < ts:
                 html += '<td colspan="3" style="color:#ccc">—</td>'
            else:
                try:
                    # For supercritical, just calc properties at T, P
                    v = get_prop(fluid, 'D', t=t_c, p=p_pa)**-1
                    h = get_prop(fluid, 'H', t=t_c, p=p_pa) / 1000
                    s = get_prop(fluid, 'S', t=t_c, p=p_pa) / 1000
                    html += f'<td class="bg-v">{fmt(v, 4)}</td><td class="bg-h">{fmt(h, 1)}</td><td>{fmt(s, 4)}</td>'
                except:
                     html += '<td colspan="3">?</td>'
        html += '</tr>'

    html += "</tbody></table></div></div>"
    return html

def main():
    content = ""
    
    # --- 1. Water Saturation (Pressure) ---
    p_steps = []
    p_steps.extend(np.arange(0.001, 0.010, 0.001)) 
    p_steps.extend(np.arange(0.01, 0.10, 0.01))    
    p_steps.extend(np.arange(0.1, 1.0, 0.1))       
    p_steps.extend(np.arange(1.0, 22.1, 0.5))      
    p_bars_water = [x * 10 for x in p_steps] # MPa -> bar
    
    content += generate_sat_p_table("Water", "Tablica 1. Woda nasycona (wg ciśnienia)", "Woda (H₂O)", p_bars_water, "theme-blue")
    
    # --- 2. Water Saturation (Temperature) ---
    t_water = np.arange(0.01, 374, 1.0) 
    content += generate_sat_t_table("Water", "Tablica 2. Woda nasycona (wg temperatury)", "Woda (H₂O)", t_water, "theme-green")
    
    # --- 3. Water Superheated ---
    # Pressures: 0.1, 0.5, 1, 2, 5, 8, 10, 12, 15, 17, 20, 30, 40, 50, 70, 100, 120, 150, 200, 250 bar
    p_super_mpa = [0.01, 0.05, 0.1, 0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 1.7, 2.0, 3.0, 4.0, 5.0, 7.0, 10.0, 12.0, 15.0, 20.0, 25.0]
    p_super_bar = [x * 10 for x in p_super_mpa]
    t_super = np.arange(0, 801, 10.0)
    
    content += generate_superheated_table("Water", "Tablica 3. Para wodna przegrzana", "Woda (H₂O)", p_super_bar, t_super, "theme-red")

    # --- 4. R134a Saturation ---
    t_r134a = np.arange(-50, 101, 1.0)
    content += generate_sat_t_table("R134a", "Tablica 4. R134a nasycony (wg temperatury)", "R134a", t_r134a, "theme-cyan")
    
    p_r134a = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12, 14, 16, 18, 20, 25, 30, 35, 40]
    content += generate_sat_p_table("R134a", "Tablica 5. R134a nasycony (wg ciśnienia)", "R134a", p_r134a, "theme-cyan")

    # --- 5. R290 Saturation ---
    t_r290 = np.arange(-50, 96, 1.0)
    content += generate_sat_t_table("R290", "Tablica 6. R290 (Propan) nasycony (wg temperatury)", "R290 (Propan)", t_r290, "theme-orange")
    
    p_r290 = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12, 14, 16, 18, 20, 25, 30, 35, 40]
    content += generate_sat_p_table("R290", "Tablica 7. R290 (Propan) nasycony (wg ciśnienia)", "R290 (Propan)", p_r290, "theme-orange")
    
    # --- 6. R290 Superheated ---
    p_super_r290 = [1.0, 5.0, 15.0]
    t_super_r290 = np.arange(-50, 150, 10.0)
    content += generate_superheated_table("R290", "Tablica 8. R290 (Propan) przegrzany", "R290 (Propan)", p_super_r290, t_super_r290, "theme-orange")

    # Final HTML
    full_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Tablice Termodynamiczne</title>
{CSS}
</head>
<body>
<h1>Tablice Termodynamiczne</h1>
<p style="color: #666; font-size: 0.9em;">Wygenerowano automatycznie przy użyciu CoolProp (v{CoolProp.__version__}).</p>
{content}
</body>
</html>
"""
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(full_html)
        
    print(f"Generated {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
