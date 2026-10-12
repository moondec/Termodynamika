#!/usr/bin/env python3
"""
update_xml_formulas.py
Update Moodle XML calculated question formulas with polynomial
approximations from CoolProp. Also add missing questions.

=== UWAGA: skrypt został już zastosowany ===
Pliki Cw03/Cw04/Cw06/Cw07_*_Calculated.xml w tym katalogu zawierają już
wzory z aproksymacjami podanymi niżej oraz pytania Cw03_Zad3_8, Cw06_Zad6_6
i Cw07_Zad8_9. Ponowne uruchomienie na aktualnych plikach jest zbędne.

Czy skrypt jest idempotentny?
- Merytorycznie tak: wzory są ustawiane na te same napisy, które są już
  w plikach, a pytania dodawane są tylko wtedy, gdy ich jeszcze nie ma
  (sprawdzane po nazwie). Drugie uruchomienie nie zmienia żadnego pytania.
- Technicznie NIE: zapis przez ElementTree reserializuje cały plik (inne
  białe znaki, LF zamiast CRLF, inne kodowanie encji, usunięte komentarze),
  więc plik po przebiegu różni się tekstowo od obecnego, choć jest z nim
  semantycznie identyczny. Dlatego domyślnie skrypt pracuje w trybie
  --dry-run (tylko raportuje); zapis wymaga jawnego --write.
- Skrypt nie odtwarza aktualnych treści pytań (treści, feedback i zbiory
  danych zostały później przepisane ręcznie w audycie), więc uruchomienie
  na pierwotnych plikach też nie da dokładnie obecnej wersji – tylko wzory.

Usage:
    python update_xml_formulas.py            # dry-run: raport, bez zapisu
    python update_xml_formulas.py --write    # zapis plików
"""
import xml.etree.ElementTree as ET
import os, copy, sys

XML_DIR = os.path.dirname(os.path.abspath(__file__))
WRITE = '--write' in sys.argv

# ============================================================
# POLYNOMIAL COEFFICIENTS (from fit_polynomials.py, CoolProp / IAPWS-95)
# Szablony: {T} = temperatura [°C], {P} = ciśnienie [bar]; funkcja steam()
# podstawia nazwy zmiennych Moodle. W Moodle potęgowanie to pow(), log() = ln.
# ============================================================

# --- Water/Steam superheated h(p,T) [kJ/kg], cubic in (T-250, p-12.5) ---
# Range: p = 10..15 bar, T = 200..300 °C; max err 0.03 kJ/kg
HSH = ("2933.78 + 2.28353*({T}-250) + (-3.82234)*({P}-12.5) + 0.0351747*({T}-250)*({P}-12.5)"
       " + (-0.00191809)*pow(({T}-250),2) + (-0.0381269)*pow(({P}-12.5),2)"
       " + 1.49888e-05*pow(({T}-250),3) + (-0.000283354)*pow(({T}-250),2)*({P}-12.5)"
       " + 0.000853504*({T}-250)*pow(({P}-12.5),2) + (-0.000769777)*pow(({P}-12.5),3)")

# --- Water/Steam superheated s(p,T) [kJ/(kgK)], same form; max err 0.00005 ---
SSH = ("6.80985 + 0.00436404*({T}-250) + (-0.042532)*({P}-12.5) + 6.85312e-05*({T}-250)*({P}-12.5)"
       " + (-7.97314e-06)*pow(({T}-250),2) + 0.00143735*pow(({P}-12.5),2)"
       " + 3.92716e-08*pow(({T}-250),3) + (-6.17443e-07)*pow(({T}-250),2)*({P}-12.5)"
       " + 1.69356e-06*({T}-250)*pow(({P}-12.5),2) + (-8.27672e-05)*pow(({P}-12.5),3)")

# --- Water saturation h'(p), h''(p), s'(p), s''(p); cubic in ln(p), p = 0.5..6 bar ---
# max err: h' 0.1, h'' 0.1 kJ/kg; s' 0.0003, s'' 0.0001 kJ/(kgK)
HP  = "417.546 + 117.783*log({P}) + 10.4073*pow(log({P}),2) + 1.44645*pow(log({P}),3)"
HPP = "2674.9 + 44.2915*log({P}) + 1.87826*pow(log({P}),2) + (-0.70967)*pow(log({P}),3)"
SP  = "1.3028 + 0.315898*log({P}) + 0.0162429*pow(log({P}),2) + 0.0017039*pow(log({P}),3)"
SPP = "7.35879 + (-0.335785)*log({P}) + 0.00262104*pow(log({P}),2) + (-0.00108305)*pow(log({P}),3)"

# --- Water s'(T) sat liquid [kJ/(kgK)], T in °C (40..80 °C, err 0.0001) ---
S_WATER = "-0.00001826*pow({tz},2) + 0.014766*{tz} + 0.0111"

# --- R134a ---
H1_R134A = "-0.002127*pow({to6},2) + 0.6041*{to6} + 398.5703"  # h_g(T) vapor
H3_R134A = "0.002042*pow({tk6},2) + 1.3296*{tk6} + 200.0224"   # h_f(T) liquid
H2S_R134A = "398.7923 + (-0.152673)*{to6} + 0.722686*{tk6} + (-0.00060308)*{to6}*{tk6} + 0.00212521*pow({to6},2) + (-0.00201033)*pow({tk6},2)"
V_R134A = "0.00005115*pow({to6},2) + (-0.002437)*{to6} + 0.069308"  # v_g(T)

# --- R290 (Propane) ---
H1_R290 = "-0.004186*pow({to6},2) + 1.1477*{to6} + 574.7918"           # h_g(t_o)
H3_R290 = "0.005311*pow({tk6},2) + 2.4687*{tk6} + 200.0520"            # h_f(t_k)
H2S_R290 = "575.1506 + (-0.298900)*{to6} + 1.381165*{tk6} + (-0.00118242)*{to6}*{tk6} + 0.00392480*pow({to6},2) + (-0.00371714)*pow({tk6},2)"


def steam(template, T=None, P=None):
    """Substitute Moodle variable names into a {T}/{P} template."""
    s = template
    if T is not None:
        s = s.replace('{T}', '{' + T + '}')
    if P is not None:
        s = s.replace('{P}', '{' + P + '}')
    assert '{T}' not in s and '{P}' not in s, template
    return s


def update_answer(question, new_formula):
    """Update the answer formula text for a calculated question."""
    ans = question.find('.//answer/text')
    if ans is not None:
        if ans.text != new_formula:
            ans.text = new_formula
            return True
    return False


def find_question(root, name_text):
    """Find question by name."""
    for q in root.findall('.//question'):
        n = q.find('name/text')
        if n is not None and n.text == name_text:
            return q
    return None


def question_vars(question):
    return [dd.find('name/text').text
            for dd in question.findall('dataset_definitions/dataset_definition')]


_SIBLING_ROOTS = None


def sibling_roots(xml_dir):
    """Parsed roots of the other *_Calculated.xml files in the directory
    (the shared variables tp/pk/md/... are defined in Cw01)."""
    global _SIBLING_ROOTS
    if _SIBLING_ROOTS is None:
        _SIBLING_ROOTS = []
        for fn in sorted(os.listdir(xml_dir)):
            if fn.endswith('_Calculated.xml'):
                try:
                    _SIBLING_ROOTS.append(ET.parse(os.path.join(xml_dir, fn)).getroot())
                except ET.ParseError:
                    pass
    return _SIBLING_ROOTS


def copy_dataset_item(root, var_name, target_q, preferred=None, xml_dir=None):
    """Copy a variable's dataset_definition into target_q.

    Looks first in `preferred` question, then in every question of the file,
    then in the other *_Calculated.xml files of `xml_dir` (same shared
    variable = same 50 items), so that a variable missing in the template
    (e.g. tp/pk in Cw03, rec8 in Cw07) is still found. Every {var} used in
    the formula/text MUST have its own dataset_definition in the question,
    otherwise the question does not work after import.
    """
    if var_name in question_vars(target_q):
        return True
    sources = ([preferred] if preferred is not None else []) + list(root.findall('question'))
    if xml_dir:
        for r in sibling_roots(xml_dir):
            sources += list(r.findall('question'))
    for src in sources:
        for dd in src.findall('dataset_definitions/dataset_definition'):
            name = dd.find('name/text')
            if name is not None and name.text == var_name:
                tgt_defs = target_q.find('dataset_definitions')
                if tgt_defs is None:
                    tgt_defs = ET.SubElement(target_q, 'dataset_definitions')
                tgt_defs.append(copy.deepcopy(dd))
                return True
    print(f"  ! brak zbioru danych '{var_name}' - pytanie nie zadziała bez niego")
    return False


def make_calculated_question(name, questiontext, formula, tolerance=0.02,
                             tolerancetype=1, correctanswerformat=1,
                             correctanswerlength=1, generalfeedback='',
                             defaultgrade='1.0000000'):
    """Create a new calculated question element in the same layout as the
    other questions of these files.

    questiontext/generalfeedback: HTML as plain text - ElementTree escapes
    < > & itself. Do NOT wrap in "<![CDATA[...]]>": the marker would be
    escaped as text and Moodle would display a literal "]]>".
    tolerance: default 2 % relative (tolerancetype 1).
    """
    q = ET.Element('question', type='calculated')
    n = ET.SubElement(q, 'name')
    ET.SubElement(n, 'text').text = name
    qt = ET.SubElement(q, 'questiontext', format='html')
    ET.SubElement(qt, 'text').text = questiontext
    gf = ET.SubElement(q, 'generalfeedback', format='html')
    ET.SubElement(gf, 'text').text = generalfeedback
    ET.SubElement(q, 'defaultgrade').text = defaultgrade
    ET.SubElement(q, 'penalty').text = '0.3333333'
    ET.SubElement(q, 'hidden').text = '0'
    ET.SubElement(q, 'idnumber')
    ET.SubElement(q, 'synchronize').text = '1'
    ET.SubElement(q, 'single').text = '0'
    ET.SubElement(q, 'answernumbering').text = 'abc'
    ET.SubElement(q, 'shuffleanswers').text = '0'
    for tag in ('correctfeedback', 'partiallycorrectfeedback', 'incorrectfeedback'):
        el = ET.SubElement(q, tag, format='html')
        ET.SubElement(el, 'text')

    ans = ET.SubElement(q, 'answer', fraction='100', format='moodle_auto_format')
    ET.SubElement(ans, 'text').text = formula
    ET.SubElement(ans, 'tolerance').text = str(tolerance)
    ET.SubElement(ans, 'tolerancetype').text = str(tolerancetype)
    ET.SubElement(ans, 'correctanswerformat').text = str(correctanswerformat)
    ET.SubElement(ans, 'correctanswerlength').text = str(correctanswerlength)
    fb = ET.SubElement(ans, 'feedback', format='html')
    ET.SubElement(fb, 'text')

    ET.SubElement(q, 'unitgradingtype').text = '0'
    ET.SubElement(q, 'unitpenalty').text = '0.1000000'
    ET.SubElement(q, 'showunits').text = '3'
    ET.SubElement(q, 'unitsleft').text = '0'
    ET.SubElement(q, 'dataset_definitions')
    return q


def set_formula(root, name, formula):
    q = find_question(root, name)
    if q is None:
        print(f"  - {name}: brak pytania")
        return 0
    changed = update_answer(q, formula)
    print(f"  {'*' if changed else '='} {name}: wzór {'zmieniony' if changed else 'bez zmian'}")
    return int(changed)


def save(tree, filepath, changes):
    if not changes:
        print("  (bez zmian)")
        return
    if WRITE:
        tree.write(filepath, encoding='unicode', xml_declaration=True)
        print(f"  zapisano {os.path.basename(filepath)} ({changes} zmian)")
    else:
        print(f"  dry-run: {changes} zmian NIE zapisano (użyj --write)")


def process_cw03(filepath):
    """Update Cw03 formulas and add missing questions."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    changes = 0

    h2 = steam(HSH, T='tp', P='pk')
    changes += set_formula(root, 'Cw03_Zad3_2_Moc_kotla',
                           f"{{md}} * 1000 / 3600 * (({h2}) - 4.19 * {{tz}})")
    changes += set_formula(root, 'Cw03_Zad3_3_Zuzycie_gazu',
                           f"{{md}} * 1000 / 3600 * (({h2}) - 4.19 * {{tz}}) / ({{ek}} * 50000 * 0.7) * 3600")
    hp, hpp = steam(HP, P='pdl'), steam(HPP, P='pdl')
    changes += set_formula(root, 'Cw03_Zad3_5_Stopien_suchosci',
                           f"({{hm}} - ({hp})) / (({hpp}) - ({hp}))")
    changes += set_formula(root, 'Cw03_Zad3_7_Entropia_kotla',
                           f"{{md}} * 1000 / 3600 * (({steam(SSH, T='tp', P='pk')}) - ({S_WATER}))")

    # Zad 3.8 (Kondensat): Q = m * (h(p,t) - h'(p_dl))
    if find_question(root, 'Cw03_Zad3_8_Bilans_kondensatu') is None:
        q38 = make_calculated_question(
            'Cw03_Zad3_8_Bilans_kondensatu',
            '<p><b>Ćw. 3 — Bilans Kondensatu</b></p>'
            '<p>Para z kotła: \\(p =\\) <b>{pk}</b> bar, \\(t =\\) <b>{tp}</b> °C, '
            '\\(\\dot{{m}} =\\) <b>{md}</b> t/h, jest dławiona (\\(h = const\\)) do ciśnienia '
            '\\(p_{{dl}} =\\) <b>{pdl}</b> bar, a następnie w wymienniku ciepła skrapla się '
            'do cieczy nasyconej przy tym ciśnieniu.</p>'
            '<p><b>Oblicz moc cieplną wymiennika \\(\\dot{{Q}}_{{wym}} = \\dot{{m}} \\cdot (h_{{para}} - h\\prime)\\) [kW]:</b></p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{{md}} * 1000 / 3600 * (({h2}) - ({hp}))",
            correctanswerlength=1)
        template = find_question(root, 'Cw03_Zad3_2_Moc_kotla')
        for var in ['md', 'tp', 'pk', 'pdl']:
            copy_dataset_item(root, var, q38, preferred=template,
                              xml_dir=os.path.dirname(filepath))
        root.append(q38)
        changes += 1
        print("  + Added Cw03_Zad3_8_Bilans_kondensatu")

    save(tree, filepath, changes)
    return True


def process_cw04(filepath):
    """Update Cw04 formulas with polynomial approximations."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    changes = 0

    h1 = steam(HSH, T='t1t', P='p1t')
    s1 = steam(SSH, T='t1t', P='p1t')
    hp, hpp = steam(HP, P='p2t'), steam(HPP, P='p2t')
    sp, spp = steam(SP, P='p2t'), steam(SPP, P='p2t')
    # x_2s = (s1 - s'(p2)) / (s''(p2) - s'(p2));  h_2s = h'(p2) + x_2s * (h''(p2) - h'(p2))
    h2s = f"(({hp}) + (({s1}) - ({sp})) / (({spp}) - ({sp})) * (({hpp}) - ({hp})))"

    changes += set_formula(root, 'Cw04_Zad4_3_Moc_turbiny_idealna',
                           f"{{mdt}} * (({h1}) - {h2s})")
    changes += set_formula(root, 'Cw04_Zad4_4_Moc_rzeczywista',
                           f"{{eis}} * {{mdt}} * (({h1}) - {h2s})")
    changes += set_formula(root, 'Cw04_Zad4_4b_Entalpia_rzeczywista',
                           f"({h1}) - {{eis}} * (({h1}) - {h2s})")

    save(tree, filepath, changes)
    return True


def process_cw06(filepath):
    """Update Cw06 R134a formulas with polynomial approximations."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    changes = 0

    eer = f"(({H1_R134A}) - ({H3_R134A})) / (({H2S_R134A}) - ({H1_R134A}))"
    changes += set_formula(root, 'Cw06_Zad6_1_EER', eer)
    changes += set_formula(root, 'Cw06_Zad6_2_Moc_sprezarki', f"{{Qo6}} / ({eer})")
    changes += set_formula(root, 'Cw06_Zad6_3_Strumien_masy',
                           f"{{Qo6}} / (({H1_R134A}) - ({H3_R134A}))")
    changes += set_formula(root, 'Cw06_Zad6_4_COP_pompa_ciepla', f"{eer} + 1")
    changes += set_formula(root, 'Cw06_Zad6_7_Predkosc_rurociagu',
                           f"({{Qo6}} / (({H1_R134A}) - ({H3_R134A}))) * ({V_R134A}) / (3.14159265 * pow({{dr6}} / 1000, 2) / 4)")

    # Zad 6.6 — R134a vs R290
    if find_question(root, 'Cw06_Zad6_6_EER_R290') is None:
        q66 = make_calculated_question(
            'Cw06_Zad6_6_EER_R290',
            '<p><b>Ćw. 6 — Porównanie Czynników: EER dla R290 (propan)</b></p>'
            '<p>Obieg chłodniczy teoretyczny z propanem (R290) pracuje między temperaturą '
            'parowania \\(t_o =\\) <b>{to6}</b> °C a temperaturą skraplania \\(t_k =\\) <b>{tk6}</b> °C '
            '(bez przegrzania i dochłodzenia, \\(h_4 = h_3\\)).</p>'
            '<p><b>Oblicz EER = \\(q_o / l_k\\) dla R290:</b></p>'
            '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>',
            f"(({H1_R290}) - ({H3_R290})) / (({H2S_R290}) - ({H1_R290}))",
            correctanswerlength=2)
        template = find_question(root, 'Cw06_Zad6_1_EER')
        for var in ['to6', 'tk6']:
            copy_dataset_item(root, var, q66, preferred=template,
                              xml_dir=os.path.dirname(filepath))
        root.append(q66)
        changes += 1
        print("  + Added Cw06_Zad6_6_EER_R290")

    save(tree, filepath, changes)
    return True


def process_cw07(filepath):
    """Cw07 — HVAC: existing cp*ΔT formulas are kept; add missing question."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    changes = 0

    # Zad 7.9 Rekuperacja: Q_rec = ṁ * cp * η * (t_wewn - t_zima)
    if find_question(root, 'Cw07_Zad8_9_Rekuperacja') is None:
        q79 = make_calculated_question(
            'Cw07_Zad8_9_Rekuperacja',
            '<p><b>Ćw. 7 — Odzysk Ciepła (rekuperacja)</b></p>'
            '<p>W centrali wentylacyjnej o strumieniu \\(\\dot{{V}} =\\) <b>{Vd8}</b> m³/h '
            '(\\(\\rho = 1.2\\) kg/m³, \\(c_p = 1005\\) J/(kg·K)) zainstalowano rekuperator krzyżowy '
            'o sprawności temperaturowej \\(\\eta =\\) <b>{rec8}</b> %.<br>'
            'Powietrze zewnętrzne (zima): \\(t_Z =\\) <b>{tzz}</b> °C, powietrze wywiewane: '
            '\\(t_W =\\) <b>{tw8}</b> °C.</p>'
            '<p><b>Oblicz moc cieplną odzyskaną z powietrza wywiewanego '
            '\\(\\Delta\\dot{{Q}} = \\dot{{m}} \\cdot c_p \\cdot \\eta \\cdot (t_W - t_Z)\\) [kW]:</b></p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            "1.2 * {Vd8} / 3600 * 1005 * {rec8} / 100 * ({tw8} - {tzz}) / 1000",
            correctanswerlength=1)
        template = find_question(root, 'Cw07_Zad8_1_Moc_nagrzewnicy_zima')
        for var in ['rec8', 'Vd8', 'tw8', 'tzz']:
            copy_dataset_item(root, var, q79, preferred=template,
                              xml_dir=os.path.dirname(filepath))
        root.append(q79)
        changes += 1
        print("  + Added Cw07_Zad8_9_Rekuperacja")

    save(tree, filepath, changes)
    return True


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("UPDATING XML FORMULAS WITH POLYNOMIAL APPROXIMATIONS")
    print("tryb:", "zapis (--write)" if WRITE else "dry-run (bez zapisu)")
    print("=" * 60)

    files = {
        'Cw03': os.path.join(XML_DIR, 'Cw03_Kociol_Parowy_Calculated.xml'),
        'Cw04': os.path.join(XML_DIR, 'Cw04_Obieg_Rankine_Calculated.xml'),
        'Cw06': os.path.join(XML_DIR, 'Cw06_Projekt_Chlodniczy_Calculated.xml'),
        'Cw07': os.path.join(XML_DIR, 'Cw07_Projekt_HVAC_Calculated.xml'),
    }
    if '--dir' in sys.argv:
        d = sys.argv[sys.argv.index('--dir') + 1]
        files = {k: os.path.join(d, os.path.basename(v)) for k, v in files.items()}

    for name, path in files.items():
        print(f"\n--- {name}: {os.path.basename(path)} ---")
        if not os.path.exists(path):
            print(f"  ✗ File not found!")
            continue

        if name == 'Cw03':
            process_cw03(path)
        elif name == 'Cw04':
            process_cw04(path)
        elif name == 'Cw06':
            process_cw06(path)
        elif name == 'Cw07':
            process_cw07(path)

    print("\n✓ Done.")
