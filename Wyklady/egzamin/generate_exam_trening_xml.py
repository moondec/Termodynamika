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
    ET.SubElement(cat_info, 'text').text = 'Baza treningowa zadań obliczeniowych z rozwiązanym i krok po kroku.'

    tasks = [
        # T01: Ciśnienie
        ("Tr01_Cisnienie",
         "<p><b>Tr 1.</b> Manometr na zbiorniku z gazem wskazuje nadciśnienie <b>{p_man}</b> kPa. Ciśnienie otoczenia wynosi <b>{p_bar}</b> hPa. Obliczyć ciśnienie absolutne gazu w zbiorniku.</p><p><b>Podaj p_abs [kPa]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Ciśnienie absolutne to suma barometrycznego i manometrycznego. Pamiętaj o jednostkach: 1 hPa = 0,1 kPa.<br/>\\( p_{abs} = p_{man} + \\frac{p_{bar}}{10} \\)<br/>Podstawienie: \\( p_{abs} = {p_man} + \\frac{{p_bar}}{10} \\) kPa.</div>",
         "{p_man} + {p_bar}/10", 0.5, [("p_man", 150, 450, 0), ("p_bar", 980, 1030, 0)]),

        # T02: Clapeyron - masa
        ("Tr02_Clapeyron_m",
         "<p><b>Tr 2.</b> Obliczyć masę azotu (\\(\\mu = 28,01\\) kg/kmol, R_u = 8314 J/(kmol K)) zebranego w zbiorniku o objętości <b>{V}</b> m³. Temperatura gazu to <b>{t}</b> °C, a ciśnienie absolutne wynosi <b>{p}</b> bar.</p><p><b>Podaj m [kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>1. Oblicz stałą gazową R = \\( R_u / \\mu \\) = 8314 / 28,01 = 296,82 J/(kg·K).<br/>2. Zamień jednostki: T = {t} + 273,15 K, p = {p} · 10⁵ Pa.<br/>3. Ze wzoru <i>p V = m R T</i> wyznacz \n\\( m = \\frac{p \\cdot V}{R \\cdot T} \\)<br/>Podstawienie: \\( m = \\frac{{p} \\cdot 10^5 \\cdot {V}}{296,82 \\cdot ({t} + 273,15)} \\) kg.</div>",
         "({p} * 100000 * {V}) / (296.82 * ({t} + 273.15))", 0.5, [("V", 0.1, 2.0, 2), ("p", 1.5, 8.0, 1), ("t", 10, 50, 0)]),

        # T03: Izochora p2
        ("Tr03_Izochora",
         "<p><b>Tr 3.</b> W stalowej butli (V=const) znajduje się gaz pod ciśnieniem <b>{p1}</b> bar w temp. <b>{t1}</b> °C. Butlę nasłoneczniono, w wyniku czego temp. wzrosła do <b>{t2}</b> °C. Obliczyć nowe ciśnienie.</p><p><b>Podaj p2 [bar]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Przemiana izochoryczna (Prawo Charles'a): \\( \\frac{p_1}{T_1} = \\frac{p_2}{T_2} \\). Koniecznie przelicz °C na K!<br/>\\( p_2 = p_1 \\cdot \\frac{T_2}{T_1} \\)<br/>Podstawienie: \\( p_2 = {p1} \\cdot \\frac{{t2} + 273,15}{{t1} + 273,15} \\) bar.</div>",
         "{p1} * ({t2} + 273.15) / ({t1} + 273.15)", 0.2, [("p1", 10, 200, 0), ("t1", 5, 25, 0), ("t2", 40, 80, 0)]),

        # T04: Praca izobaryczna
        ("Tr04_PracaIzobara",
         "<p><b>Tr 4.</b> Powietrze jest ogrzewane w cylindrze pod stałym tłokiem (p = <b>{p}</b> bar = const). W wyniku tego jego objętość rośnie z <b>{V1}</b> m³ do <b>{V2}</b> m³. Obliczyć wykonaną pracę objętościową gazu.</p><p><b>Podaj L [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Dla przemiany izobarycznej praca wynosi \\( L = p \\cdot (V_2 - V_1) \\). Aby wynik był w kJ, przelicz ciśnienie z bar (1 bar = 100 kPa).<br/>Podstawienie: \\( L = {p} \\cdot 100 \\cdot ({V2} - {V1}) \\) kJ.</div>",
         "{p} * 100 * ({V2} - {V1})", 2, [("p", 1, 10, 1), ("V1", 0.1, 1.0, 2), ("V2", 1.2, 3.0, 2)]),

        # T05: Energia wewnętrzna
        ("Tr05_DeltaU",
         "<p><b>Tr 5.</b> <b>{m}</b> kg azotu (\\(c_v\\) = 0,743 kJ/(kg·K)) podgrzano od temperatury <b>{t1}</b> °C do <b>{t2}</b> °C. O ile wzrosła energia wewnętrzna tego gazu?</p><p><b>Podaj ΔU [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Energia wewnętrzna gazu doskonałego zależy tylko od temperatury: \\( \\Delta U = m \\cdot c_v \\cdot (T_2 - T_1) \\). Różnica temperatur K i °C jest liczbowo taka sama.<br/>Podstawienie: \\( \\Delta U = {m} \\cdot 0,743 \\cdot ({t2} - {t1}) \\) kJ.</div>",
         "{m} * 0.743 * ({t2} - {t1})", 2, [("m", 1.0, 5.0, 1), ("t1", 10, 40, 0), ("t2", 100, 300, 0)]),

        # T06: Entalpia gazu
        ("Tr06_DeltaH",
         "<p><b>Tr 6.</b> <b>{m}</b> kg tlenu (\\(c_p\\) = 0,918 kJ/(kg·K)) schłodzono izobarycznie z <b>{t1}</b> °C do <b>{t2}</b> °C. Obliczyć zmianę entalpii układu z poprawnym znakiem (+/-).</p><p><b>Podaj ΔH [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Entalpia gazu to \\( \\Delta H = m \\cdot c_p \\cdot (T_2 - T_1) \\). Ze względu na chłodzenie (temperatura maleje), przyrost entalpii oraz ciepło układu jest wartością ujemną.<br/>Podstawienie: \\( \\Delta H = {m} \\cdot 0,918 \\cdot ({t2} - {t1}) \\) kJ.</div>",
         "{m} * 0.918 * ({t2} - {t1})", 2, [("m", 2.0, 8.0, 1), ("t1", 200, 400, 0), ("t2", 20, 80, 0)]),

        # T07: Dysza c2
        ("Tr07_Dysza",
         "<p><b>Tr 7.</b> Para wodna przepływa przez dyszę adiabatyczną. Entalpia na wlocie to <b>{h1}</b> kJ/kg, na wylocie <b>{h2}</b> kJ/kg. Prędkość strudze na wlocie to <b>{c1}</b> m/s. Obliczyć prędkość pary na wylocie dyszy.</p><p><b>Podaj c₂ [m/s]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Z bilansu energii dla elementu bez pracy mechanicznej (dysza): \\( h_1 + \\frac{c_1^2}{2000} = h_2 + \\frac{c_2^2}{2000} \\). Dzielenie przez 2000 godzi jednostki (kJ z m²/s²).<br/>Po przekształceniu: \\( c_2 = \\sqrt{2000 \\cdot (h_1 - h_2) + c_1^2} \\)<br/>Podstawienie: \\( c_2 = \\sqrt{2000 \\cdot ({h1} - {h2}) + {c1}^2} \\) m/s.</div>",
         "pow(2000 * ({h1} - {h2}) + {c1}*{c1}, 0.5)", 2, [("h1", 3000, 3300, 0), ("h2", 2800, 2950, 0), ("c1", 30, 60, 0)]),

        # T08: Moc turbiny (uproszczona)
        ("Tr08_MocTurbiny",
         "<p><b>Tr 8.</b> Przez turbinę wodną zasilaną parą przepływa <b>{mdot}</b> kg/s czynnika. Parą na wlocie ma <b>{h1}</b> kJ/kg, a na wylocie <b>{h2}</b> kJ/kg. Pominąć zmiany energii kinetycznej i potencjalnej. Obliczyć moc turbiny (adiabatycznej).</p><p><b>Podaj P [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Z I Zasady Teromydnamiki dla przepływu ustalonego: \\( P = \\dot{m} \\cdot (h_1 - h_2) \\)<br/>Podstawienie: \\( P = {mdot} \\cdot ({h1} - {h2}) \\) kW.</div>",
         "{mdot} * ({h1} - {h2})", 2, [("mdot", 10, 50, 1), ("h1", 3300, 3450, 0), ("h2", 2300, 2500, 0)]),

        # T09: Moc sprężarki
        ("Tr09_MocSprezarki",
         "<p><b>Tr 9.</b> Sprężarka adiabatyczna zasysa <b>{mdot}</b> kg/s gazu. Entalpia gazu wzrasta o <b>{dh}</b> kJ/kg. Obliczyć wymaganą moc napędową wpakowaną na wał.</p><p><b>Podaj P [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Moc doprowadzona do sprężarki (wartość dodatnia bezwzględnie): \\( P = \\dot{m} \\cdot \\Delta h \\)<br/>Podstawienie: \\( P = {mdot} \\cdot {dh} \\) kW.</div>",
         "{mdot} * {dh}", 2, [("mdot", 1.5, 6.0, 1), ("dh", 150, 350, 0)]),

        # T10: Wymiennik Q
        ("Tr10_WymiennikWoda",
         "<p><b>Tr 10.</b> W wymienniku ciepła płynie woda (\\(c_w\\) = 4,19 kJ/(kg·K)) ze strumieniem <b>{mdot}</b> kg/s. Woda ogrzewa się z z <b>{t1}</b> °C do <b>{t2}</b> °C. Obliczyć strumień przejmowanego ciepła przez wodę.</p><p><b>Podaj Q [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Moc cieplna: \\( \\dot{Q} = \\dot{m} \\cdot c_w \\cdot (T_2 - T_1) \\)<br/>Podstawienie: \\( \\dot{Q} = {mdot} \\cdot 4,19 \\cdot ({t2} - {t1}) \\) kW.</div>",
         "{mdot} * 4.19 * ({t2} - {t1})", 2, [("mdot", 0.5, 3.0, 2), ("t1", 15, 30, 0), ("t2", 60, 95, 0)]),

        # T11: Sprawnosc termiczna
        ("Tr11_SprawnoscT",
         "<p><b>Tr 11.</b> Czas pracy pewnego silnika to 1 cykl. Pobiera on <b>{Qin}</b> kJ ciepła ze źródła i odprowadza <b>{Qout}</b> kJ zasilonemu układowi otoczenia. Obliczyć sprawność termiczną silnika.</p><p><b>Podaj (eta_t) [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Wykonana praca \\( L = Q_{in} - Q_{out} \\). Sprawność \\( \\eta = \\frac{L}{Q_{in}} = 1 - \\frac{Q_{out}}{Q_{in}} \\)<br/>Podstawienie: \\( \\eta = 1 - \\frac{{Qout}}{{Qin}} \\).</div>",
         "1 - ({Qout}/{Qin})", 0.01, [("Qin", 1500, 3000, 0), ("Qout", 900, 1200, 0)]),

        # T12: Carnot ETA
        ("Tr12_Carnot",
         "<p><b>Tr 12.</b> Idealnie odwracalny silnik pracuje cyklem Carnota między <b>{TH}</b> °C i <b>{TL}</b> °C. Obliczyć sprawność tego silnika.</p><p><b>Podaj eta_C [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Sprawność wg Carnota: \\( \\eta_C = 1 - \\frac{T_L}{T_H} \\), gdzie temperatury są w kelwinach!<br/>Podstawienie: \\( \\eta_C = 1 - \\frac{{TL} + 273,15}{{TH} + 273,15} \\).</div>",
         "1 - ({TL}+273.15)/({TH}+273.15)", 0.01, [("TH", 500, 950, 0), ("TL", 15, 45, 0)]),

        # T13: COP_chlodziarki
        ("Tr13_ChlodziarkaCOP",
         "<p><b>Tr 13.</b> Obliczyć maksymalny teoretyczny współczynnik COP dla chłodziarki, by chłodziła wnętrze o temperaturze <b>{TL}</b> °C, oddając ciepło w temp <b>{TH}</b> °C.</p><p><b>Podaj COP [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Z definicji dla chłodziarki Carnota: \\( COP = \\frac{T_L}{T_H - T_L} \\) z T w kelwinach.<br/>Podstawienie: \\( COP = \\frac{{TL} + 273,15}{({TH} + 273,15) - ({TL} + 273,15)} \\).</div>",
         "({TL} + 273.15) / ({TH} - {TL})", 0.1, [("TL", -25, -5, 0), ("TH", 20, 40, 0)]),

        # T14: COP_PC
        ("Tr14_PompaCieplaCOP",
         "<p><b>Tr 14.</b> Z jaką maksymalną sprawnością energetyczną (COP wg równań Carnota) może parować pompa ciepła, pozyskująca energię z dolnego źródła gruntu przy <b>{TL}</b> °C podgrzewając system ścienny pod C.O. do <b>{TH}</b> °C?</p><p><b>Podaj COP_PC [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Dla pompy ciepła wydajność (COP_PC) określa równanie: \\( COP_H = \\frac{T_H}{T_H - T_L} \\) z T w kelwinach. Dodatkowo pamiętaj, że \\(COP_{PC} = COP_{ch} + 1\\).<br/>Podstawienie: \\( COP_H = \\frac{{TH} + 273,15}{{TH} - {TL}} \\).</div>",
         "({TH} + 273.15) / ({TH} - {TL})", 0.1, [("TH", 35, 50, 0), ("TL", -5, 12, 0)]),

        # T15: Izentropa p2
        ("Tr15_IzentropaGaz",
         "<p><b>Tr 15.</b> Powietrze (\\(\\kappa = 1,4\\)) zostaje izentropowo rozprężone. Ciśnienie początkowe wynosiło <b>{p1}</b> bar, a temp. początkowa to <b>{T1}</b> °C. Rejestrowana na dekompresji temp to <b>{T2}</b> °C. Oblicz ciśnienie końcowe.</p><p><b>Podaj p2 [bar]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Przemiana izentropowa: \\( \\frac{T_2}{T_1} = \\left(\\frac{p_2}{p_1}\\right)^{\\frac{\\kappa-1}{\\kappa}} \\). Przekształcając w p_2: \\( p_2 = p_1 \\cdot \\left(\\frac{T_2}{T_1}\\right)^{\\frac{\\kappa}{\\kappa-1}} \\). Tutaj w kelwinach! Wykładnik to \\( 1,4/0,4 = 3,5 \\).<br/>Podstawienie: \\( p_2 = {p1} \\cdot \\left( \\frac{{T2}+273,15}{{T1}+273,15} \\right)^{3,5} \\).</div>",
         "{p1} * pow(({T2}+273.15)/({T1}+273.15), 3.5)", 0.2, [("p1", 8, 25, 1), ("T1", 300, 500, 0), ("T2", -20, 50, 0)]),

        # T16: Izoterma L
        ("Tr16_IzotermaL",
         "<p><b>Tr 16.</b> W procesie sprzężania <b>{m}</b> kg gazu doskonałego (R = <b>{R}</b> J/(kg·K)) ciśnienie rośnie od <b>{p1}</b> bar do <b>{p2}</b> bar. Zjawisko wykonano izotermicznie przy temp. <b>{t}</b> °C. Obliczyć pracę włożoną w system jako wartość ujemną lub pobranej pracy bezwzględnej. Tu podaj samą jej wielkość absolutną o wartości prcy nad tłokiem jako liczbe ze znakiem. System pod ciśnieniem zmniejsza obj. zatem praca oddawana do gazy to liczba  (- L_obs ) - podaj L.</p><p><b>Podaj L [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Z równań na przemianę izotermiczną gazu o stałej temperaturze: \\( L = m R T \\cdot \\ln\\left(\\frac{p_1}{p_2}\\right) \\) by uzyskać kJ, R podajemy w kJ/kgK. <br/>Podstawienie: \\( L = {m} \\cdot \\frac{{R}}{1000} \\cdot ({t}+273,15) \\cdot \\ln\\left(\\frac{{p1}}{{p2}}\\right) \\). Ponieważ p2 > p1, ln < 0 co da ujemną wyliczoną w [kJ].</div>",
         "{m} * ({R}/1000) * ({t}+273.15) * log({p1}/{p2})", 2, [("m", 1.0, 5.0, 1), ("R", 200, 350, 0), ("p1", 1, 3, 1), ("p2", 8, 20, 1), ("t", 15, 60, 0)]),

        # T17: Mieszanina udział (mas na mol - lub masy z mol i na odwr) ale uproszcze z 2 gazami prosto.
        ("Tr17_MieszUdziałyMo",
         "<p><b>Tr 17.</b> W butli o znanej masie wymieszano <b>{m1}</b> kg tlenu O_2 z <b>{m2}</b> kg dwutlenku węgla CO_2. Obliczyć udział masowy tlenu wyrażony w procentach (np 54.3 %).</p><p><b>Podaj g_O2 [%]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Udział masowy to masa jednego składnika przez sumę obydwu: \\( g = \\frac{m_1}{m_1 + m_2} \\cdot 100\\% \\).<br/>Podstawienie: \\( g = \\frac{{m1}}{{m1} + {m2}} \\cdot 100 \\).</div>",
         "100 * {m1} / ({m1} + {m2})", 0.5, [("m1", 2.0, 10.0, 1), ("m2", 2.0, 10.0, 1)]),

        # T18: Para mokra X
        ("Tr18_ParaStopien",
         "<p><b>Tr 18.</b> W fazie statycznej komorownika para mokra waży <b>{m_calkowita}</b> kg z czego faza wodna stanowi <b>{m_woda}</b> kg. Oblicz stopień jej suchości w ułamku lub punkcie całkowitym (tj. bez procentów np 0.53).</p><p><b>Podaj x [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Stopień suchości odpowiada podziałowi w masie fazy pazywej względem całego czynnika wilgotnego. Zatem  \\( m'' = m - m' \\). I wzór podstawowy \\( x = \\frac{m''}{m_{całkowita}} = 1 - \\frac{m'}{m_{całkowita}} \\).<br/>Podstawienie: \\( x = 1 - \\frac{{m_woda}}{{m_calkowita}} \\).</div>",
         "1 - ({m_woda}/{m_calkowita})", 0.01, [("m_calkowita", 10, 50, 1), ("m_woda", 1.0, 8.0, 1)]),

        # T19: Powilgotne X
        ("Tr19_ZawilzeniePw",
         "<p><b>Tr 19.</b> Na podstawie psychrometru Assmana wyliczono że ciśnienie cząstkowe pary wynosi <b>{pw}</b> hPa dla klimatu o ogólnym b. ciśnieniem powietrza równym <b>{pB}</b> hPa. Wynik X oddaj w g/kg.</p><p><b>Podaj X [g/kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Wzór na zawilżenie absolutne używa 622 (z R suchego/R mokrego). \\( X = 622 \\cdot \\frac{p_w}{p_B - p_w} \\).<br/>Podstawienie: \\( X = 622 \\cdot \\frac{{pw}}{{pB} - {pw}} \\).</div>",
         "622 * {pw} / ({pB} - {pw})", 0.5, [("pw", 5, 25, 1), ("pB", 950, 1050, 0)]),

        # T20: Odzysk w rekuperatorze (krok mix pow. wilgotnego jest zaaw) zróbmy prościej. - Mieszanie prostych.
        ("Tr20_RegulaDzwigniPowietrza",
         "<p><b>Tr 20.</b> Centrale obiegowe wentylacji rewelacyjnie mieszają <b>{m1}</b> kg/s zewnętrznego mroźnego powietrza zewnątrz (- <b>{t1_ujemna}</b> °C) ze <b>{m2}</b> kg/s wyciągowego pow. odzyskanego (<b>{t2}</b> °C). Oblicz końcową temperaturę wynikającą dla nawiewu do dalszej nagrzewnicy.</p><p><b>Podaj T_miesz [%]:</b></p><p>UWAGA, t1= - {t1_ujemna} st. wpisz minus do równania!</p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Reguła dźwigni: T_mieszane wg bilansu: \\( t_M = \\frac{m_1 \\cdot t_1 + m_2 \\cdot t_2}{m_1 + m_2} \\). Mając znaki, tj. t_1 wchodzi jako straty cieplne ujemne.<br/>Podstawienie: \\( t_M = \\frac{{m1} \\cdot (-{t1_ujemna}) + {m2} \\cdot {t2}}{{m1} + {m2}} \\).</div>",
         "({m1} * (-{t1_ujemna}) + {m2} * {t2}) / ({m1} + {m2})", 0.5, [("m1", 2, 8, 1), ("t1_ujemna", 5, 25, 0), ("m2", 5, 12, 1), ("t2", 15, 25, 0)]),

        # T21: Sciana przenikanie
        ("Tr21_ScianaU",
         "<p><b>Tr 21.</b> Policz opór całkowity z współczynnikiem przenikania ciepła jednowarstwowej zbrojki betonowej ściany płaskiej d= <b>{d_cm}</b> cm ze spoiwem \\(\\lambda\\)= <b>{lam}</b> W/(m·K). Mając na zewnatrz alfa_1= <b>{a1}</b> i alfa_2= <b>{a2}</b> W/m²K. Otrzymaj U.</p><p><b>Podaj U [W/(m²K)]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Suma oporów na zjawisko wnosi \\( 1/U = R_{total} = \\frac{1}{\\alpha_1} + \\frac{\\delta}{\\lambda} + \\frac{1}{\\alpha_2} \\). Koniecznie centymetry konwertuj do 1 m = 100 cm!<br/>Podstawienie: \\( 1/U = \\frac{1}{{a1}} + \\frac{{d_cm} / 100}{{lam}} + \\frac{1}{{a2}} \\).</div>",
         "1 / ( (1/{a1}) + ({d_cm}/100/{lam}) + (1/{a2}) )", 0.1, [("d_cm", 15, 40, 0), ("lam", 0.8, 2.5, 2), ("a1", 10, 30, 0), ("a2", 5, 12, 0)]),

        # T22: Otto Eta
        ("Tr22_ObiegOtto",
         "<p><b>Tr 22.</b> Oblicz sprawność dla uśpionego idealnego obiegu Otto pod stopniem sprężaniu obiętościowym V1/V2 na poziomie <b>{eps}</b> z gazem doskonałym, np. zimne powietrze (\\(\\kappa\\) = 1.4).</p><p><b>Podaj eta [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Owa sprawność rzutuje od stosunku eps, wywiedzioną ogólnikową z izentropy izochorowej: \\( \\eta = 1 - \\frac{1}{\\varepsilon^{\\kappa-1}} \\).<br/>Podstawienie: \\( \\eta = 1 - \\frac{1}{{eps}^{1.4-1}} \\).</div>",
         "1 - 1 / pow({eps}, 0.4)", 0.01, [("eps", 7.0, 11.5, 1)]),

        # T23: Mieszanina entalpi
        ("Tr23_EntalpiaPowwilg",
         "<p><b>Tr 23.</b> Oblicz entalpię dla letniego powitrz z <b>{t}</b> °C oraz podniesionej zawartości w <b>{X}</b> g w kg (tzw z wilgocią).</p><p><b>Podaj h [kJ/kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Przybliżony praktyczny inżynieri wzror wywodzacy sie z 1 kg szkieletu : \\( h = 1.005 \\cdot t + \\frac{X}{1000} \\cdot (2500 + 1.86 \\cdot t) \\), ew w g ułamkach na karcie : \\( h \\approx 1.005 t + X(2.5 + 0.00186 t) \\).<br/>Podstawienie: \\( h = 1.005 \\cdot {t} + {X} \\cdot (2.5 + 0.00186 \\cdot {t}) \\).</div>",
         "1.005 * {t} + {X} * (2.5 + 0.00186 * {t})", 1.0, [("t", 20, 35, 1), ("X", 5.0, 15.0, 1)]),

        # T24: ZapotrzebowanieTlenu O2
        ("Tr24_SpalanieO2",
         "<p><b>Tr 24.</b> W silniku o procesie ciągłym przepłoneło <b>{m_c}</b> kg czystego pierwiastka grafen/węgla kopalnego C. Reagując bezresztkowo jak ze stechiometrii spalono go, oblicz zużytą tlenową cześć z masy O2 do CO2 (kg).</p><p><b>Podaj M_O2 [kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Masy molowe tj C to 12. O2 to 32. 12 kg spali się na 32 kg tlenu.<br/>Podstawienie: Z proporcji z mas \\( m_{O2} = \\frac{m_C}{12} \\cdot 32 = \\frac{{m_c}}{12} \\cdot 32 \\).</div>",
         "({m_c} / 12) * 32", 0.5, [("m_c", 5, 25, 1)]),

        # T25: Sciana Strumien q
        ("Tr25_PrzewScianaQ",
         "<p><b>Tr 25.</b> Jaką wielkość strat gęstości rzutu strumienia dla osłoniętych warstwy komory płaskiej wyindukujemy od ściany zrównanej o temp styk <b>{t1}</b> ze scianą zewnetrzną ubiegającą w stoku grubej ściedziny rzedu d=<b>{d}</b> cm ze spoiwem \\(\\lambda\\) rzędu <b>{lam}</b>. Powierzchnia to chłodnicy zew. przy <b>{t2}</b> °C stykowej.</p><p><b>Podaj q [W/m²]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Gęstość przenikania przez warstawy płaskoprzewodzącej Fouriera (nie całe U tj bez alfa): \\( q = \\frac{\\lambda}{\\delta} \\cdot (T_1 - T_2) \\). Tutaj w cm ! Konwert do metrow. <br/>Podstawienie: \\( q = \\frac{{lam}}{{d}/100} \\cdot ({t1} - {t2}) \\).</div>",
         "({lam} / ({d}/100)) * ({t1} - {t2})", 2.0, [("t1", 20, 90, 0), ("t2", -10, 5, 0), ("d", 5, 20, 1), ("lam", 0.04, 0.20, 2)]),

        # T26: Bilans chłodnicy (Wymiennik ciepla)
        ("Tr26_KondesatCieplo",
         "<p><b>Tr 26.</b> W chłodnicy oleju obniżono temp zlecenia ze <b>{t1}</b> °C by finalnie opasać masarnie uł. <b>{t2}</b> °C przemykającą ciecz o przepływie <b>{m}</b> kg/s lepkości obdarzoną ciepłym włs. c=<b>{c}</b> kJ/kgK. Oblicz rzucone straty uogólnione w cieple odprowadzonym do chłodzenia kW!</p><p><b>Podaj Q [kW]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Ciepło oddane to zmiana entalpii z uwzględnieniem obranego kierunku znaków. Moc odprowadzona oblicz na czysto i oddaj jako wielkość absolutną. <br/>Podstawienie: \\( Q = |\\dot{m} c_v (t_{out} - t_{in})| = {m} \\cdot {c} \\cdot ({t1} - {t2}) \\) jako wynik na +.</div>",
         "{m} * {c} * ({t1} - {t2})", 2.0, [("t1", 80, 130, 0), ("t2", 40, 70, 0), ("m", 0.5, 4.0, 1), ("c", 2.0, 2.5, 2)]),

        # T27: Praca Cyklu Carnota z Q odp
        ("Tr27_PracaCarnotaQ",
         "<p><b>Tr 27.</b> Obieg cyklu odwracalnego wzięty pomiędzy zbiorami <b>{tH}</b> °C oraz parną podłogowym skraplaczem dla opiętej zarysem ziemi <b>{tL}</b> °C zasymilował wymianą rzędu chłodzącą w temp wyjściowo uchyłku <b>{Qout}</b> MW ciepła z bloku. Mając na uwadzę że silnik obraca sie jako prawoskrętny obieg silnikowy Carnota, ile on potrafił oddać na przód prac z cyklu w MW ?</p><p><b>Podaj L [MW]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Aby obliczyć pracę z wyrzutu Q_L i ETA korzystasz z ETA = 1 - TL/TH. Ale też ETA = L/Q_H (z bilansu: L = Q_H - Q_L, lub Q_H = L + Q_L).<br/>Znając eta_C i równania dla stosunków ciepła to: Q_H / Q_L = TH / TL, zatem L = Q_H - Q_L = (TH/TL)*Q_L - Q_L = Q_L * ( (TH/TL) - 1 ). T podawaj w [K].<br/>Podstawienie: \\( L = {Qout} \\cdot \\left[ \\frac{{tH}+273.15}{{tL}+273.15} - 1 \\right] \\).</div>",
         "{Qout} * ( ({tH}+273.15)/({tL}+273.15) - 1 )", 2.0, [("tH", 300, 700, 0), ("tL", 10, 40, 0), ("Qout", 100, 500, 0)]),

        # T28: Mieszanina entalpi (x parametr mokry)
        ("Tr28_EnatlpiaZSuchoscia",
         "<p><b>Tr 28.</b> W fazie statycznej komorownika na karcie wodnej pobrano stan dla x=<b>{x}</b>, h_ciecz_wrzaca=<b>{hw}</b> kJ/kg oraz r_cieplo_parowania= <b>{r}</b> kJ/kg. Odtwórz pełną ujętą enalpię x układu.</p><p><b>Podaj h_x [kJ/kg]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Entalpia mieszaniny suchość: \\( h_x = h' + x \\cdot r \\).<br/>Podstawienie: \\( h_x = {hw} + {x} \\cdot {r} \\).</div>",
         "{hw} + {x} * {r}", 2.0, [("x", 0.60, 0.95, 2), ("hw", 500, 1000, 0), ("r", 1500, 2200, 0)]),

        # T29: Efektywność wymiennik
        ("Tr29_WymiennikEffectiv",
         "<p><b>Tr 29.</b> Rzeczywisty strumien oddany cieplny w rurociągu to Q= <b>{Qrzecz}</b> kW, zaś układ pod pełnym brakiem oporów teoretycznie dla owych warunków pociągnie przepływy aż za potencjalne idealne Max czyli Q_max= <b>{Qmax}</b> kW. Z jaką rezerwą i tzw. sprawnością energetyczną epsilon wyliczysz to urządzenie odzyskowe na wprost jako wielkość [względną - np ułamek od 0 - 1.0]?</p><p><b>Podaj \\( \\epsilon \\) [-]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Z definicji efektywności (sprawności wymiennika lub systemu rekuperacji dla odysku Max): \\( \\epsilon = \\frac{Q_{rzeczywiste}}{Q_{max\\_idealne}} \\).<br/>Podstawienie: \\( \\epsilon = \\frac{{Qrzecz}}{{Qmax}} \\).</div>",
         "{Qrzecz} / {Qmax}", 0.01, [("Qrzecz", 15, 60, 1), ("Qmax", 80, 150, 1)]),

        # T30: Prosta I zasada jako ostatnie.
        ("Tr30_1ZasadaZamkn",
         "<p><b>Tr 30.</b> Ostatnie podniesie proste! Ukłąd w cyklu zamknietym bez odplywow otrzymal <b>{Q}</b> kJ, a gaz z racji rozprezania dokonal pod pracami obijanej struny nad tlokiem odepchniecia oporow L = <b>{L}</b> kJ. Co stanelo sie z energia wewnętrzna układu ? Jej skok Delta u - w gore czy w dól podaj jako wielkosc liczbe.</p><p><b>Podaj dU [kJ]:</b></p>",
         "<div class='well'><b>Rozwiązanie:</b><br/>Z pierwszej zasady układ Zamkn.: \\( Q = \\Delta U + L \\), tj. \\( \\Delta U = Q - L \\).<br/>Podstawienie: \\( \\Delta U = {Q} - {L} \\). (Znaki w Q dodatnie dodanie do ciala, a L od ciała odbija na zewnatrz).</div>",
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
