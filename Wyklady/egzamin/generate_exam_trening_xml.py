#!/usr/bin/env python3
"""Generate Moodle XML files for training calculation questions.
- egzamin_zadania_trening.xml: calculated type with 50 dataset items (randomized)
Category: egzamin/trening
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os, random

random.seed(123) # different seed for training
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
NUM_DATASETS = 50

def write_xml(root, filename):
    raw = ET.tostring(root, encoding='unicode')
    dom = minidom.parseString(raw)
    xml_str = dom.toprettyxml(indent='    ', encoding=None)
    lines = [l for l in xml_str.split('\n') if not l.strip().startswith('<?xml')]
    content = "<?xml version='1.0' encoding='UTF-8'?>\n" + '\n'.join(lines)
    path = os.path.join(OUT_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {path}")

def gen_values(vmin, vmax, decimals, n=NUM_DATASETS):
    step = 10**(-decimals) if decimals > 0 else 1
    vals = []
    for _ in range(n):
        v = random.uniform(vmin, vmax)
        v = round(v / step) * step
        v = round(v, max(decimals, 0))
        vals.append(v)
    return vals

def add_dataset(parent, name, vmin, vmax, decimals, status='private'):
    dd = ET.SubElement(parent, 'dataset_definition')
    st = ET.SubElement(dd, 'status')
    ET.SubElement(st, 'text').text = status
    nm = ET.SubElement(dd, 'name')
    ET.SubElement(nm, 'text').text = name
    ET.SubElement(dd, 'type').text = 'calculated'
    dist = ET.SubElement(dd, 'distribution')
    ET.SubElement(dist, 'text').text = 'uniform'
    mn = ET.SubElement(dd, 'minimum')
    ET.SubElement(mn, 'text').text = str(vmin)
    mx = ET.SubElement(dd, 'maximum')
    ET.SubElement(mx, 'text').text = str(vmax)
    dec = ET.SubElement(dd, 'decimals')
    ET.SubElement(dec, 'text').text = str(decimals)
    ET.SubElement(dd, 'itemcount').text = str(NUM_DATASETS)
    ET.SubElement(dd, 'number_of_items').text = str(NUM_DATASETS)
    items_el = ET.SubElement(dd, 'dataset_items')
    values = gen_values(vmin, vmax, decimals)
    for i, v in enumerate(values, 1):
        di = ET.SubElement(items_el, 'dataset_item')
        ET.SubElement(di, 'number').text = str(i)
        if decimals == 0:
            ET.SubElement(di, 'value').text = str(int(v))
        else:
            ET.SubElement(di, 'value').text = f'{v:.{decimals}f}'

def add_calculated_question(quiz, name, html, feedback, formula, tolerance, grade, variables, tol_type=2):
    q = ET.SubElement(quiz, 'question', type='calculated')
    q_name = ET.SubElement(q, 'name')
    ET.SubElement(q_name, 'text').text = name
    q_qt = ET.SubElement(q, 'questiontext', format='html')
    ET.SubElement(q_qt, 'text').text = html
    q_gf = ET.SubElement(q, 'generalfeedback', format='html')
    ET.SubElement(q_gf, 'text').text = feedback
    ET.SubElement(q, 'defaultgrade').text = f'{grade:.7f}'
    ET.SubElement(q, 'penalty').text = '0.3333333'
    ET.SubElement(q, 'hidden').text = '0'
    ET.SubElement(q, 'idnumber')
    ET.SubElement(q, 'synchronize').text = '0'
    ET.SubElement(q, 'single').text = '0'
    ET.SubElement(q, 'answernumbering').text = 'abc'
    ET.SubElement(q, 'shuffleanswers').text = '0'
    for tag in ['correctfeedback', 'partiallycorrectfeedback', 'incorrectfeedback']:
        el = ET.SubElement(q, tag)
        ET.SubElement(el, 'text')

    a = ET.SubElement(q, 'answer', fraction='100')
    ET.SubElement(a, 'text').text = formula
    ET.SubElement(a, 'tolerance').text = str(tolerance)
    ET.SubElement(a, 'tolerancetype').text = str(tol_type)
    ET.SubElement(a, 'correctanswerformat').text = '1'
    ET.SubElement(a, 'correctanswerlength').text = '4'
    fb = ET.SubElement(a, 'feedback', format='html')
    ET.SubElement(fb, 'text')
    
    ET.SubElement(q, 'unitgradingtype').text = '0'
    ET.SubElement(q, 'unitpenalty').text = '0.1000000'
    ET.SubElement(q, 'showunits').text = '3'
    ET.SubElement(q, 'unitsleft').text = '0'
    
    dds = ET.SubElement(q, 'dataset_definitions')
    for vname, vmin, vmax, vdec in variables:
        add_dataset(dds, vname, vmin, vmax, vdec)

def make_trening():
    quiz = ET.Element('quiz')
    cat = ET.SubElement(quiz, 'question', type='category')
    cat_cat = ET.SubElement(cat, 'category')
    ET.SubElement(cat_cat, 'text').text = '$course$/top/egzamin/trening'
    cat_info = ET.SubElement(cat, 'info', format='moodle_auto_format')
    ET.SubElement(cat_info, 'text').text = 'Baza treningowa zadań obliczeniowych z rozwiązaniami krok po kroku.'

    tasks = [
        # T01: Ciśnienie
        ("Tr01_Cisnienie",
         "<p><b>Tr 1.</b> Manometr na zbiorniku z gazem wskazuje nadciśnienie <b>{p_man}</b> kPa. Ciśnienie otoczenia wynosi <b>{p_bar}</b> hPa. Oblicz ciśnienie absolutne gazu w zbiorniku.</p><p><b>Podaj p_abs [kPa]:</b></p>",
         "<div class='well'><b>Rozwiązanie — ciśnienie absolutne:</b><br/><b>1. Definicja:</b> Ciśnienie absolutne (bezwzględne) w zbiorniku to suma ciśnienia barometrycznego (otoczenia) i nadciśnienia wskazywanego przez manometr.<br/><b>2. Jednostki:</b> Manometr podaje nadciśnienie w kPa, barometr często w hPa. 1 hPa = 0,1 kPa, więc p_bar (hPa) w kPa to p_bar/10.<br/><b>3. Wzór:</b> \\( p_{abs} = p_{man} + p_{barometryczne} \\) (w tych samych jednostkach).<br/><b>4. Podstawienie:</b> \\( p_{abs} = {p_man} + \\frac{{p_bar}}{10} \\) kPa.</div>",
         "{p_man} + {p_bar}/10", 0.5, [("p_man", 150, 450, 0), ("p_bar", 980, 1030, 0)]),

        # T02: Clapeyron - masa
        ("Tr02_Clapeyron_m",
         "<p><b>Tr 2.</b> Oblicz masę azotu (\\(\\mu = 28{,}01\\) kg/kmol, R_u = 8314 J/(kmol·K)) w zbiorniku o objętości <b>{V}</b> m³. Temperatura gazu wynosi <b>{t}</b> °C, ciśnienie absolutne <b>{p}</b> bar.</p><p><b>Podaj m [kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie — równanie Clapeyrona (stan gazu):</b><br/><b>1. Równanie stanu:</b> \\( pV = mRT \\) (dla gazu doskonałego). Stąd \\( m = \\frac{pV}{RT} \\).<br/><b>2. Stała gazowa:</b> \\( R = R_u/\\mu \\) = 8314/28,01 ≈ 296,82 J/(kg·K).<br/><b>3. Jednostki:</b> p w Pa (1 bar = 10⁵ Pa), V w m³, T w K: T = {t} + 273,15. Wtedy m wyjdzie w kg.<br/><b>4. Podstawienie:</b> \\( m = \\frac{p \\cdot 10^5 \\cdot V}{296{,}82 \\cdot (t + 273{,}15)} \\) → \\( m = \\frac{{p} \\cdot 10^5 \\cdot {V}}{296{,}82 \\cdot ({t} + 273{,}15)} \\) kg.</div>",
         "({p} * 100000 * {V}) / (296.82 * ({t} + 273.15))", 0.5, [("V", 0.1, 2.0, 2), ("p", 1.5, 8.0, 1), ("t", 10, 50, 0)]),

        # T03: Izochora p2
        ("Tr03_Izochora",
         "<p><b>Tr 3.</b> W stalowej butli (V = const) znajduje się gaz pod ciśnieniem <b>{p1}</b> bar w temperaturze <b>{t1}</b> °C. Po nasłonecznieniu temperatura wzrosła do <b>{t2}</b> °C. Oblicz nowe ciśnienie.</p><p><b>Podaj p2 [bar]:</b></p>",
         "<div class='well'><b>Rozwiązanie — przemiana izochoryczna (prawo Charles’a):</b><br/><b>1. Założenie:</b> Objętość stała (V = const), masa gazu stała → stosunek p/T jest stały.<br/><b>2. Prawo Charles’a:</b> \\( \\frac{p_1}{T_1} = \\frac{p_2}{T_2} \\). Temperatury muszą być w kelwinach (T = t + 273,15).<br/><b>3. Wyznaczenie p₂:</b> \\( p_2 = p_1 \\cdot \\frac{T_2}{T_1} = p_1 \\cdot \\frac{t_2 + 273{,}15}{t_1 + 273{,}15} \\).<br/><b>4. Podstawienie:</b> \\( p_2 = {p1} \\cdot \\frac{{t2} + 273{,}15}{{t1} + 273{,}15} \\) bar. Jednostka ciśnienia (bar) zachowana.</div>",
         "{p1} * ({t2} + 273.15) / ({t1} + 273.15)", 0.2, [("p1", 10, 200, 0), ("t1", 5, 25, 0), ("t2", 40, 80, 0)]),

        # T04: Praca izobaryczna
        ("Tr04_PracaIzobara",
         "<p><b>Tr 4.</b> Powietrze jest ogrzewane w cylindrze pod stałym tłokiem (p = <b>{p}</b> bar = const). Objętość rośnie z <b>{V1}</b> m³ do <b>{V2}</b> m³. Oblicz wykonaną pracę objętościową gazu.</p><p><b>Podaj L [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie — praca objętościowa w przemianie izobarycznej:</b><br/><b>1. Definicja pracy:</b> Przy stałym ciśnieniu \\( L = \\int p\\,dV = p(V_2 - V_1) \\).<br/><b>2. Jednostki:</b> p w Pa, V w m³ → L w J. Aby otrzymać L w kJ: p w bar × 100 = p w kPa, wtedy L = p [bar] · 100 · (V₂ − V₁) [m³] daje kJ.<br/><b>3. Podstawienie:</b> \\( L = {p} \\cdot 100 \\cdot ({V2} - {V1}) \\) kJ. Wynik dodatni — gaz wykonuje pracę przy rozprężaniu.</div>",
         "{p} * 100 * ({V2} - {V1})", 2, [("p", 1, 10, 1), ("V1", 0.1, 1.0, 2), ("V2", 1.2, 3.0, 2)]),

        # T05: Energia wewnętrzna
        ("Tr05_DeltaU",
         "<p><b>Tr 5.</b> <b>{m}</b> kg azotu (\\(c_v\\) = 0,743 kJ/(kg·K)) podgrzano z <b>{t1}</b> °C do <b>{t2}</b> °C. Oblicz przyrost energii wewnętrznej gazu.</p><p><b>Podaj ΔU [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie — przyrost energii wewnętrznej gazu doskonałego:</b><br/><b>1. Właściwość gazu doskonałego:</b> Energia wewnętrzna U zależy tylko od temperatury. Zmiana: \\( \\Delta U = m \\cdot c_v \\cdot (T_2 - T_1) \\).<br/><b>2. Ciepło właściwe:</b> c_v = 0,743 kJ/(kg·K) dla azotu (przy stałej objętości).<br/><b>3. Różnica temperatur:</b> (T₂ − T₁) w kelwinach jest liczbowo równa (t₂ − t₁) w °C, więc można podstawiać temperatury w °C.<br/><b>4. Jednostki:</b> m [kg], c_v [kJ/(kg·K)], ΔT [K] → ΔU w kJ.<br/><b>5. Podstawienie:</b> \\( \\Delta U = {m} \\cdot 0{,}743 \\cdot ({t2} - {t1}) \\) kJ.</div>",
         "{m} * 0.743 * ({t2} - {t1})", 2, [("m", 1.0, 5.0, 1), ("t1", 10, 40, 0), ("t2", 100, 300, 0)]),

        # T06: Entalpia gazu
        ("Tr06_DeltaH",
         "<p><b>Tr 6.</b> <b>{m}</b> kg tlenu (\\(c_p\\) = 0,918 kJ/(kg·K)) schłodzono izobarycznie z <b>{t1}</b> °C do <b>{t2}</b> °C. Oblicz zmianę entalpii układu (uwzględnij znak).</p><p><b>Podaj ΔH [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie — zmiana entalpii przy procesie izobarycznym:</b><br/><b>1. Definicja entalpii:</b> Dla gazu doskonałego przy stałym ciśnieniu \\( \\Delta H = m \\cdot c_p \\cdot (T_2 - T_1) \\).<br/><b>2. Ciepło właściwe:</b> c_p = 0,918 kJ/(kg·K) dla tlenu (przy stałym ciśnieniu).<br/><b>3. Znak:</b> Przy chłodzeniu t₂ &lt; t₁, więc (t₂ − t₁) &lt; 0 — zmiana entalpii jest ujemna (entalpia maleje). Podaj wynik ze znakiem.<br/><b>4. Jednostki:</b> m [kg], c_p [kJ/(kg·K)], ΔT [K lub °C] → ΔH w kJ.<br/><b>5. Podstawienie:</b> \\( \\Delta H = {m} \\cdot 0{,}918 \\cdot ({t2} - {t1}) \\) kJ.</div>",
         "{m} * 0.918 * ({t2} - {t1})", 2, [("m", 2.0, 8.0, 1), ("t1", 200, 400, 0), ("t2", 20, 80, 0)]),

        # T07: Dysza c2
        ("Tr07_Dysza",
         "<p><b>Tr 7.</b> Para wodna przepływa przez dyszę adiabatyczną. Entalpia na wlocie wynosi <b>{h1}</b> kJ/kg, na wylocie <b>{h2}</b> kJ/kg. Prędkość strugi na wlocie wynosi <b>{c1}</b> m/s. Oblicz prędkość pary na wylocie dyszy.</p><p><b>Podaj c₂ [m/s]:</b></p>",
         "<div class='well'><b>Rozwiązanie — dysza adiabatyczna (bilans energii):</b><br/><b>1. Założenia:</b> Przepływ ustalony, brak pracy mechanicznej, brak wymiany ciepła (dysza adiabatyczna). Bilans energii (entalpia + energia kinetyczna): \\( h_1 + \\frac{c_1^2}{2} = h_2 + \\frac{c_2^2}{2} \\) w jednostkach kJ/kg.<br/><b>2. Jednostki:</b> h w kJ/kg, c w m/s. \\( c^2/2 \\) w (m/s)² daje J/kg = 10⁻³ kJ/kg. Aby dodać do h [kJ/kg], piszemy \\( \\frac{c^2}{2000} \\) (bo 1 (m/s)² = 10⁻³ kJ/kg → c²/2 w kJ/kg to c²/2000).<br/><b>3. Przekształcenie:</b> \\( \\frac{c_2^2}{2000} = h_1 - h_2 + \\frac{c_1^2}{2000} \\), więc \\( c_2 = \\sqrt{2000(h_1 - h_2) + c_1^2} \\).<br/><b>4. Podstawienie:</b> \\( c_2 = \\sqrt{2000 \\cdot ({h1} - {h2}) + {c1}^2} \\) m/s.</div>",
         "pow(2000 * ({h1} - {h2}) + {c1}*{c1}, 0.5)", 2, [("h1", 3000, 3300, 0), ("h2", 2800, 2950, 0), ("c1", 30, 60, 0)]),

        # T08: Moc turbiny (uproszczona)
        ("Tr08_MocTurbiny",
         "<p><b>Tr 8.</b> Przez turbinę parową przepływa <b>{mdot}</b> kg/s czynnika. Entalpia pary na wlocie wynosi <b>{h1}</b> kJ/kg, na wylocie <b>{h2}</b> kJ/kg. Pominąć zmiany energii kinetycznej i potencjalnej. Oblicz moc turbiny adiabatycznej.</p><p><b>Podaj P [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie — moc turbiny (I zasada dla przepływu):</b><br/><b>1. Bilans energii:</b> Dla przepływu ustalonego przez turbinę adiabatyczną, przy zaniedbaniu zmian energii kinetycznej i potencjalnej: moc na wale \\( P = \\dot{m}(h_1 - h_2) \\). Ciepło nie jest wymieniane (adiabatyczna).<br/><b>2. Znaczenie:</b> Różnica entalpii (h₁ − h₂) to energia odbierana od czynnika na kg; mnożona przez strumień masy daje moc w kW, gdy \\( \\dot{m} \\) w kg/s, h w kJ/kg.<br/><b>3. Podstawienie:</b> \\( P = {mdot} \\cdot ({h1} - {h2}) \\) kW.</div>",
         "{mdot} * ({h1} - {h2})", 2, [("mdot", 10, 50, 1), ("h1", 3300, 3450, 0), ("h2", 2300, 2500, 0)]),

        # T09: Moc sprężarki
        ("Tr09_MocSprezarki",
         "<p><b>Tr 9.</b> Sprężarka adiabatyczna zasysa <b>{mdot}</b> kg/s gazu. Przyrost entalpii gazu wynosi <b>{dh}</b> kJ/kg. Oblicz wymaganą moc napędową doprowadzoną do wału.</p><p><b>Podaj P [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie — moc sprężarki (I zasada dla przepływu):</b><br/><b>1. Bilans energii:</b> W sprężarce adiabatycznej praca jest doprowadzana do gazu; przyrost entalpii czynnika \\( \\Delta h = h_2 - h_1 \\) [kJ/kg] wynika z pracy na wale. Moc napędowa \\( P = \\dot{m} \\cdot \\Delta h \\).<br/><b>2. Jednostki:</b> \\( \\dot{m} \\) [kg/s], Δh [kJ/kg] → P [kW]. Zadanie podaje już przyrost entalpii Δh.<br/><b>3. Podstawienie:</b> \\( P = {mdot} \\cdot {dh} \\) kW.</div>",
         "{mdot} * {dh}", 2, [("mdot", 1.5, 6.0, 1), ("dh", 150, 350, 0)]),

        # T10: Wymiennik Q
        ("Tr10_WymiennikWoda",
         "<p><b>Tr 10.</b> W wymienniku ciepła płynie woda (\\(c_w\\) = 4,19 kJ/(kg·K)) ze strumieniem <b>{mdot}</b> kg/s. Woda ogrzewa się z <b>{t1}</b> °C do <b>{t2}</b> °C. Oblicz strumień ciepła przejmowanego przez wodę.</p><p><b>Podaj Q [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie — strumień ciepła w wymienniku (ogrzewanie wody):</b><br/><b>1. Bilans ciepła:</b> Ciepło przejmowane przez wodę przy ogrzewaniu: \\( \\dot{Q} = \\dot{m} \\cdot c_w \\cdot (T_2 - T_1) \\). Strumień masy \\( \\dot{m} \\) [kg/s], ciepło właściwe c_w [kJ/(kg·K)], różnica temperatur w K lub °C.<br/><b>2. Jednostki:</b> \\( \\dot{m} \\) [kg/s], c_w = 4,19 kJ/(kg·K), (t₂ − t₁) [K] → \\( \\dot{Q} \\) w kW.<br/><b>3. Podstawienie:</b> \\( \\dot{Q} = {mdot} \\cdot 4{,}19 \\cdot ({t2} - {t1}) \\) kW.</div>",
         "{mdot} * 4.19 * ({t2} - {t1})", 2, [("mdot", 0.5, 3.0, 2), ("t1", 15, 30, 0), ("t2", 60, 95, 0)]),

        # T11: Sprawnosc termiczna
        ("Tr11_SprawnoscT",
         "<p><b>Tr 11.</b> W jednym cyklu silnik pobiera ze źródła <b>{Qin}</b> kJ ciepła i odprowadza do otoczenia <b>{Qout}</b> kJ. Oblicz sprawność termiczną silnika.</p><p><b>Podaj (eta_t) [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — sprawność termiczna silnika:</b><br/><b>1. Definicja sprawności:</b> \\( \\eta = \\frac{L}{Q_{in}} \\), gdzie L — praca netto wykonana w cyklu, Q_in — ciepło pobrane ze źródła.<br/><b>2. Bilans energii (I zasada):</b> W cyklu \\( Q_{in} - Q_{out} = L \\) (ciepło oddane Q_out do otoczenia). Stąd \\( L = Q_{in} - Q_{out} \\).<br/><b>3. Postać sprawności:</b> \\( \\eta = \\frac{Q_{in} - Q_{out}}{Q_{in}} = 1 - \\frac{Q_{out}}{Q_{in}} \\). Wartość ułamkowa (0–1).<br/><b>4. Podstawienie:</b> \\( \\eta = 1 - \\frac{{Qout}}{{Qin}} \\).</div>",
         "1 - ({Qout}/{Qin})", 0.01, [("Qin", 1500, 3000, 0), ("Qout", 900, 1200, 0)]),

        # T12: Carnot ETA
        ("Tr12_Carnot",
         "<p><b>Tr 12.</b> Idealnie odwracalny silnik pracuje cyklem Carnota między <b>{TH}</b> °C i <b>{TL}</b> °C. Oblicz sprawność tego silnika.</p><p><b>Podaj eta_C [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — sprawność obiegu Carnota:</b><br/><b>1. Wzór Carnota:</b> Dla silnika odwracalnego pracującego między źródłem górnym (T_H) a dolnym (T_L): \\( \\eta_C = 1 - \\frac{T_L}{T_H} \\). Temperatury muszą być w kelwinach.<br/><b>2. Jednostki:</b> T [K] = t [°C] + 273,15. Sprawność jest liczbą niemianowaną (0–1).<br/><b>3. Podstawienie:</b> \\( \\eta_C = 1 - \\frac{{TL} + 273{,}15}{{TH} + 273{,}15} \\).</div>",
         "1 - ({TL}+273.15)/({TH}+273.15)", 0.01, [("TH", 500, 950, 0), ("TL", 15, 45, 0)]),

        # T13: COP_chlodziarki
        ("Tr13_ChlodziarkaCOP",
         "<p><b>Tr 13.</b> Oblicz maksymalny teoretyczny współczynnik COP chłodziarki, która chłodzi wnętrze o temperaturze <b>{TL}</b> °C, oddając ciepło do otoczenia o temperaturze <b>{TH}</b> °C.</p><p><b>Podaj COP [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — COP chłodziarki (Carnot):</b><br/><b>1. Definicja COP:</b> Współczynnik wydajności chłodniczej \\( COP = \\frac{\\dot{Q}_L}{P} \\) — stosunek ciepła odbieranego z wnętrza do pracy sprężarki. Dla obiegu Carnota: \\( COP = \\frac{T_L}{T_H - T_L} \\) (T w kelwinach).<br/><b>2. Znaczenie:</b> T_L — temp. zimnego źródła (wnętrze), T_H — temp. otoczenia. Im mniejsza różnica T_H − T_L, tym wyższy COP.<br/><b>3. Jednostki:</b> T = t + 273,15 [K]. Wynik niemianowany.<br/><b>4. Podstawienie:</b> \\( COP = \\frac{{TL} + 273{,}15}{({TH} + 273{,}15) - ({TL} + 273{,}15)} = \\frac{{TL} + 273{,}15}{{TH} - {TL}} \\).</div>",
         "({TL} + 273.15) / ({TH} - {TL})", 0.1, [("TL", -25, -5, 0), ("TH", 20, 40, 0)]),

        # T14: COP_PC
        ("Tr14_PompaCieplaCOP",
         "<p><b>Tr 14.</b> Pompa ciepła pozyskuje energię z dolnego źródła (grunt) o temperaturze <b>{TL}</b> °C i oddaje ciepło do systemu grzewczego o temperaturze <b>{TH}</b> °C. Oblicz maksymalny teoretyczny COP (wg Carnota) tej pompy ciepła.</p><p><b>Podaj COP_PC [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — COP pompy ciepła (Carnot):</b><br/><b>1. Definicja COP pompy ciepła:</b> \\( COP_{PC} = \\frac{\\dot{Q}_H}{P} \\) — stosunek ciepła oddanego do ogrzewania do pracy napędowej. Dla obiegu Carnota: \\( COP_{PC} = \\frac{T_H}{T_H - T_L} \\) (T w kelwinach).<br/><b>2. Związek z COP chłodziarki:</b> \\( COP_{PC} = COP_{chłodziarki} + 1 \\), bo to ten sam obieg — pompa „przenosi” ciepło z T_L do T_H i oddaje więcej niż pobiera pracę.<br/><b>3. Jednostki:</b> T = t + 273,15 [K]. Wynik niemianowany, zwykle &gt; 1.<br/><b>4. Podstawienie:</b> \\( COP_{PC} = \\frac{{TH} + 273{,}15}{{TH} - {TL}} \\) (mianownik w °C: TH − TL).</div>",
         "({TH} + 273.15) / ({TH} - {TL})", 0.1, [("TH", 35, 50, 0), ("TL", -5, 12, 0)]),

        # T15: Izentropa p2
        ("Tr15_IzentropaGaz",
         "<p><b>Tr 15.</b> Powietrze (\\(\\kappa = 1,4\\)) rozprężono izentropowo. Ciśnienie początkowe wynosi <b>{p1}</b> bar, temperatura początkowa <b>{T1}</b> °C. Temperatura po rozprężeniu wynosi <b>{T2}</b> °C. Oblicz ciśnienie końcowe.</p><p><b>Podaj p2 [bar]:</b></p>",
         "<div class='well'><b>Rozwiązanie — przemiana izentropowa (wyznaczenie p₂ z T₂):</b><br/><b>1. Zależność T–p w izentropie:</b> Dla gazu doskonałego \\( \\frac{T_2}{T_1} = \\left(\\frac{p_2}{p_1}\\right)^{(\\kappa-1)/\\kappa} \\). Stąd \\( \\frac{p_2}{p_1} = \\left(\\frac{T_2}{T_1}\\right)^{\\kappa/(\\kappa-1)} \\) i \\( p_2 = p_1 \\cdot (T_2/T_1)^{\\kappa/(\\kappa-1)} \\). Temperatury w kelwinach.<br/><b>2. Wykładnik:</b> Dla powietrza κ = 1,4: κ/(κ−1) = 1,4/0,4 = 3,5.<br/><b>3. Podstawienie:</b> \\( p_2 = {p1} \\cdot \\left( \\frac{{T2}+273{,}15}{{T1}+273{,}15} \\right)^{3{,}5} \\) bar.</div>",
         "{p1} * pow(({T2}+273.15)/({T1}+273.15), 3.5)", 0.2, [("p1", 8, 25, 1), ("T1", 300, 500, 0), ("T2", -20, 50, 0)]),

        # T16: Izoterma L
        ("Tr16_IzotermaL",
         "<p><b>Tr 16.</b> W procesie sprężania izotermicznego <b>{m}</b> kg gazu doskonałego (R = <b>{R}</b> J/(kg·K)) ciśnienie rośnie z <b>{p1}</b> bar do <b>{p2}</b> bar przy stałej temperaturze <b>{t}</b> °C. Oblicz pracę sprężania (wartość bezwzględną w kJ).</p><p><b>Podaj L [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie — praca sprężania izotermicznego:</b><br/><b>1. Praca w przemianie izotermicznej:</b> \\( L = m R T \\ln\\frac{V_2}{V_1} = m R T \\ln\\frac{p_1}{p_2} \\) (z pV = const). Przy sprężaniu p₂ &gt; p₁, więc ln(p₁/p₂) &lt; 0 — praca doprowadzona (ujemna z konwencji „praca gazu”). Podaj wartość bezwzględną.<br/><b>2. Jednostki:</b> R podane w J/(kg·K) → R/1000 w kJ/(kg·K). T = t + 273,15 [K]. m [kg] → L w kJ.<br/><b>3. Podstawienie:</b> \\( L = {m} \\cdot \\frac{{R}}{1000} \\cdot ({t}+273{,}15) \\cdot \\ln\\frac{{p1}}{{p2}} \\). Wynik ujemny — weź wartość bezwzględną.</div>",
         "{m} * ({R}/1000) * ({t}+273.15) * log({p1}/{p2})", 2, [("m", 1.0, 5.0, 1), ("R", 200, 350, 0), ("p1", 1, 3, 1), ("p2", 8, 20, 1), ("t", 15, 60, 0)]),

        # T17: Mieszanina udział masowy
        ("Tr17_MieszUdziałyMo",
         "<p><b>Tr 17.</b> W butli wymieszano <b>{m1}</b> kg tlenu O₂ z <b>{m2}</b> kg dwutlenku węgla CO₂. Oblicz udział masowy tlenu w procentach (np. 54,3%).</p><p><b>Podaj g_O2 [%]:</b></p>",
         "<div class='well'><b>Rozwiązanie — udział masowy w mieszaninie gazów:</b><br/><b>1. Definicja udziału masowego:</b> Udział masowy składnika 1 to \\( g_1 = \\frac{m_1}{m_1 + m_2} \\) (jako ułamek) lub \\( g_1 = \\frac{m_1}{m_1 + m_2} \\cdot 100\\% \\) w procentach.<br/><b>2. Tutaj:</b> Składnik 1 = tlen O₂, składnik 2 = CO₂. Szukamy g_O₂ [%].<br/><b>3. Podstawienie:</b> \\( g_{O_2} = \\frac{{m1}}{{m1} + {m2}} \\cdot 100 \\) %.</div>",
         "100 * {m1} / ({m1} + {m2})", 0.5, [("m1", 2.0, 10.0, 1), ("m2", 2.0, 10.0, 1)]),

        # T18: Para mokra X
        ("Tr18_ParaStopien",
         "<p><b>Tr 18.</b> W zbiorniku para mokra ma masę całkowitą <b>{m_calkowita}</b> kg, z czego faza ciekła stanowi <b>{m_woda}</b> kg. Oblicz stopień suchości pary (jako ułamek, np. 0,53).</p><p><b>Podaj x [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — stopień suchości pary mokrej:</b><br/><b>1. Definicja stopnia suchości:</b> \\( x = \\frac{m''}{m} \\) — stosunek masy pary nasyconej suchej (m″) do całkowitej masy mieszaniny (para + ciecz). Masa fazy ciekłej m′ = m − m″, więc \\( x = \\frac{m - m'}{m} = 1 - \\frac{m'}{m} \\).<br/><b>2. W zadaniu:</b> m_calkowita = m, m_woda = m′ (faza ciekła).<br/><b>3. Podstawienie:</b> \\( x = 1 - \\frac{{m_woda}}{{m_calkowita}} \\). Wynik jako ułamek (0 &lt; x &lt; 1).</div>",
         "1 - ({m_woda}/{m_calkowita})", 0.01, [("m_calkowita", 10, 50, 1), ("m_woda", 1.0, 8.0, 1)]),

        # T19: Zawilżenie X
        ("Tr19_ZawilzeniePw",
         "<p><b>Tr 19.</b> Na podstawie pomiaru psychrometrem Assmanna wyznaczono ciśnienie cząstkowe pary wodnej <b>{pw}</b> hPa przy ciśnieniu barometrycznym <b>{pB}</b> hPa. Oblicz zawilżenie absolutne powietrza X.</p><p><b>Podaj X [g/kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie — zawilżenie absolutne powietrza (X):</b><br/><b>1. Definicja:</b> Zawilżenie X [g/kg] to masa pary wodnej na 1 kg powietrza suchego. Z równania stanu i stosunku stałych gazowych (powietrze/para): \\( X = 622 \\cdot \\frac{p_w}{p_B - p_w} \\), gdzie p_w — ciśnienie cząstkowe pary, p_B — ciśnienie barometryczne (w tych samych jednostkach).<br/><b>2. Jednostki:</b> p_w i p_B w hPa → X w g/kg (współczynnik 622 przy założeniu R_powietrza/R_pary ≈ 0,622).<br/><b>3. Podstawienie:</b> \\( X = 622 \\cdot \\frac{{pw}}{{pB} - {pw}} \\) g/kg.</div>",
         "622 * {pw} / ({pB} - {pw})", 0.5, [("pw", 5, 25, 1), ("pB", 950, 1050, 0)]),

        # T20: Mieszanie powietrza (reguła dźwigni)
        ("Tr20_RegulaDzwigniPowietrza",
         "<p><b>Tr 20.</b> W centrali wentylacyjnej miesza się <b>{m1}</b> kg/s powietrza zewnętrznego o temperaturze −<b>{t1_ujemna}</b> °C ze <b>{m2}</b> kg/s powietrza wywiewanego o temperaturze <b>{t2}</b> °C. Oblicz temperaturę powietrza po zmieszaniu (nawiew).</p><p><b>Podaj T_miesz [°C]:</b></p><p><i>Uwaga: t₁ = −{t1_ujemna} °C (wartość ujemna).</i></p>",
         "<div class='well'><b>Rozwiązanie — temperatura mieszaniny (bilans energii):</b><br/><b>1. Bilans przy mieszaniu:</b> Przy mieszaniu dwóch strumieni powietrza (bez wymiany ciepła z otoczeniem) \\( m_1 t_1 + m_2 t_2 = (m_1 + m_2) t_M \\), więc \\( t_M = \\frac{m_1 t_1 + m_2 t_2}{m_1 + m_2} \\). Temperatury w °C (dla powietrza przy niewielkiej zmianie c_p dopuszczalne).<br/><b>2. Znaki:</b> Powietrze zewnętrzne ma t₁ = −{t1_ujemna} °C (ujemne), więc w wzorze: t₁ = −t1_ujemna.<br/><b>3. Podstawienie:</b> \\( t_M = \\frac{{m1} \\cdot (-{t1_ujemna}) + {m2} \\cdot {t2}}{{m1} + {m2}} \\) °C.</div>",
         "({m1} * (-{t1_ujemna}) + {m2} * {t2}) / ({m1} + {m2})", 0.5, [("m1", 2, 8, 1), ("t1_ujemna", 5, 25, 0), ("m2", 5, 12, 1), ("t2", 15, 25, 0)]),

        # T21: Ściana — współczynnik U
        ("Tr21_ScianaU",
         "<p><b>Tr 21.</b> Jednowarstwowa ściana płaska z betonu zbrojonego ma grubość <b>{d_cm}</b> cm i współczynnik przewodzenia \\(\\lambda\\) = <b>{lam}</b> W/(m·K). Współczynniki przejmowania ciepła: od zewnątrz \\(\\alpha_1\\) = <b>{a1}</b> W/(m²·K), od wewnątrz \\(\\alpha_2\\) = <b>{a2}</b> W/(m²·K). Oblicz współczynnik przenikania ciepła U.</p><p><b>Podaj U [W/(m²K)]:</b></p>",
         "<div class='well'><b>Rozwiązanie — współczynnik przenikania ciepła U:</b><br/><b>1. Opór całkowity:</b> Przenikanie przez ścianę: opór konwekcji zewnętrznej + opór przewodzenia + opór konwekcji wewnętrznej. \\( \\frac{1}{U} = R_{tot} = \\frac{1}{\\alpha_1} + \\frac{\\delta}{\\lambda} + \\frac{1}{\\alpha_2} \\). Stąd \\( U = 1/R_{tot} \\) [W/(m²·K)].<br/><b>2. Jednostki:</b> δ w m (d_cm/100), λ [W/(m·K)], α [W/(m²·K)].<br/><b>3. Podstawienie:</b> \\( \\frac{1}{U} = \\frac{1}{{a1}} + \\frac{{d_cm}/100}{{lam}} + \\frac{1}{{a2}} \\), następnie U = 1 / (prawa strona).</div>",
         "1 / ((1/{a1}) + ({d_cm}/100/{lam}) + (1/{a2}))", 0.1, [("d_cm", 15, 40, 0), ("lam", 0.8, 2.5, 2), ("a1", 10, 30, 0), ("a2", 5, 12, 0)]),

        # T22: Otto Eta
        ("Tr22_ObiegOtto",
         "<p><b>Tr 22.</b> Oblicz sprawność idealnego obiegu Otto przy stopniu sprężania objętościowym \\(\\varepsilon = V_1/V_2\\) = <b>{eps}</b>. Gaz doskonały, \\(\\kappa\\) = 1,4 (np. powietrze).</p><p><b>Podaj eta [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — sprawność obiegu Otto:</b><br/><b>1. Obieg Otto:</b> Składa się z izentropy sprężania, izochorycznego doprowadzenia ciepła, izentropy rozprężania i izochorycznego odbioru ciepła. Dla gazu doskonałego ze stałym κ sprawność zależy tylko od stopnia sprężania ε = V₁/V₂.<br/><b>2. Wzór:</b> \\( \\eta = 1 - \\frac{1}{\\varepsilon^{\\kappa-1}} \\). Dla powietrza κ = 1,4: κ−1 = 0,4.<br/><b>3. Podstawienie:</b> \\( \\eta = 1 - \\frac{1}{{eps}^{0{,}4}} \\). Wynik jako ułamek (0–1).</div>",
         "1 - 1 / pow({eps}, 0.4)", 0.01, [("eps", 7.0, 11.5, 1)]),

        # T23: Entalpia powietrza wilgotnego
        ("Tr23_EntalpiaPowwilg",
         "<p><b>Tr 23.</b> Oblicz entalpię powietrza wilgotnego o temperaturze <b>{t}</b> °C i zawilżeniu <b>{X}</b> g/kg (entalpia odniesiona do 1 kg powietrza suchego).</p><p><b>Podaj h [kJ/kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie — entalpia powietrza wilgotnego:</b><br/><b>1. Entalpia odniesiona do 1 kg powietrza suchego:</b> \\( h = c_{p,pow}\\,t + X \\cdot (r_0 + c_{p,para}\\,t) \\), gdzie X [kg/kg] — zawilżenie. W praktyce X podaje się w g/kg; wtedy \\( h \\approx 1{,}005\\,t + \\frac{X}{1000}(2500 + 1{,}86\\,t) \\) kJ/kg, czyli \\( h \\approx 1{,}005\\,t + X\\cdot(2{,}5 + 0{,}00186\\,t) \\) gdy X w g/kg (2500 ≈ ciepło parowania przy 0°C w kJ/kg).<br/><b>2. Jednostki:</b> t [°C], X [g/kg] → h [kJ/kg].<br/><b>3. Podstawienie:</b> \\( h = 1{,}005 \\cdot {t} + {X} \\cdot (2{,}5 + 0{,}00186 \\cdot {t}) \\) kJ/kg.</div>",
         "1.005 * {t} + {X} * (2.5 + 0.00186 * {t})", 1.0, [("t", 20, 35, 1), ("X", 5.0, 15.0, 1)]),

        # T24: Zapotrzebowanie tlenu O₂
        ("Tr24_SpalanieO2",
         "<p><b>Tr 24.</b> W procesie spalania stechiometrycznego spalono <b>{m_c}</b> kg węgla (C). Oblicz masę tlenu O₂ zużytego do całkowitego spalenia do CO₂.</p><p><b>Podaj M_O2 [kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/><b>1. Reakcja i stechiometria:</b> C + O₂ → CO₂. Z równania: 1 mol C (12 kg) wymaga 1 mola O₂ (32 kg).<br/><b>2. Proporcja mas:</b> \\( m_{O_2}/m_C = 32/12 \\), więc \\( m_{O_2} = m_C \\cdot 32/12 \\).<br/><b>3. Jednostki:</b> masa węgla w kg → wynik w kg.<br/><b>4. Podstawienie:</b> \\( m_{O_2} = \\frac{{m_c}}{12} \\cdot 32 \\) kg.</div>",
         "({m_c} / 12) * 32", 0.5, [("m_c", 5, 25, 1)]),

        # T25: Ściana — gęstość strumienia q
        ("Tr25_PrzewScianaQ",
         "<p><b>Tr 25.</b> Przez płaską warstwę o grubości <b>{d}</b> cm i współczynniku przewodzenia \\(\\lambda\\) = <b>{lam}</b> W/(m·K) przenika ciepło. Temperatura po stronie wewnętrznej wynosi <b>{t1}</b> °C, po zewnętrznej <b>{t2}</b> °C. Oblicz gęstość strumienia ciepła (prawo Fouriera, bez oporów przejmowania).</p><p><b>Podaj q [W/m²]:</b></p>",
         "<div class='well'><b>Rozwiązanie — gęstość strumienia ciepła (prawo Fouriera):</b><br/><b>1. Prawo Fouriera:</b> Dla ustalonego przewodzenia przez warstwę płaską \\( q = \\frac{\\lambda}{\\delta}(T_1 - T_2) \\) [W/m²], gdzie λ — współczynnik przewodzenia, δ — grubość warstwy, T₁, T₂ — temperatury powierzchni. Nie uwzględniamy tu oporów przejmowania (alfa).<br/><b>2. Jednostki:</b> δ w m (d [cm] → d/100), λ [W/(m·K)], T w K lub °C (różnica taka sama).<br/><b>3. Podstawienie:</b> \\( q = \\frac{{lam}}{{d}/100} \\cdot ({t1} - {t2}) \\) W/m².</div>",
         "({lam} / ({d}/100)) * ({t1} - {t2})", 2.0, [("t1", 20, 90, 0), ("t2", -10, 5, 0), ("d", 5, 20, 1), ("lam", 0.04, 0.20, 2)]),

        # T26: Chłodnica (wymiennik ciepła)
        ("Tr26_KondesatCieplo",
         "<p><b>Tr 26.</b> W chłodnicy ciecz o strumieniu masy <b>{m}</b> kg/s i cieple właściwym <b>{c}</b> kJ/(kg·K) ochładza się z <b>{t1}</b> °C do <b>{t2}</b> °C. Oblicz strumień ciepła odprowadzonego w chłodnicy (moc w kW).</p><p><b>Podaj Q [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie — strumień ciepła w chłodnicy (wymiennik):</b><br/><b>1. Bilans ciepła:</b> Ciecz ochładza się z t₁ do t₂, oddając ciepło do chłodnicy. Strumień ciepła odprowadzonego (moc): \\( \\dot{Q} = \\dot{m} \\cdot c \\cdot (t_1 - t_2) \\) — przy spadku temperatury (t₁ &gt; t₂) wynik dodatni [kW].<br/><b>2. Jednostki:</b> \\( \\dot{m} \\) [kg/s], c [kJ/(kg·K)], (t₁ − t₂) [K lub °C] → \\( \\dot{Q} \\) [kW].<br/><b>3. Podstawienie:</b> \\( \\dot{Q} = {m} \\cdot {c} \\cdot ({t1} - {t2}) \\) kW.</div>",
         "{m} * {c} * ({t1} - {t2})", 2.0, [("t1", 80, 130, 0), ("t2", 40, 70, 0), ("m", 0.5, 4.0, 1), ("c", 2.0, 2.5, 2)]),

        # T27: Praca cyklu Carnota
        ("Tr27_PracaCarnotaQ",
         "<p><b>Tr 27.</b> Silnik Carnota pracuje między temperaturą źródła górnego <b>{tH}</b> °C a temperaturą skraplacza <b>{tL}</b> °C. Do skraplacza odprowadzane jest <b>{Qout}</b> MW ciepła. Oblicz pracę netto cyklu w MW.</p><p><b>Podaj L [MW]:</b></p>",
         "<div class='well'><b>Rozwiązanie — praca netto cyklu Carnota:</b><br/><b>1. Stosunek ciepła w Carnota:</b> Dla obiegu odwracalnego \\( \\frac{Q_H}{Q_L} = \\frac{T_H}{T_L} \\) (temperatury w K). Ciepło odprowadzone do skraplacza to Q_L (w zadaniu Qout).<br/><b>2. Bilans i praca:</b> \\( L = Q_H - Q_L \\). Z \\( Q_H = Q_L \\cdot T_H/T_L \\) otrzymujemy \\( L = Q_L \\cdot (T_H/T_L - 1) \\).<br/><b>3. Jednostki:</b> Qout [MW], T = t + 273,15 [K] → L [MW].<br/><b>4. Podstawienie:</b> \\( L = {Qout} \\cdot \\left( \\frac{{tH}+273{,}15}{{tL}+273{,}15} - 1 \\right) \\) MW.</div>",
         "{Qout} * ( ({tH}+273.15)/({tL}+273.15) - 1 )", 2.0, [("tH", 300, 700, 0), ("tL", 10, 40, 0), ("Qout", 100, 500, 0)]),

        # T28: Entalpia pary mokrej (stopień suchości x)
        ("Tr28_EnatlpiaZSuchoscia",
         "<p><b>Tr 28.</b> Z tablic pary wodnej: entalpia cieczy wrzącej <b>{hw}</b> kJ/kg, ciepło parowania <b>{r}</b> kJ/kg. Dla stopnia suchości <b>{x}</b> oblicz entalpię pary mokrej.</p><p><b>Podaj h_x [kJ/kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie — entalpia pary mokrej (wzór na h_x):</b><br/><b>1. Wzór na entalpię pary mokrej:</b> \\( h_x = h' + x \\cdot r \\), gdzie h′ — entalpia cieczy wrzącej (kJ/kg), r — ciepło parowania (kJ/kg), x — stopień suchości (ułamek masy pary). Wartości h′, r odczytuje się z tablic pary dla danego ciśnienia (lub temperatury nasycenia).<br/><b>2. Jednostki:</b> h′, r [kJ/kg], x [−] → h_x [kJ/kg].<br/><b>3. Podstawienie:</b> \\( h_x = {hw} + {x} \\cdot {r} \\) kJ/kg.</div>",
         "{hw} + {x} * {r}", 2.0, [("x", 0.60, 0.95, 2), ("hw", 500, 1000, 0), ("r", 1500, 2200, 0)]),

        # T29: Efektywność wymiennika
        ("Tr29_WymiennikEffectiv",
         "<p><b>Tr 29.</b> W wymienniku rzeczywisty strumień oddanego ciepła wynosi <b>{Qrzecz}</b> kW. Teoretyczna maksymalna moc cieplna przy tych samych warunkach brzegowych wynosi <b>{Qmax}</b> kW. Oblicz efektywność (sprawność) wymiennika ε jako ułamek od 0 do 1.</p><p><b>Podaj \\( \\epsilon \\) [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie — efektywność (sprawność) wymiennika:</b><br/><b>1. Definicja efektywności ε:</b> Stosunek rzeczywistej mocy cieplnej wymienionej w wymienniku do teoretycznej maksymalnej mocy przy tych samych warunkach brzegowych (np. te same strumienie i temperatury wlotowe). \\( \\epsilon = \\frac{Q_{rzeczywiste}}{Q_{max}} \\).<br/><b>2. Zakres:</b> 0 ≤ ε ≤ 1. Im bliżej 1, tym wymiennik lepiej wykorzystuje możliwości odzysku ciepła.<br/><b>3. Podstawienie:</b> \\( \\epsilon = \\frac{{Qrzecz}}{{Qmax}} \\).</div>",
         "{Qrzecz} / {Qmax}", 0.01, [("Qrzecz", 15, 60, 1), ("Qmax", 80, 150, 1)]),

        # T30: I zasada — układ zamknięty
        ("Tr30_1ZasadaZamkn",
         "<p><b>Tr 30.</b> Układ zamknięty (bez odpływu masy) otrzymał <b>{Q}</b> kJ ciepła, a gaz podczas rozprężania wykonał pracę objętościową L = <b>{L}</b> kJ. Oblicz zmianę energii wewnętrznej układu ΔU (w kJ).</p><p><b>Podaj dU [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie — I zasada termodynamiki (układ zamknięty):</b><br/><b>1. Bilans energii:</b> Dla układu zamkniętego (bez przepływu masy) \\( Q = \\Delta U + L \\): ciepło doprowadzone Q równa się przyrostowi energii wewnętrznej ΔU plus praca L wykonana przez układ. Konwencja: Q &gt; 0 — doprowadzone ciepło, L &gt; 0 — praca oddana przez gaz (np. rozprężanie).<br/><b>2. Wyznaczenie ΔU:</b> \\( \\Delta U = Q - L \\). Jednostki: Q i L w kJ → ΔU w kJ.<br/><b>3. Podstawienie:</b> \\( \\Delta U = {Q} - {L} \\) kJ.</div>",
         "{Q} - {L}", 1.0, [("Q", 150, 800, 0), ("L", 50, 400, 0)])

    ]

    for name, html, feedback, formula, tolerance, variables in tasks:
        add_calculated_question(quiz, name, html, feedback, formula, tolerance, 3.0, variables)

    write_xml(quiz, 'egzamin_zadania_trening.xml')
    print("  Total training tasks generated:", len(tasks))

if __name__ == '__main__':
    print("Generating Moodle XML for training...")
    make_trening()
    print("Done.")
