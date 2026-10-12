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
import os, copy, sys, random

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

# --- Water/Steam superheated h(p,T), s(p,T) for the Cw04 Zad 4.5 variant
#     (p1t + 4 bar, t1t + 50 K): cubic in (T-300, p-16.5) ---
# Range: p = 14..19 bar, T = 250..350 °C; max err h 0.15 kJ/kg, s 0.0003 kJ/(kgK)
HSH2 = ("3034.07 + 2.25329*({T}-300) + (-2.77496)*({P}-16.5) + 0.0194378*({T}-300)*({P}-16.5)"
        " + (-0.00105331)*pow(({T}-300),2) + (-0.0135631)*pow(({P}-16.5),2)"
        " + 7.00492e-06*pow(({T}-300),3) + (-0.000116249)*pow(({T}-300),2)*({P}-16.5)"
        " + 0.000231903*({T}-300)*pow(({P}-16.5),2) + (-7.92723e-05)*pow(({P}-16.5),3)")
SSH2 = ("6.87037 + 0.00393117*({T}-300) + (-0.0316459)*({P}-16.5) + 3.43641e-05*({T}-300)*({P}-16.5)"
        " + (-5.32487e-06)*pow(({T}-300),2) + 0.000835407*pow(({P}-16.5),2)"
        " + 1.8544e-08*pow(({T}-300),3) + (-2.35231e-07)*pow(({T}-300),2)*({P}-16.5)"
        " + 4.13759e-07*({T}-300)*pow(({P}-16.5),2) + (-3.49913e-05)*pow(({P}-16.5),3)")

# --- Water/Steam superheated T(h,p) [°C] (Cw03 Zad 3.4, temperatura po dławieniu):
#     cubic in ((h-2920)/100, p-4) ---
# Range: p = 2..6 bar, h = 2780..3060 kJ/kg (para przegrzana); max err 0.12 °C na siatce,
# do 0.4 °C na brzegu zakresu (h = 2796 kJ/kg, 2 bar) – wobec tolerancji 2 % bez znaczenia
TSH_H = ("228.399 + 48.4102*(({H}-2920)/100) + 1.92588*({P}-4) + (-0.723719)*(({H}-2920)/100)*({P}-4)"
         " + 0.469339*pow((({H}-2920)/100),2) + (-0.0147598)*pow(({P}-4),2)"
         " + (-0.211493)*pow((({H}-2920)/100),3) + 0.189917*pow((({H}-2920)/100),2)*({P}-4)"
         " + 0.0121502*(({H}-2920)/100)*pow(({P}-4),2) + 3.08864e-05*pow(({P}-4),3)")

# --- Water saturation temperature t_s(p) [°C] (Cw03 Zad 3.6); cubic in (p-12.5) ---
# Range: p = 10..15 bar; max err 0.003 °C
TS_P = "189.811 + 3.64649*({P}-12.5) + (-0.116047)*pow(({P}-12.5),2) + 0.00564638*pow(({P}-12.5),3)"


def steam(template, T=None, P=None, H=None):
    """Substitute Moodle variable names into a {T}/{P}/{H} template.

    A plain name ("tp") becomes "{tp}"; a value containing an operator
    (e.g. "{t1t}+50" or a whole h-expression) is inserted in parentheses.
    """
    def expr(v):
        return '{' + v + '}' if v.replace('_', 'a').isalnum() else '(' + v + ')'
    s = template
    if T is not None:
        s = s.replace('{T}', expr(T))
    if P is not None:
        s = s.replace('{P}', expr(P))
    if H is not None:
        s = s.replace('{H}', expr(H))
    assert '{T}' not in s and '{P}' not in s and '{H}' not in s, template
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
    ET.SubElement(q, 'shuffleanswers').text = '1'
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
    ET.SubElement(q, 'unitpenalty').text = '1.0000000'
    ET.SubElement(q, 'showunits').text = '3'
    ET.SubElement(q, 'unitsleft').text = '0'
    ET.SubElement(q, 'dataset_definitions')
    return q


def make_dataset_definition(name, minimum, maximum, decimals, seed, count=50):
    """New shared dataset_definition with `count` items drawn deterministically
    (random.Random(seed), uniform on the min..max grid with `decimals` places),
    in the same XML layout as the existing definitions of these files."""
    dd = ET.Element('dataset_definition')
    ET.SubElement(ET.SubElement(dd, 'status'), 'text').text = 'shared'
    ET.SubElement(ET.SubElement(dd, 'name'), 'text').text = name
    ET.SubElement(dd, 'type').text = 'calculated'
    ET.SubElement(ET.SubElement(dd, 'distribution'), 'text').text = 'uniform'
    ET.SubElement(ET.SubElement(dd, 'minimum'), 'text').text = f"{minimum:.{decimals}f}"
    ET.SubElement(ET.SubElement(dd, 'maximum'), 'text').text = f"{maximum:.{decimals}f}"
    ET.SubElement(ET.SubElement(dd, 'decimals'), 'text').text = str(decimals)
    ET.SubElement(dd, 'itemcount').text = str(count)
    ET.SubElement(dd, 'number_of_items').text = str(count)
    items = ET.SubElement(dd, 'dataset_items')
    rng = random.Random(seed)
    step = 10 ** (-decimals)
    nsteps = int(round((maximum - minimum) / step))
    for i in range(1, count + 1):
        v = minimum + rng.randint(0, nsteps) * step
        it = ET.SubElement(items, 'dataset_item')
        ET.SubElement(it, 'number').text = str(i)
        ET.SubElement(it, 'value').text = f"{v:.{decimals}f}"
    return dd


def make_multichoice_question(name, questiontext, answers, generalfeedback='',
                              defaultgrade='1.0000000'):
    """Single-answer multichoice in the layout of the other multichoice
    questions of these files (Cw03_Zad3_1_Stan_pary). answers: list of
    (text, fraction) with exactly one fraction 100."""
    assert sum(1 for _, f in answers if int(f) == 100) == 1, name
    q = ET.Element('question', type='multichoice')
    ET.SubElement(ET.SubElement(q, 'name'), 'text').text = name
    qt = ET.SubElement(q, 'questiontext', format='html')
    ET.SubElement(qt, 'text').text = questiontext
    gf = ET.SubElement(q, 'generalfeedback', format='html')
    ET.SubElement(gf, 'text').text = generalfeedback
    ET.SubElement(q, 'defaultgrade').text = defaultgrade
    ET.SubElement(q, 'penalty').text = '0.3333333'
    for text, fraction in answers:
        a = ET.SubElement(q, 'answer', fraction=str(fraction), format='html')
        ET.SubElement(a, 'text').text = text
    ET.SubElement(q, 'shuffleanswers').text = '1'
    ET.SubElement(q, 'single').text = 'true'
    ET.SubElement(q, 'answernumbering').text = 'abc'
    return q


def append_question(root, q):
    """Append a question to <quiz> with the file's 4-space indentation."""
    ET.indent(q, space='    ', level=1)
    children = list(root)
    if children:
        children[-1].tail = '\n    '
    q.tail = '\n'
    root.append(q)
    print(f"  + Added {q.find('name/text').text}")
    return 1


def set_formula(root, name, formula):
    q = find_question(root, name)
    if q is None:
        print(f"  - {name}: brak pytania")
        return 0
    changed = update_answer(q, formula)
    print(f"  {'*' if changed else '='} {name}: wzór {'zmieniony' if changed else 'bez zmian'}")
    return int(changed)


def set_text(root, name, path, value):
    """Set the text of a sub-element (e.g. 'defaultgrade', 'answer/tolerance')
    of the named question; returns 1 if it changed."""
    q = find_question(root, name)
    if q is None:
        print(f"  - {name}: brak pytania")
        return 0
    el = q.find(path)
    if el is None or el.text == value:
        return 0
    el.text = value
    print(f"  * {name}: {path} = {value}")
    return 1


def save(tree, filepath, changes):
    if not changes:
        print("  (bez zmian)")
        return
    if WRITE:
        # LF, UTF-8 declaration and trailing newline as in the files in the repo
        body = ET.tostring(tree.getroot(), encoding='unicode')
        with open(filepath, 'w', encoding='utf-8', newline='\n') as f:
            f.write("<?xml version='1.0' encoding='UTF-8'?>\n" + body.rstrip('\n') + '\n')
        print(f"  zapisano {os.path.basename(filepath)} ({changes} zmian)")
    else:
        print(f"  dry-run: {changes} zmian NIE zapisano (użyj --write)")


def process_cw02(filepath):
    """Cw02 — sprężarkownia: add Zad 2.5 (sprężanie dwustopniowe) and
    Zad 2.6 (izoterma vs adiabata) questions; existing formulas are kept."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    changes = 0
    template = find_question(root, 'Cw02_Zad2_1_Praca_techniczna')

    # praca politropowa jednostopniowa i dwustopniowa (p_m = sqrt(p1*p2), chłodzenie do t1)
    l_1st = "{npoly} / ({npoly} - 1) * 287 * ({t1} + 273.15) * (pow({p2} / 1, ({npoly} - 1) / {npoly}) - 1)"
    l_2st = "2 * {npoly} / ({npoly} - 1) * 287 * ({t1} + 273.15) * (pow(sqrt(1 * {p2}) / 1, ({npoly} - 1) / {npoly}) - 1)"
    dane = ('<p>Sprężarka tłokowa spręża powietrze z ciśnienia \\(p_1 = 1\\) bar do \\(p_2 =\\) <b>{p2}</b> bar. '
            'Temperatura ssania: \\(t_1 =\\) <b>{t1}</b> °C, wykładnik politropy: \\(n =\\) <b>{npoly}</b>, '
            '\\(R = 287\\) J/(kg·K).</p>')

    # Zad 2.5a: optymalne ciśnienie międzystopniowe
    if find_question(root, 'Cw02_Zad2_5_Cisnienie_miedzystopniowe') is None:
        q = make_calculated_question(
            'Cw02_Zad2_5_Cisnienie_miedzystopniowe',
            '<p><b>Ćw. 2 — Sprężanie Dwustopniowe: ciśnienie międzystopniowe</b></p>' + dane +
            '<p>Temperatura tłoczenia przy sprężaniu jednostopniowym (Zad. 2.3) jest za wysoka dla oleju, '
            'dlatego projektujemy sprężanie <b>dwustopniowe</b> z chłodnicą międzystopniową.</p>'
            '<p><b>Oblicz optymalne ciśnienie międzystopniowe \\(p_m\\) [bar] (minimalna suma prac obu stopni '
            '– ściśle przy chłodzeniu międzystopniowym do \\(t_1\\)):</b></p>'
            '<p>$$p_m = \\sqrt{{p_1 \\cdot p_2}}$$</p>'
            '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>',
            "sqrt(1 * {p2})",
            correctanswerlength=2,
            generalfeedback='<p>Przy jednakowych wykładnikach politropy obu stopni i chłodzeniu międzystopniowym '
            'do temperatury ssania suma prac jest najmniejsza, gdy oba stopnie mają ten sam stosunek ciśnień: '
            '\\(p_m/p_1 = p_2/p_m\\), czyli \\(p_m = \\sqrt{{p_1 p_2}}\\) (Zad. 2.5 na slajdach; np. 1 i 9.5 bar: '
            '\\(p_m \\approx 3.08\\) bar). Wynik nie zależy od \\(t_1\\) ani \\(n\\).</p>')
        for var in ['p2', 't1', 'npoly']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=os.path.dirname(filepath))
        changes += append_question(root, q)

    # Zad 2.5a jest proste (sqrt(p2) przy p1 = 1 bar) – pół punktu
    changes += set_text(root, 'Cw02_Zad2_5_Cisnienie_miedzystopniowe', 'defaultgrade', '0.5000000')

    # Zad 2.5b: oszczędność pracy przy sprężaniu dwustopniowym
    if find_question(root, 'Cw02_Zad2_5_Oszczednosc_dwustopniowe') is None:
        q = make_calculated_question(
            'Cw02_Zad2_5_Oszczednosc_dwustopniowe',
            '<p><b>Ćw. 2 — Sprężanie Dwustopniowe: oszczędność pracy</b></p>' + dane +
            '<p>Porównujemy sprężanie <b>jednostopniowe</b> (Zad. 2.1) ze sprężaniem <b>dwustopniowym</b> '
            'z optymalnym ciśnieniem międzystopniowym \\(p_m = \\sqrt{{p_1 \\cdot p_2}}\\) i chłodzeniem '
            'międzystopniowym z powrotem do temperatury ssania \\(t_1\\). Oba stopnie są politropowe z tym samym '
            'wykładnikiem \\(n\\), więc pracę każdego stopnia liczysz wzorem z Zad. 2.1 (stosunek ciśnień '
            '\\(p_m/p_1 = p_2/p_m\\), temperatura początkowa \\(T_1\\)).</p>'
            '<p><b>Oblicz, o ile procent suma wartości bezwzględnych prac technicznych obu stopni '
            '\\(|l_I| + |l_{{II}}|\\) jest mniejsza od pracy sprężania jednostopniowego \\(|l_t|\\):</b></p>'
            '<p>$$\\Delta = \\left(1 - \\frac{|l_I| + |l_{{II}}|}{|l_t|}\\right) \\cdot 100\\ \\%$$</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"(1 - ({l_2st}) / ({l_1st})) * 100",
            correctanswerlength=1,
            generalfeedback='<p>1. \\(|l_t| = \\frac{{n}}{n-1} R T_1 \\left[(p_2/p_1)^{(n-1)/n} - 1\\right]\\) '
            '(jednostopniowo, Zad. 2.1).<br>'
            '2. \\(p_m = \\sqrt{{p_1 p_2}}\\); każdy stopień ma stosunek ciśnień \\(\\sqrt{{p_2/p_1}}\\) i startuje od '
            '\\(T_1\\), więc \\(|l_I| = |l_{{II}}| = \\frac{{n}}{n-1} R T_1 \\left[(p_2/p_1)^{(n-1)/(2n)} - 1\\right]\\).<br>'
            '3. \\(\\Delta = (1 - 2|l_I|/|l_t|) \\cdot 100\\). Dla danych ze slajdu (9.5 bar, \\(n = 1.35\\)) '
            'ok. 14.5 % – oprócz niższej temperatury tłoczenia (Zad. 2.5) dwustopniowe sprężanie oszczędza '
            'też pracę napędu.</p>')
        for var in ['p2', 't1', 'npoly']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=os.path.dirname(filepath))
        changes += append_question(root, q)

    # Zad 2.6: izoterma vs adiabata (kappa = 1.4)
    if find_question(root, 'Cw02_Zad2_6_Oszczednosc_izoterma_adiabata') is None:
        q = make_calculated_question(
            'Cw02_Zad2_6_Oszczednosc_izoterma_adiabata',
            '<p><b>Ćw. 2 — Porównanie Procesów Sprężania: izoterma a adiabata</b></p>'
            '<p>Powietrze (\\(R = 287\\) J/(kg·K), \\(\\kappa = 1.4\\)) jest sprężane z \\(p_1 = 1\\) bar do '
            '\\(p_2 =\\) <b>{p2}</b> bar; temperatura ssania \\(t_1 =\\) <b>{t1}</b> °C.</p>'
            '<p>Porównaj co do wartości bezwzględnej pracę techniczną sprężania <b>izotermicznego</b> '
            '(\\(n = 1\\): \\(|l_t| = R T_1 \\ln(p_2/p_1)\\)) i <b>adiabatycznego</b> (\\(n = \\kappa\\): '
            '\\(|l_t| = \\frac{\\kappa}{\\kappa-1} R T_1 \\left[(p_2/p_1)^{(\\kappa-1)/\\kappa} - 1\\right]\\)).</p>'
            '<p><b>Oblicz, o ile procent mniej pracy wymaga sprężanie izotermiczne niż adiabatyczne:</b></p>'
            '<p>$$\\Delta = \\left(1 - \\frac{|l_{{izo}}|}{|l_{{ad}}|}\\right) \\cdot 100\\ \\%$$</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            "(1 - (287 * ({t1} + 273.15) * log({p2} / 1)) / (1.4 / 0.4 * 287 * ({t1} + 273.15) * (pow({p2} / 1, 0.4 / 1.4) - 1))) * 100",
            correctanswerlength=1,
            generalfeedback='<p>1. Izoterma: \\(|l_{{izo}}| = R T_1 \\ln(p_2/p_1)\\) – minimum teoretyczne '
            '(całka z \\(1/p\\) daje logarytm, dlatego wzór politropowy z \\(n = 1\\) „się psuje”).<br>'
            '2. Adiabata: \\(|l_{{ad}}| = 3.5 \\, R T_1 \\left[(p_2/p_1)^{0.286} - 1\\right]\\).<br>'
            '3. \\(\\Delta = (1 - |l_{{izo}}|/|l_{{ad}}|) \\cdot 100\\); stosunek prac nie zależy od \\(T_1\\). '
            'Dla danych ze slajdu (1 → 9.5 bar): 189 i 266 kJ/kg, czyli o 29 % mniej (Zad. 2.6) – '
            'dlatego chłodzimy sprężarki.</p>')
        for var in ['p2', 't1']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=os.path.dirname(filepath))
        changes += append_question(root, q)

    save(tree, filepath, changes)
    return True


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

    template = find_question(root, 'Cw03_Zad3_8_Bilans_kondensatu')

    # Zad 3.4: temperatura pary po dławieniu izentalpowym, t2 = T(h1, p_dl)
    if find_question(root, 'Cw03_Zad3_4_Temperatura_po_dlawieniu') is None:
        q = make_calculated_question(
            'Cw03_Zad3_4_Temperatura_po_dlawieniu',
            '<p><b>Ćw. 3 — Dławienie Pary (h = const)</b></p>'
            '<p>Para z kotła: \\(p_1 =\\) <b>{pk}</b> bar, \\(t_1 =\\) <b>{tp}</b> °C, jest dławiona w zaworze '
            'redukcyjnym do ciśnienia \\(p_2 =\\) <b>{pdl}</b> bar. Dławienie jest izentalpowe: \\(h_2 = h_1\\).</p>'
            '<p>1. Odczytaj \\(h_1 = h(p_1, t_1)\\) z Załącznika B (interpolacja liniowa w temperaturze, a gdy '
            'ciśnienia nie ma w tablicy – także między sąsiednimi kolumnami ciśnień).<br>'
            '2. Sprawdź, że \\(h_2 > h\\prime\\prime(p_2)\\) (Załącznik A) – para po dławieniu jest nadal przegrzana.<br>'
            '3. W kolumnie \\(p_2\\) Załącznika B znajdź sąsiednie wiersze \\(t_a, t_b\\), między którymi leży '
            '\\(h_2\\), i wyznacz temperaturę interpolacją odwrotną:</p>'
            '<p>$$t_2 = t_a + \\frac{h_2 - h_a}{h_b - h_a} \\cdot (t_b - t_a)$$</p>'
            '<p><b>Oblicz temperaturę pary po dławieniu \\(t_2\\) [°C].</b></p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            steam(TSH_H, H=h2, P='pdl'),
            correctanswerlength=1,
            generalfeedback='<p>1. \\(h_1\\) – Załącznik B dla \\(p_1, t_1\\) (np. 10 bar, 250 °C: 2943 kJ/kg).<br>'
            '2. \\(h_2 = h_1\\) (dławienie); \\(h_2 > h\\prime\\prime(p_2)\\) → para przegrzana.<br>'
            '3. Interpolacja odwrotna w kolumnie \\(p_2\\) (np. 2 bar: 200 °C – 2870, 250 °C – 2971 kJ/kg → '
            '\\(t_2 = 200 + (2943-2870)/(2971-2870) \\cdot 50 \\approx 236\\) °C, Zad. 3.4 na slajdach). '
            'Ciśnienie spada drastycznie, temperatura tylko nieznacznie – para staje się „bardziej” przegrzana.</p>')
        for var in ['pk', 'tp', 'pdl']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=os.path.dirname(filepath))
        changes += append_question(root, q)

    # Zad 3.6: interpolacja liniowa t_s(p) między wierszami 10 i 15 bar Załącznika A
    if find_question(root, 'Cw03_Zad3_6_Interpolacja_ts') is None:
        q = make_calculated_question(
            'Cw03_Zad3_6_Interpolacja_ts',
            '<p><b>Ćw. 3 — Interpolacja w Tablicach Pary</b></p>'
            '<p>Producent kotła proponuje pracę przy ciśnieniu pary \\(p =\\) <b>{pint}</b> bar. Takiego ciśnienia '
            'nie ma w tablicy pary nasyconej (Załącznik A) – odczytaj temperaturę nasycenia \\(t_s\\) dla '
            'sąsiednich wierszy \\(p_a\\) i \\(p_b\\) (10 i 15 bar) i zastosuj <b>interpolację liniową</b>:</p>'
            '<p>$$t_s(p) = t_s(p_a) + \\frac{p - p_a}{p_b - p_a} \\cdot \\left[t_s(p_b) - t_s(p_a)\\right]$$</p>'
            '<p><b>Oblicz temperaturę nasycenia (wrzenia) \\(t_s\\) [°C] przy ciśnieniu \\(p =\\) <b>{pint}</b> bar.</b></p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            steam(TS_P, P='pint'),
            correctanswerlength=1,
            generalfeedback='<p>Załącznik A: \\(t_s(10\\ \\text{{bar}}) = 179.9\\) °C, \\(t_s(15\\ \\text{{bar}}) = 198.3\\) °C. '
            'Interpolacja liniowa (jak w Zad. 3.1/3.6 na slajdach) daje wynik z błędem poniżej 1 K względem '
            'dokładnych tablic – krzywa nasycenia jest w tym zakresie prawie prostą.</p>')
        # nowa zmienna: ciśnienie między wierszami 10 i 15 bar tablicy (seed 2036)
        q.find('dataset_definitions').append(make_dataset_definition('pint', 10.5, 14.5, 1, seed=2036))
        changes += append_question(root, q)

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

    template = find_question(root, 'Cw04_Zad4_4_Moc_rzeczywista')
    xml_dir = os.path.dirname(filepath)
    # Odczyt z tablic: dla p2t = 1.5 bar (brak wiersza w Załączniku A – interpolacja liniowa
    # między 1 i 2 bar) błąd studenta sięga 2.1 % na N_t, 2.7 % na eta_t – stąd tolerancja 0.03
    # (także w istniejących 4.3/4.4; 4.4b – entalpia h2 ok. 2600 kJ/kg – zostaje 0.01).
    TOL_TAB = 0.03
    for qname, tol in (('Cw04_Zad4_3_Moc_turbiny_idealna', '0.03'),
                       ('Cw04_Zad4_4_Moc_rzeczywista', '0.03')):
        changes += set_text(root, qname, 'answer/tolerance', tol)

    # Zad 4.5: wariant "Modernizacja Plus" – para o p1+4 bar i t1+50 K
    if find_question(root, 'Cw04_Zad4_5_Moc_wyzsze_parametry') is None:
        h1v = steam(HSH2, T='{t1t}+50', P='{p1t}+4')
        s1v = steam(SSH2, T='{t1t}+50', P='{p1t}+4')
        h2sv = f"(({hp}) + (({s1v}) - ({sp})) / (({spp}) - ({sp})) * (({hpp}) - ({hp})))"
        q = make_calculated_question(
            'Cw04_Zad4_5_Moc_wyzsze_parametry',
            '<p><b>Ćw. 4 — Analiza Wariantowa: wyższe parametry pary</b></p>'
            '<p>Dotychczas turbina pracowała parą \\(p_1 =\\) <b>{p1t}</b> bar, \\(t_1 =\\) <b>{t1t}</b> °C (Zad. 4.3). '
            'W wariancie „Modernizacja Plus” kocioł dostarcza parę o ciśnieniu wyższym o <b>4 bar</b> i temperaturze '
            'wyższej o <b>50 K</b>: \\(p_1\\prime = p_1 + 4\\) bar, \\(t_1\\prime = t_1 + 50\\) °C. '
            'Wylot turbiny nadal \\(p_2 =\\) <b>{p2t}</b> bar, strumień pary \\(\\dot{{m}} =\\) <b>{mdt}</b> kg/s.</p>'
            '<p>Odczytaj \\(h_1\\prime, s_1\\prime\\) z Załącznika B (interpolacja liniowa w temperaturze i między '
            'sąsiednimi kolumnami ciśnień), a \\(h\\prime, h\\prime\\prime, s\\prime, s\\prime\\prime\\) dla \\(p_2\\) '
            'z Załącznika A.</p>'
            '<p><b>Oblicz idealną moc turbiny w tym wariancie \\(N_{{t,var}}\\) [kW]:</b></p>'
            '<p>$$x_{{2s}} = \\frac{s_1\\prime - s\\prime}{s\\prime\\prime - s\\prime}, \\qquad '
            'h_{{2s}} = h\\prime + x_{{2s}} \\cdot (h\\prime\\prime - h\\prime), \\qquad '
            'N_{{t,var}} = \\dot{{m}} \\cdot (h_1\\prime - h_{{2s}})$$</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{{mdt}} * (({h1v}) - {h2sv})",
            tolerance=TOL_TAB, correctanswerlength=1,
            generalfeedback='<p>Jak w Zad. 4.3, tylko z nowym punktem 1 (np. 14 bar, 300 °C: \\(h_1\\prime = 3041\\) kJ/kg, '
            '\\(s_1\\prime = 6.955\\) kJ/(kg·K)); dla 2 bar: \\(x_{{2s}} \\approx 0.969\\), \\(h_{{2s}} \\approx 2638\\) kJ/kg, '
            '\\(N_{{t,var}} \\approx 0.5556 \\cdot 402.6 \\approx 224\\) kW zamiast 175 kW (Zad. 4.5 na slajdach). '
            'Wyższe parametry pary = większy spadek entalpii w turbinie = większa moc przy tym samym strumieniu.</p>')
        for var in ['mdt', 'p1t', 't1t', 'p2t']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 4.6 (cd.): sprawność eta_t = N_t / Q_kotla
    if find_question(root, 'Cw04_Zad4_6_Sprawnosc_eta_t') is None:
        q = make_calculated_question(
            'Cw04_Zad4_6_Sprawnosc_eta_t',
            '<p><b>Ćw. 4 — Sprawność \\(\\eta_t\\) a sprawność Carnota</b></p>'
            '<p>Para z kotła: \\(p_1 =\\) <b>{p1t}</b> bar, \\(t_1 =\\) <b>{t1t}</b> °C, \\(\\dot{{m}} =\\) <b>{mdt}</b> kg/s, '
            'rozpręża się izentropowo w idealnej turbinie do \\(p_2 =\\) <b>{p2t}</b> bar (moc \\(N_t\\) jak w Zad. 4.3). '
            'Woda zasilająca kocioł ma temperaturę \\(t_{{zas}} =\\) <b>{tz}</b> °C '
            '(\\(h_{{zas}} \\approx 4.19 \\cdot t_{{zas}}\\) kJ/kg, jak w Zad. 3.2).</p>'
            '<p><b>Oblicz sprawność wytwarzania pracy \\(\\eta_t\\) [%] – stosunek idealnej mocy turbiny do mocy '
            'cieplnej kotła:</b></p>'
            '<p>$$\\eta_t = \\frac{{N_t}}{\\dot{{Q}}_{{kotła}}} \\cdot 100 = '
            '\\frac{\\dot{{m}} \\cdot (h_1 - h_{{2s}})}{\\dot{{m}} \\cdot (h_1 - h_{{zas}})} \\cdot 100\\ \\%$$</p>'
            '<p>Porównaj wynik ze sprawnością Carnota \\(\\eta_C = 1 - T_L/T_H\\) dla \\(t_1\\) i otoczenia 20 °C (Zad. 4.6).</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"({{mdt}} * (({h1}) - {h2s})) / ({{mdt}} * (({h1}) - 4.19 * {{tz}})) * 100",
            tolerance=TOL_TAB, correctanswerlength=1,
            generalfeedback='<p>1. \\(N_t = \\dot{{m}}(h_1 - h_{{2s}})\\) – jak w Zad. 4.3 (np. 175.3 kW).<br>'
            '2. \\(\\dot{{Q}}_{{kotła}} = \\dot{{m}}(h_1 - 4.19\\,t_{{zas}})\\) – jak w Zad. 3.2 (np. 1495 kW).<br>'
            '3. \\(\\eta_t = N_t/\\dot{{Q}}_{{kotła}} \\approx 11.7\\ \\%\\) wobec \\(\\eta_C \\approx 44\\ \\%\\) (Zad. 4.6 na slajdach). '
            'Turbina jest przeciwprężna – nie rozpręża pary do temperatury otoczenia; reszta mocy kotła trafia '
            'do wymiennika jako ciepło użytkowe (kogeneracja).</p>')
        for var in ['mdt', 'p1t', 't1t', 'p2t', 'tz']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 4.7: dodatkowe zużycie gazu w kotle po zainstalowaniu turbiny (uwaga do Raportu 4)
    if find_question(root, 'Cw04_Zad4_7_Dodatkowy_gaz') is None:
        q = make_calculated_question(
            'Cw04_Zad4_7_Dodatkowy_gaz',
            '<p><b>Ćw. 4 — Kogeneracja: dodatkowe zużycie gazu</b></p>'
            '<p>Para z kotła: \\(p_1 =\\) <b>{p1t}</b> bar, \\(t_1 =\\) <b>{t1t}</b> °C, \\(\\dot{{m}} =\\) <b>{mdt}</b> kg/s, '
            'rozpręża się w turbinie o sprawności izentropowej \\(\\eta_{{is}} =\\) <b>{eis}</b> do \\(p_2 =\\) <b>{p2t}</b> bar '
            '(rzeczywista moc \\(N_r\\) jak w Zad. 4.4). Turbina zamienia część entalpii pary na pracę, więc do wymiennika '
            'ciepła trafia o \\(N_r\\) mniej ciepła niż przy dławieniu na zaworze. Aby utrzymać ciepło dla procesu, '
            'kocioł o sprawności \\(\\eta_k =\\) <b>{ek}</b> musi spalić więcej gazu '
            '(\\(W_d = 50\\,000\\) kJ/kg, \\(\\rho_{{gaz}} = 0.7\\) kg/m³ – jak w Zad. 3.3).</p>'
            '<p><b>Oblicz dodatkowe zużycie gazu \\(\\Delta\\dot{{V}}_{{gaz}}\\) [m³/h]:</b></p>'
            '<p>$$\\Delta\\dot{{V}}_{{gaz}} = \\frac{{N_r}}{\\eta_k \\cdot W_d \\cdot \\rho_{{gaz}}} \\cdot 3600$$</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{{eis}} * {{mdt}} * (({h1}) - {h2s}) / ({{ek}} * 50000 * 0.7) * 3600",
            tolerance=TOL_TAB, correctanswerlength=1,
            generalfeedback='<p>1. \\(N_r = \\eta_{{is}} \\cdot \\dot{{m}} \\cdot (h_1 - h_{{2s}})\\) [kW] (Zad. 4.4, np. 140 kW).<br>'
            '2. Metodą z Zad. 3.3: \\(\\Delta\\dot{{V}}_{{gaz}} = N_r/(\\eta_k W_d \\rho_{{gaz}}) \\cdot 3600\\) '
            '(np. \\(140/(0.9 \\cdot 50\\,000 \\cdot 0.7) \\cdot 3600 \\approx 16\\) m³/h – uwaga do Raportu 4). '
            'Ten koszt gazu trzeba uwzględnić w ocenie opłacalności kogeneracji obok zysku ze sprzedaży prądu.</p>')
        for var in ['mdt', 'eis', 'p1t', 't1t', 'p2t', 'ek']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 4.1: stan pary po rozprężaniu izentropowym – 3 stałe warianty (multichoice).
    # Poprawne odpowiedzi z CoolProp (IAPWS-95) i z Załączników A/B:
    #   A: 10 bar, 250 °C → 2 bar: s1 = 6.926 < s''(2 bar) = 7.127  → mokra (x = 0.964)
    #   B:  5 bar, 300 °C → 1 bar: s1 = 7.461 > s''(1 bar) = 7.359  → przegrzana
    #   C:  8 bar, 300 °C → 1 bar: s1 = 7.234 < s''(1 bar) = 7.359  → mokra (x = 0.980)
    ODP = {'mokra': 'Para mokra (\\(0 < x_2 < 1\\) – mieszanina cieczy i pary)',
           'sucha': 'Para nasycona sucha (\\(x_2 = 1\\))',
           'przegrzana': 'Para przegrzana (\\(t_2 > t_s(p_2)\\), stopień suchości nie istnieje)'}
    WARIANTY = [
        ('A', 10, 250, 2, '6.926', '1.530', '7.127', 'mokra',
         '\\(s\\prime < s_1 < s\\prime\\prime\\) → para mokra, \\(x_2 = (6.926 - 1.530)/(7.127 - 1.530) \\approx 0.964\\) (przykład ze slajdu, Zad. 4.1).'),
        ('B', 5, 300, 1, '7.461', '1.303', '7.359', 'przegrzana',
         '\\(s_1 > s\\prime\\prime\\) → punkt 2s leży na prawo od krzywej nasycenia: para przegrzana, '
         'temperaturę \\(t_2\\) odczytuje się z Załącznika B (kolumna 1 bar) dla \\(s = 7.461\\) kJ/(kg·K).'),
        ('C', 8, 300, 1, '7.234', '1.303', '7.359', 'mokra',
         '\\(s\\prime < s_1 < s\\prime\\prime\\) → para mokra, \\(x_2 = (7.234 - 1.303)/(7.359 - 1.303) \\approx 0.98\\) – prawie sucha.'),
    ]
    for lit, p1, t1, p2, s1, sp_, spp_, ok, wyj in WARIANTY:
        name = f'Cw04_Zad4_1_Stan_pary_{lit}'
        if find_question(root, name) is not None:
            continue
        q = make_multichoice_question(
            name,
            '<p><b>Ćw. 4 — Rozprężanie izentropowe: stan pary za turbiną idealną</b></p>'
            f'<p>Para przegrzana o parametrach \\(p_1 = {p1}\\) bar, \\(t_1 = {t1}\\) °C rozpręża się '
            f'izentropowo (\\(s_2 = s_1\\)) w idealnej turbinie do ciśnienia \\(p_2 = {p2}\\) bar.</p>'
            '<p>Odczytaj \\(s_1\\) z Załącznika B oraz \\(s\\prime\\) i \\(s\\prime\\prime\\) dla \\(p_2\\) '
            'z Załącznika A i porównaj.</p>'
            '<p><b>W jakim stanie jest para na wylocie z turbiny?</b></p>',
            [(ODP['mokra'], 100 if ok == 'mokra' else 0),
             (ODP['sucha'], 100 if ok == 'sucha' else 0),
             (ODP['przegrzana'], 100 if ok == 'przegrzana' else 0)],
            generalfeedback=f'<p>Załącznik B: \\(s_1 = {s1}\\) kJ/(kg·K) dla {p1} bar, {t1} °C. '
            f'Załącznik A, wiersz {p2} bar: \\(s\\prime = {sp_}\\), \\(s\\prime\\prime = {spp_}\\) kJ/(kg·K).<br>'
            + wyj + '</p>')
        changes += append_question(root, q)

    save(tree, filepath, changes)
    return True


def process_cw05(filepath):
    """Cw05 — odzysk ciepła: add Zad 5.4 (egzergia spalin, sprawność egzergetyczna),
    5.6 (kaskada wymienników) and 5.7 (entropia otoczenia); existing questions are kept.
    Wszystkie wzory zamknięte (bilanse, logarytmy) – tolerancja 2 %."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    changes = 0
    xml_dir = os.path.dirname(filepath)
    template = find_question(root, 'Cw05_Zad5_3_Gouy_Stodola')

    # składniki wspólne (SI: W, W/K; temperatury w K)
    Q = "{ms5} * 1000 * ({tsi} - {tso})"
    Tin, Tout, Tmid, T0 = "({tsi} + 273.15)", "({tso} + 273.15)", "({tsm5} + 273.15)", "({T05} + 273.15)"
    Tm = f"(({{tsi}} - {{tso}}) / log({Tin} / {Tout}))"                 # średnia temperatura termodynamiczna spalin
    bmax = f"(({Q}) * (1 - {T0} / {Tm}) / 1000)"                        # kW
    dSs = f"({{ms5}} * 1000 * log({Tout} / {Tin}))"                     # W/K, < 0
    dSw = f"(({Q}) / ({{two5}} - {{twi5}}) * log(({{two5}} + 273.15) / ({{twi5}} + 273.15)))"  # W/K, > 0
    bstr = f"({T0} * ({dSs} + {dSw}) / 1000)"                           # kW (Zad. 5.3)

    spaliny = ('<p>Spaliny: \\(\\dot{{m}}_s =\\) <b>{ms5}</b> kg/s, \\(t_{{in}} =\\) <b>{tsi}</b> °C, '
               '\\(t_{{out}} =\\) <b>{tso}</b> °C, \\(c_s = 1000\\) J/(kg·K). ')
    otoczenie = '<p>Temperatura otoczenia (hali): \\(t_0 =\\) <b>{T05}</b> °C (\\(T_0 = t_0 + 273.15\\) K).</p>'
    woda = '<p>Woda: \\(t_{{w,in}} =\\) <b>{twi5}</b> °C, \\(t_{{w,out}} =\\) <b>{two5}</b> °C, \\(c_w = 4190\\) J/(kg·K).</p>'
    kelwiny = '<p>Temperatury w kelwinach (\\(T = t + 273.15\\)). Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>'

    # Zad 5.4: egzergia ciepła spalin (silnik Carnota dla średniej temperatury termodynamicznej)
    if find_question(root, 'Cw05_Zad5_4_Egzergia_spalin') is None:
        q = make_calculated_question(
            'Cw05_Zad5_4_Egzergia_spalin',
            '<p><b>Ćw. 5 — Egzergia Ciepła Spalin</b></p>' + spaliny + '</p>' + otoczenie +
            '<p>Spaliny oddają ciepło \\(\\dot{{Q}} = \\dot{{m}}_s c_s (t_{{in}} - t_{{out}})\\) nie w stałej temperaturze, '
            'lecz w zakresie \\(T_{{in}} \\rightarrow T_{{out}}\\). Silnik Carnota liczymy więc dla '
            '<b>średniej temperatury termodynamicznej</b> spalin:</p>'
            '<p>$$T_{{m,s}} = \\frac{T_{{in}} - T_{{out}}}{\\ln(T_{{in}}/T_{{out}})}, \\qquad '
            '\\eta_C = 1 - \\frac{{T_0}}{T_{{m,s}}}$$</p>'
            '<p><b>Oblicz egzergię ciepła spalin – maksymalną moc, jaką mógłby z niego uzyskać silnik Carnota '
            '\\(\\dot{{B}}_{{max}} = \\eta_C \\cdot \\dot{{Q}}\\) [kW]:</b></p>' + kelwiny,
            bmax,
            correctanswerlength=1,
            generalfeedback='<p>1. \\(\\dot{{Q}} = \\dot{{m}}_s c_s (t_{{in}} - t_{{out}})\\) (Zad. 5.1).<br>'
            '2. \\(T_{{m,s}} = (T_{{in}} - T_{{out}})/\\ln(T_{{in}}/T_{{out}})\\) (np. 573.15 → 423.15 K: 494.4 K).<br>'
            '3. \\(\\eta_C = 1 - T_0/T_{{m,s}}\\) (np. 40.7 %), \\(\\dot{{B}}_{{max}} = \\eta_C \\dot{{Q}}\\) '
            '(np. 61.05 kW dla 150 kW – Zad. 5.4 na slajdach). To samo daje '
            '\\(\\dot{{Q}} - T_0 |\\Delta\\dot{{S}}_{{spalin}}|\\), bo \\(|\\Delta\\dot{{S}}_{{spalin}}| = \\dot{{Q}}/T_{{m,s}}\\).</p>')
        for var in ['ms5', 'tsi', 'tso', 'T05']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 5.4 (cd.): sprawność egzergetyczna wymiennika psi = 1 - B_str/B_max
    if find_question(root, 'Cw05_Zad5_4b_Sprawnosc_egzergetyczna') is None:
        q = make_calculated_question(
            'Cw05_Zad5_4b_Sprawnosc_egzergetyczna',
            '<p><b>Ćw. 5 — Sprawność Egzergetyczna Wymiennika</b></p>' + spaliny + '</p>' + woda + otoczenie +
            '<p>Egzergia oddana przez spaliny \\(\\dot{{B}}_{{max}} = \\dot{{Q}} \\left(1 - T_0/T_{{m,s}}\\right)\\), '
            '\\(T_{{m,s}} = (T_{{in}} - T_{{out}})/\\ln(T_{{in}}/T_{{out}})\\) (Zad. 5.4), albo trafia do wody, albo jest niszczona '
            'w wymienniku: \\(\\dot{{B}}_{{str}} = T_0 \\cdot \\Delta\\dot{{S}}_{{gen}}\\) (Zad. 5.3), gdzie '
            '\\(\\Delta\\dot{{S}}_{{gen}} = \\Delta\\dot{{S}}_s + \\Delta\\dot{{S}}_w\\), '
            '\\(\\Delta\\dot{{S}}_i = \\dot{{m}}_i c_i \\ln(T_{{i,out}}/T_{{i,in}})\\), '
            '\\(\\dot{{m}}_w c_w = \\dot{{Q}}/\\Delta t_w\\) (bez zaokrągleń).</p>'
            '<p><b>Oblicz sprawność egzergetyczną wymiennika \\(\\psi\\) [%] – jaka część egzergii spalin trafia do wody:</b></p>'
            '<p>$$\\psi = \\left(1 - \\frac{\\dot{{B}}_{{str}}}{\\dot{{B}}_{{max}}}\\right) \\cdot 100\\ \\%$$</p>' + kelwiny,
            f"(1 - {bstr} / {bmax}) * 100",
            correctanswerlength=1,
            generalfeedback='<p>1. \\(\\dot{{B}}_{{max}} = \\dot{{Q}}(1 - T_0/T_{{m,s}})\\) (np. 61.05 kW, Zad. 5.4).<br>'
            '2. \\(\\dot{{B}}_{{str}} = T_0(\\Delta\\dot{{S}}_s + \\Delta\\dot{{S}}_w)\\) (np. 293.15 · 162.1 W/K = 47.52 kW, Zad. 5.3).<br>'
            '3. \\(\\psi = 1 - 47.52/61.05 \\approx 22.2\\ \\%\\) (Zad. 5.4 cd. na slajdach): tylko ok. 1/5 egzergii spalin '
            'trafia do ciepłej wody, reszta jest niszczona przez nieodwracalność wymiany ciepła przy dużej różnicy temperatur. '
            'Wynik nie zależy od \\(\\dot{{m}}_s\\).</p>')
        for var in ['ms5', 'tsi', 'tso', 'twi5', 'two5', 'T05']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 5.6: kaskada dwóch wymienników – całkowita generacja entropii
    if find_question(root, 'Cw05_Zad5_6_Kaskada_entropia') is None:
        QA = "{ms5} * 1000 * ({tsi} - {tsm5})"
        QB = "{ms5} * 1000 * ({tsm5} - {tso})"
        SA = (f"({{ms5}} * 1000 * log({Tmid} / {Tin}) + ({QA}) / ({{two5}} - {{twi5}})"
              f" * log(({{two5}} + 273.15) / ({{twi5}} + 273.15)))")
        SB = (f"({{ms5}} * 1000 * log({Tout} / {Tmid}) + ({QB}) / ({{twb5}} - 15)"
              f" * log(({{twb5}} + 273.15) / (15 + 273.15)))")
        q = make_calculated_question(
            'Cw05_Zad5_6_Kaskada_entropia',
            '<p><b>Ćw. 5 — Kaskada Wymienników: generacja entropii</b></p>'
            '<p>Spaliny \\(\\dot{{m}}_s =\\) <b>{ms5}</b> kg/s (\\(c_s = 1000\\) J/(kg·K)) przepływają kolejno przez dwa wymienniki:</p>'
            '<ul><li><b>Wymiennik A:</b> spaliny <b>{tsi}</b> → <b>{tsm5}</b> °C, podgrzewanie wody kotłowej od '
            '<b>{twi5}</b> do <b>{two5}</b> °C;</li>'
            '<li><b>Wymiennik B:</b> spaliny <b>{tsm5}</b> → <b>{tso}</b> °C, podgrzewanie wody użytkowej od '
            '<b>15</b> do <b>{twb5}</b> °C.</li></ul>'
            '<p>\\(c_w = 4190\\) J/(kg·K). Dla każdego stopnia wyznacz moc \\(\\dot{{Q}} = \\dot{{m}}_s c_s \\Delta t_s\\), '
            'pojemność strumienia wody \\(\\dot{{m}}_w c_w = \\dot{{Q}}/\\Delta t_w\\) (bez zaokrągleń) i generację entropii jak w Zad. 5.2:</p>'
            '<p>$$\\Delta\\dot{{S}}_{{gen}} = \\dot{{m}}_s c_s \\ln\\frac{T_{{s,out}}}{T_{{s,in}}} + '
            '\\dot{{m}}_w c_w \\ln\\frac{T_{{w,out}}}{T_{{w,in}}}$$</p>'
            '<p><b>Oblicz całkowitą generację entropii kaskady '
            '\\(\\Delta\\dot{{S}}_{{gen,A}} + \\Delta\\dot{{S}}_{{gen,B}}\\) [W/K]:</b></p>' + kelwiny,
            f"{SA} + {SB}",
            correctanswerlength=1,
            generalfeedback='<p>Stopień A: \\(\\dot{{Q}}_A = \\dot{{m}}_s c_s (t_{{in}} - t_{{m}})\\), '
            '\\(\\Delta\\dot{{S}}_{{gen,A}} = \\dot{{m}}_s c_s \\ln(T_m/T_{{in}}) + (\\dot{{Q}}_A/\\Delta t_{{w,A}}) \\ln(T_{{w,out,A}}/T_{{w,in,A}})\\); '
            'stopień B analogicznie ze spalinami \\(t_m \\rightarrow t_{{out}}\\) i wodą 15 °C → \\(t_{{w,out,B}}\\). '
            'Dla danych ze slajdu (300 → 220 → 150 °C, woda 20 → 90 i 15 → 50 °C): A – 94.4 W/K, B – 76.2 W/K, razem 170.6 W/K, '
            'czyli <b>więcej</b> niż jeden wymiennik 20 → 80 °C (162.1 W/K, Zad. 5.6 na slajdach). Kaskada dopasowuje poziom '
            'temperatury do odbiorcy, ale ciepło oddane wodzie o niskiej średniej temperaturze (stopień B) generuje dużo entropii.</p>')
        for var in ['ms5', 'tsi', 'tso', 'twi5', 'two5']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        # nowe zmienne: temperatura spalin między stopniami (tso <= 180 < tsm5 < 250 <= tsi)
        # i temperatura wody użytkowej za stopniem B
        q.find('dataset_definitions').append(make_dataset_definition('tsm5', 190, 240, 0, seed=2056))
        q.find('dataset_definitions').append(make_dataset_definition('twb5', 45, 55, 0, seed=2057))
        changes += append_question(root, q)

    # Zad 5.7: entropia atmosfery przy stygnięciu spalin z komina
    if find_question(root, 'Cw05_Zad5_7_Entropia_otoczenia') is None:
        q = make_calculated_question(
            'Cw05_Zad5_7_Entropia_otoczenia',
            '<p><b>Ćw. 5 — Entropia a Otoczenie (strata kominowa)</b></p>'
            '<p>Spaliny za wymiennikiem: \\(\\dot{{m}}_s =\\) <b>{ms5}</b> kg/s, \\(t_{{out}} =\\) <b>{tso}</b> °C, '
            '\\(c_s = 1000\\) J/(kg·K), uchodzą kominem i stygną w atmosferze do temperatury otoczenia '
            '\\(t_{{atm}} =\\) <b>{T05}</b> °C.</p>'
            '<p>Ciepło tracone przez komin \\(\\dot{{Q}}_{{komin}} = \\dot{{m}}_s c_s (t_{{out}} - t_{{atm}})\\) atmosfera '
            'przyjmuje w stałej temperaturze \\(T_{{atm}}\\).</p>'
            '<p><b>Oblicz przyrost strumienia entropii atmosfery \\(\\Delta\\dot{{S}}_{{atm}}\\) [W/K]:</b></p>'
            '<p>$$\\Delta\\dot{{S}}_{{atm}} = \\frac{\\dot{{Q}}_{{komin}}}{T_{{atm}}}$$</p>' + kelwiny,
            "{ms5} * 1000 * ({tso} - {T05}) / ({T05} + 273.15)",
            correctanswerlength=1,
            generalfeedback='<p>\\(\\dot{{Q}}_{{komin}} = \\dot{{m}}_s c_s (t_{{out}} - t_{{atm}})\\) (np. 130 kW), '
            '\\(\\Delta\\dot{{S}}_{{atm}} = \\dot{{Q}}_{{komin}}/T_{{atm}}\\) (np. 130 000/293.15 = 443.5 W/K, Zad. 5.7 na slajdach). '
            'Same spaliny tracą przy tym \\(\\dot{{m}}_s c_s \\ln(T_{{atm}}/T_{{out}})\\) (np. −367 W/K), więc przy stygnięciu '
            'w atmosferze generuje się różnica (ok. 76 W/K). Obniżenie \\(t_{{out}}\\) (kocioł kondensacyjny) zmniejsza '
            'zarówno stratę kominową, jak i eksport entropii.</p>')
        for var in ['ms5', 'tso', 'T05']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

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
    # Studenci odczytują h2 z wykresu p-h: przy l_k = 19–33 kJ/kg błąd odczytu ±1–1.5 kJ/kg
    # daje do ~10 % na EER/N/COP i ~1.5 % na q_o (strumień masy) – stąd tolerancje.
    for qname, tol in (('Cw06_Zad6_1_EER', '0.1'), ('Cw06_Zad6_2_Moc_sprezarki', '0.1'),
                       ('Cw06_Zad6_4_COP_pompa_ciepla', '0.1'), ('Cw06_Zad6_3_Strumien_masy', '0.03'),
                       ('Cw06_Zad6_7_Predkosc_rurociagu', '0.03'), ('Cw06_Zad6_6_EER_R290', '0.06')):
        q = find_question(root, qname)
        if q is not None:
            t = q.find('answer/tolerance')
            if t is not None and t.text != tol:
                t.text = tol
                changes += 1

    # Zad 6.6 — R134a vs R290
    if find_question(root, 'Cw06_Zad6_6_EER_R290') is None:
        q66 = make_calculated_question(
            'Cw06_Zad6_6_EER_R290',
            '<p><b>Ćw. 6 — Porównanie Czynników: EER dla R290 (propan)</b></p>'
            '<p>Obieg chłodniczy teoretyczny z propanem (R290) pracuje między temperaturą '
            'parowania \\(t_o =\\) <b>{to6}</b> °C a temperaturą skraplania \\(t_k =\\) <b>{tk6}</b> °C '
            '(bez przegrzania i dochłodzenia, \\(h_4 = h_3\\)).</p>'
            "<p>Entalpie odczytaj jak w Zad. 6.6: \\(h_1 = h''(t_o)\\), \\(s_1 = s''(t_o)\\) i "
            "\\(h_3 = h_4 = h'(t_k)\\) z tablicy nasycenia R290 (Załącznik D), \\(h_2\\) z wykresu p-h R290 "
            '(Załącznik G) lub z tablicy pary przegrzanej R290 – na przecięciu izentropy \\(s_1\\) '
            'z izobarą \\(p_k = p_s(t_k)\\).</p>'
            '<p><b>Oblicz EER dla R290:</b></p>'
            '<p>$$EER = \\frac{{q_o}}{{l_k}} = \\frac{h_1 - h_4}{h_2 - h_1}$$</p>'
            '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>',
            f"(({H1_R290}) - ({H3_R290})) / (({H2S_R290}) - ({H1_R290}))",
            tolerance=0.06, correctanswerlength=2,
            generalfeedback='<p>\\(q_o = h_1 - h_3\\), \\(l_k = h_2 - h_1\\), EER = \\(q_o / l_k\\). '
            'Dla R290 EER jest praktycznie taki sam jak dla R134a (różnica ok. 2 %), ale \\(q_o\\) jest ok. 2 razy '
            'większe – potrzebny strumień czynnika jest prawie o połowę mniejszy. O wyborze decydują GWP i palność '
            '(R290 – klasa A3).</p>')
        template = find_question(root, 'Cw06_Zad6_1_EER')
        for var in ['to6', 'tk6']:
            copy_dataset_item(root, var, q66, preferred=template,
                              xml_dir=os.path.dirname(filepath))
        root.append(q66)
        changes += 1
        print("  + Added Cw06_Zad6_6_EER_R290")

    template = find_question(root, 'Cw06_Zad6_2_Moc_sprezarki')
    xml_dir = os.path.dirname(filepath)
    odczyt = ('<p>Entalpie obiegu teoretycznego odczytaj jak w Zad. 6.1: \\(h_1 = h\\prime\\prime(t_o)\\) i '
              '\\(s_1 = s\\prime\\prime(t_o)\\) z tablicy nasycenia R134a (Załącznik C, interpolacja liniowa między wierszami), '
              '\\(h_3 = h_4 = h\\prime(t_k)\\) z tej samej tablicy, \\(h_2\\) z wykresu p-h (Załącznik F) na przecięciu '
              'izentropy \\(s_1\\) z izobarą \\(p_k = p_s(t_k)\\). Niepewność odczytu z wykresu jest uwzględniona '
              'w tolerancji odpowiedzi.</p>')
    qo = f"(({H1_R134A}) - ({H3_R134A}))"
    qsk = f"(({H2S_R134A}) - ({H3_R134A}))"

    # Zad 6.2: jednostkowe ciepło skraplania q_sk = h2 - h3.
    # Odczyt: h2 z wykresu ±1.5 kJ/kg, h3 z tablicy ±0.5 → ±2/163 = 1.2 % → tolerancja 0.03 (jak w 6.3).
    if find_question(root, 'Cw06_Zad6_2_Cieplo_skraplania') is None:
        q = make_calculated_question(
            'Cw06_Zad6_2_Cieplo_skraplania',
            '<p><b>Ćw. 6 — Bilans Energetyczny: ciepło skraplania</b></p>'
            '<p>\\(t_o =\\) <b>{to6}</b> °C, \\(t_k =\\) <b>{tk6}</b> °C. Czynnik R134a, obieg teoretyczny '
            '(bez przegrzania i dochłodzenia, \\(h_4 = h_3\\)).</p>' + odczyt +
            '<p><b>Oblicz jednostkowe ciepło skraplania (odpadowe) \\(q_{{sk}}\\) [kJ/kg]:</b></p>'
            '<p>$$q_{{sk}} = h_2 - h_3 = q_o + l_k$$</p>'
            '<p>Sprawdź I zasadę: \\(q_o + l_k = (h_1 - h_4) + (h_2 - h_1) = q_{{sk}}\\).</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            qsk,
            tolerance=0.03, correctanswerlength=1,
            generalfeedback='<p>\\(q_{{sk}} = h_2 - h_3\\) (np. 425 − 256 = 169 kJ/kg dla 2/40 °C, Zad. 6.2 na slajdach) '
            '– tyle ciepła na 1 kg czynnika oddaje skraplacz na dachu; równa się sumie \\(q_o + l_k = 144 + 25\\).</p>')
        for var in ['to6', 'tk6']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 6.3: moc skraplacza Q_sk = Qo + N = m * q_sk.
    # Odczyt: q_sk ±1.2 %, q_o (h1 - h3 z tablic) ±1 % → ok. 2.5 % na iloczynie; przez N = Qo/EER
    # (EER z wykresu ±10 %, N/Q_sk <= 0.2) – ok. 2 %. Tolerancja 0.05.
    if find_question(root, 'Cw06_Zad6_3_Moc_skraplacza') is None:
        q = make_calculated_question(
            'Cw06_Zad6_3_Moc_skraplacza',
            '<p><b>Ćw. 6 — Moc Skraplacza (ciepło wyrzucane na dach)</b></p>'
            '<p>\\(\\dot{{Q}}_o =\\) <b>{Qo6}</b> kW, \\(t_o =\\) <b>{to6}</b> °C, \\(t_k =\\) <b>{tk6}</b> °C. '
            'Czynnik R134a, obieg teoretyczny.</p>' + odczyt +
            '<p><b>Oblicz strumień ciepła oddawanego w skraplaczu \\(\\dot{{Q}}_{{sk}}\\) [kW]:</b></p>'
            '<p>$$\\dot{{m}} = \\frac{\\dot{{Q}}_o}{h_1 - h_4}, \\qquad N = \\dot{{m}} (h_2 - h_1), \\qquad '
            '\\dot{{Q}}_{{sk}} = \\dot{{Q}}_o + N = \\dot{{m}} \\cdot q_{{sk}}$$</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{{Qo6}} / {qo} * {qsk}",
            tolerance=0.05, correctanswerlength=1,
            generalfeedback='<p>\\(\\dot{{m}} = \\dot{{Q}}_o/q_o\\) (np. 300/144 = 2.08 kg/s), \\(N = \\dot{{m}} l_k\\) (np. 52 kW), '
            '\\(\\dot{{Q}}_{{sk}} = \\dot{{Q}}_o + N\\) (np. 352 kW) \\(= \\dot{{m}} q_{{sk}} = 2.08 \\cdot 169\\) '
            '(Zad. 6.3 na slajdach). Skraplacz musi oddać do otoczenia ciepło odebrane z hali <b>plus</b> pracę sprężarki.</p>')
        for var in ['Qo6', 'to6', 'tk6']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 6.7 (cz. 2): średnica rurociągu ssawnego dla zadanej prędkości w (nowa zmienna wr6 = 8..12 m/s).
    # Odczyt: m ±1.5 % (tablice), v1 ±1 % → pod pierwiastkiem ok. 1.3 % na d → tolerancja 0.03 (jak w 6.7).
    if find_question(root, 'Cw06_Zad6_7b_Srednica_rurociagu') is None:
        q = make_calculated_question(
            'Cw06_Zad6_7b_Srednica_rurociagu',
            '<p><b>Ćw. 6 — Dobór Średnicy Rurociągu Ssawnego</b></p>'
            '<p>\\(\\dot{{Q}}_o =\\) <b>{Qo6}</b> kW, \\(t_o =\\) <b>{to6}</b> °C, \\(t_k =\\) <b>{tk6}</b> °C. Czynnik R134a. '
            'Strumień masy jak w zad. 6.3: \\(\\dot{{m}} = \\dot{{Q}}_o / (h_1 - h_3)\\), \\(h_1 = h\\prime\\prime(t_o)\\), '
            '\\(h_3 = h\\prime(t_k)\\); objętość właściwą pary nasyconej na ssaniu \\(v_1 = v\\prime\\prime(t_o)\\) odczytaj '
            'z tablicy nasycenia R134a (Załącznik C, interpolacja między wierszami).</p>'
            '<p>Prędkość czynnika w rurociągu ssawnym ma wynosić \\(w =\\) <b>{wr6}</b> m/s (zakres dopuszczalny 8–15 m/s).</p>'
            '<p><b>Oblicz wymaganą średnicę wewnętrzną rurociągu \\(d\\) [mm]:</b></p>'
            '<p>$$\\dot{{V}} = \\dot{{m}} \\cdot v_1, \\qquad d = \\sqrt{\\frac{4 \\dot{{V}}}{\\pi w}}$$</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"sqrt(4 * ({{Qo6}} / {qo}) * ({V_R134A}) / (3.14159265 * {{wr6}})) * 1000",
            tolerance=0.03, correctanswerlength=1,
            generalfeedback='<p>\\(\\dot{{V}} = \\dot{{m}} v_1\\) (np. 2.08 · 0.065 = 0.135 m³/s), '
            '\\(d = \\sqrt{4\\dot{{V}}/(\\pi w)}\\) (np. dla 12 m/s: 0.120 m = 120 mm, Zad. 6.7 na slajdach). '
            'Za mała rura → za duża prędkość, spadki ciśnienia i niższy EER; za duża (poniżej 8 m/s) → zły powrót oleju.</p>')
        for var in ['Qo6', 'to6', 'tk6']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        q.find('dataset_definitions').append(make_dataset_definition('wr6', 8, 12, 0, seed=2067))
        changes += append_question(root, q)

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

    # ---- Pytania z wykresem h-X (0.1 MPa, jak na slajdach Ć7). Klucz ze wzorów zamkniętych
    #      (Karta Wzorów): p = 100 kPa, p_s(t) z równania Magnusa (nad wodą; dla t < 0 °C nad lodem –
    #      wykres i CoolProp używają nasycenia nad lodem), X = 0.622 phi p_s/(p - phi p_s) [kg/kg],
    #      h = 1.005 t + X (2501 + 1.86 t) [kJ/kg], punkt rosy z odwrócenia Magnusa.
    #      Wykres obejmuje -10..+60 °C, więc zima na wykresie: nowa zmienna tzw7 = -10..-3 °C
    #      (tzz sięga -15 °C – poza wykresem). Wilgotność hali phi_W = 50 % (wymaganie hali)
    #      poza Zad. 7.4, gdzie jest zmienną phiw7. Tolerancje policzone dla odczytu
    #      ±0.3 g/kg na X i ±1 kJ/kg na h (patrz komentarze przy pytaniach).
    template = find_question(root, 'Cw07_Zad8_2_Moc_chlodnicy_lato')
    xml_dir = os.path.dirname(filepath)
    P_PA = 100000
    psw = lambda t: f"(610.94 * exp(17.625 * {t} / ({t} + 243.04)))"          # Pa, nad wodą
    psi = lambda t: f"(611.21 * exp(22.587 * {t} / ({t} + 273.86)))"          # Pa, nad lodem (t < 0)
    xw = lambda ps, phi: f"(0.622 * ({phi}) / 100 * {ps} / ({P_PA} - ({phi}) / 100 * {ps}))"   # kg/kg
    hx = lambda t, x: f"(1.005 * {t} + {x} * (2501 + 1.86 * {t}))"               # kJ/kg
    md = "(1.2 * {Vd8} / 3600)"                                                  # kg/s
    XW = xw(psw('{tw8}'), '50')                                                  # hala, 50 %
    XZw = xw(psi('{tzw7}'), '{phiz7}')                                           # zima
    XZl = xw(psw('{tzl}'), '{phil7}')                                            # lato
    # punkt rosy dla zawilżenia X: p_w = X p/(0.622 + X), t_r = 243.04 ln(p_w/610.94)/(17.625 - ln(p_w/610.94))
    def tdp(x):
        lg = f"log(({x}) * {P_PA} / (0.622 + ({x})) / 610.94)"
        return f"(243.04 * {lg} / (17.625 - {lg}))"
    TR = tdp(XW)
    HR = hx(TR, XW)                                                              # stan R (nasycenie przy X_W)
    HZl = hx('{tzl}', XZl)

    wykres = ('Wartości odczytaj z wykresu h-X (wykres Molliera dla 0.1 MPa, jak na slajdach Ć7) albo oblicz ze wzorów '
              'z Karty Wzorów (powietrze wilgotne, \\(p = 100\\) kPa). Niepewność odczytu z wykresu jest uwzględniona '
              'w tolerancji odpowiedzi.')
    hala50 = '\\(t_W =\\) <b>{tw8}</b> °C, \\(\\varphi_W = 50\\ \\%\\)'

    # Zad 7.1: nawilżanie parowe zimą – ilość wody. dX = X_W - X_Z >= 4.6 g/kg; odczyt ±0.3 g/kg
    # na każdym X → ±0.42 g/kg (RSS) / 4.6 = 9 % → tolerancja 0.10.
    if find_question(root, 'Cw07_Zad7_1_Nawilzanie_zima') is None:
        q = make_calculated_question(
            'Cw07_Zad7_1_Nawilzanie_zima',
            '<p><b>Ćw. 7 — Proces Zimowy: nawilżanie parowe</b></p>'
            '<p>Powietrze zewnętrzne zimą: \\(t_Z =\\) <b>{tzw7}</b> °C, \\(\\varphi_Z =\\) <b>{phiz7}</b> %. '
            'Wymagania hali: ' + hala50 + '. Strumień centrali \\(\\dot{{V}} =\\) <b>{Vd8}</b> m³/h, \\(\\rho = 1.2\\) kg/m³.</p>'
            '<p>W centrali powietrze jest ogrzewane w nagrzewnicy wstępnej (\\(X = \\text{{const}}\\)) do \\(t_P = t_W\\), '
            'a następnie nawilżane parą (izotermicznie) do stanu nawiewu \\(N\\) o zawilżeniu \\(X_N = X_W\\) '
            '(bilans wilgoci hali ≈ 0, jak w Zad. 7.1).</p>'
            '<p>Odczytaj \\(X_Z\\) (punkt Z) i \\(X_W\\) (punkt W). ' + wykres + '</p>'
            '<p><b>Oblicz strumień pary wodnej doprowadzanej w nawilżaczu \\(\\dot{{m}}_w\\) [kg/h]:</b></p>'
            '<p>$$\\dot{{m}}_w = \\dot{{m}} \\cdot (X_W - X_Z), \\qquad \\dot{{m}} = \\rho \\dot{{V}}$$</p>'
            '<p>(\\(X\\) w kg/kg, \\(\\dot{{m}}\\) w kg/h). Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{md} * 3600 * ({XW} - {XZw})",
            tolerance=0.10, correctanswerlength=1,
            generalfeedback='<p>Np. Z (−10 °C, 90 %): \\(X_Z \\approx 1.4\\) g/kg; W (22 °C, 50 %): \\(X_W \\approx 8.3\\) g/kg; '
            '\\(\\dot{{m}} = 1.2 \\cdot 25\\,000 = 30\\,000\\) kg/h → \\(\\dot{{m}}_w = 30\\,000 \\cdot (8.3 - 1.4)/1000 \\approx 207\\) kg/h '
            '(proces Z → P → N z Zad. 7.1 na slajdach). Nagrzewnica zmienia tylko \\(t\\) (pionowo w górę na wykresie), '
            'nawilżacz parowy dodaje \\(X_W - X_Z\\) kg pary na kg powietrza suchego.</p>')
        for var in ['tw8', 'Vd8']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        q.find('dataset_definitions').append(make_dataset_definition('tzw7', -10, -3, 0, seed=2071))
        q.find('dataset_definitions').append(make_dataset_definition('phiz7', 80, 90, 0, seed=2072))
        changes += append_question(root, q)

    # Zad 7.4: punkt rosy powietrza w hali. t_r = 7.7..14.1 °C; odczyt X_W ±0.3 g/kg (4.5 % przy 6.6 g/kg)
    # → ±0.7 K na t_r, zaokrąglenie ±0.05 K → tolerancja NOMINALNA 0.8 K (względna byłaby 10 % przy 7.7 °C,
    # a 1.4 K przy 14 °C – temperatura w °C nie ma sensownej skali względnej).
    if find_question(root, 'Cw07_Zad7_4_Punkt_rosy') is None:
        XWv = xw(psw('{tw8}'), '{phiw7}')
        q = make_calculated_question(
            'Cw07_Zad7_4_Punkt_rosy',
            '<p><b>Ćw. 7 — Punkt Rosy: kontrola kondensacji na ścianie</b></p>'
            '<p>Powietrze w hali: \\(t_W =\\) <b>{tw8}</b> °C, \\(\\varphi_W =\\) <b>{phiw7}</b> %. Zimą temperatura '
            'wewnętrznej powierzchni ściany zewnętrznej spada do ok. 12 °C – czy pojawi się na niej rosa?</p>'
            '<p>Na wykresie h-X od punktu W idź w dół po \\(X = \\text{{const}}\\) do krzywej \\(\\varphi = 100\\ \\%\\) '
            '(punkt rosy R). ' + wykres + '</p>'
            '<p><b>Oblicz temperaturę punktu rosy \\(t_R\\) [°C] powietrza w hali.</b></p>'
            '<p>Ze wzorów: \\(p_w = \\varphi_W \\, p_s(t_W) = \\dfrac{X_W \\, p}{0.622 + X_W}\\), a \\(t_R\\) to temperatura, '
            'w której \\(p_s(t_R) = p_w\\) (odwrócenie wzoru na \\(p_s\\)).</p>'
            '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            tdp(XWv),
            tolerance=0.8, tolerancetype=2, correctanswerlength=1,
            generalfeedback='<p>Np. W (22 °C, 50 %): \\(X_W \\approx 8.3\\) g/kg → na krzywej nasycenia \\(t_R \\approx 11.1\\) °C '
            '(Zad. 7.4 na slajdach). Ze wzorów: \\(p_w = 0.5 \\cdot 2645 = 1322\\) Pa, '
            '\\(t_R = 243.04 \\ln(1322/610.94)/(17.625 - \\ln(1322/610.94)) \\approx 11.1\\) °C. '
            'Ściana (12 °C) jest cieplejsza od \\(t_R\\) → kondensacji nie ma, ale zapas jest mały; przy \\(|t_{{ściany}} - t_R| \\lt 0.5\\) K '
            'wynik jest „na granicy” (dokładność odczytu z wykresu).</p>')
        copy_dataset_item(root, 'tw8', q, preferred=template, xml_dir=xml_dir)
        q.find('dataset_definitions').append(make_dataset_definition('phiw7', 45, 55, 0, seed=2073))
        changes += append_question(root, q)

    # Zad 7.3 (lato): moc chłodnicy Q_ch = m (h_Z - h_R). h_Z - h_R >= 25 kJ/kg; odczyt h_Z ±1, h_R ±1,
    # X_W ±0.3 g/kg → t_R ±0.6 K → h_R ±1.4 → łącznie ±2 kJ/kg (RSS) / 25 = 8 % → tolerancja 0.08.
    if find_question(root, 'Cw07_Zad7_3_Moc_chlodnicy_hX') is None:
        q = make_calculated_question(
            'Cw07_Zad7_3_Moc_chlodnicy_hX',
            '<p><b>Ćw. 7 — Proces Letni: chłodnica z osuszaniem (wykres h-X)</b></p>'
            '<p>Powietrze zewnętrzne latem: \\(t_Z =\\) <b>{tzl}</b> °C, \\(\\varphi_Z =\\) <b>{phil7}</b> %. '
            'Wymagania hali: ' + hala50 + '. Strumień centrali \\(\\dot{{V}} =\\) <b>{Vd8}</b> m³/h, \\(\\rho = 1.2\\) kg/m³.</p>'
            '<p>Ponieważ \\(X_Z \\gt X_W\\), powietrze trzeba <b>osuszyć</b>: w chłodnicy jest ochładzane (przy \\(X = \\text{{const}}\\) '
            'do nasycenia, dalej wzdłuż \\(\\varphi = 100\\ \\%\\)) aż do punktu R na krzywej nasycenia o zawilżeniu '
            '\\(X_R = X_W\\) (punkt rosy aparatu), jak w Zad. 7.2.</p>'
            '<p>Odczytaj \\(h_Z\\) (punkt Z), \\(X_W\\) (punkt W) oraz \\(h_R\\) (punkt R: \\(\\varphi = 100\\ \\%\\), \\(X = X_W\\)). '
            + wykres + '</p>'
            '<p><b>Oblicz moc chłodnicy \\(\\dot{{Q}}_{{ch}}\\) [kW]:</b></p>'
            '<p>$$\\dot{{Q}}_{{ch}} = \\dot{{m}} \\cdot (h_Z - h_R), \\qquad \\dot{{m}} = \\rho \\dot{{V}} / 3600$$</p>'
            '<p>(\\(h\\) w kJ/kg powietrza suchego). Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{md} * ({HZl} - {HR})",
            tolerance=0.08, correctanswerlength=1,
            generalfeedback='<p>Np. Z (32 °C, 45 %): \\(h_Z \\approx 67\\) kJ/kg; W (22 °C, 50 %): \\(X_W \\approx 8.3\\) g/kg → '
            'R (\\(\\varphi = 100\\ \\%\\), 8.3 g/kg): \\(t_R \\approx 11.1\\) °C, \\(h_R \\approx 32\\) kJ/kg; '
            '\\(\\dot{{Q}}_{{ch}} = 8.33 \\cdot (67 - 32) \\approx 292\\) kW (Zad. 7.3 na slajdach). Ze wzorów: '
            '\\(h = 1.005\\,t + X(2501 + 1.86\\,t)\\), \\(t_R\\) z odwrócenia wzoru na \\(p_s\\) dla \\(p_w = X_W p/(0.622 + X_W)\\). '
            'Moc chłodnicy obejmuje ciepło jawne i utajone (wykraplanie wody) – stąd jest dużo większa niż '
            '\\(\\dot{{m}} c_p (t_Z - t_R)\\).</p>')
        for var in ['tzl', 'tw8', 'Vd8']:
            copy_dataset_item(root, var, q, preferred=template, xml_dir=xml_dir)
        q.find('dataset_definitions').append(make_dataset_definition('phil7', 55, 65, 0, seed=2074))
        changes += append_question(root, q)

    template7 = find_question(root, 'Cw07_Zad7_3_Moc_chlodnicy_hX')

    # Zad 7.7: kondensat latem. dX = X_Z - X_W >= 4.3 g/kg; odczyt ±0.42 g/kg (RSS) / 4.3 = 10 % → tolerancja 0.10.
    if find_question(root, 'Cw07_Zad7_7_Kondensat_lato') is None:
        q = make_calculated_question(
            'Cw07_Zad7_7_Kondensat_lato',
            '<p><b>Ćw. 7 — Ilość Kondensatu (lato)</b></p>'
            '<p>Powietrze zewnętrzne latem: \\(t_Z =\\) <b>{tzl}</b> °C, \\(\\varphi_Z =\\) <b>{phil7}</b> %. '
            'Wymagania hali: ' + hala50 + '. Strumień centrali \\(\\dot{{V}} =\\) <b>{Vd8}</b> m³/h, \\(\\rho = 1.2\\) kg/m³, '
            '\\(\\rho_w \\approx 1\\) kg/l.</p>'
            '<p>W chłodnicy powietrze jest osuszane do zawilżenia \\(X_R = X_W\\) (Zad. 7.2); wykroploną wodę trzeba '
            'odprowadzić do kanalizacji.</p>'
            '<p>Odczytaj \\(X_Z\\) (punkt Z) i \\(X_W\\) (punkt W). ' + wykres + '</p>'
            '<p><b>Oblicz strumień kondensatu \\(\\dot{{V}}_w\\) [l/h]:</b></p>'
            '<p>$$\\dot{{m}}_w = \\dot{{m}} \\cdot (X_Z - X_R), \\qquad \\dot{{m}} = \\rho \\dot{{V}}$$</p>'
            '<p>(\\(X\\) w kg/kg, \\(\\dot{{m}}\\) w kg/h). Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>',
            f"{md} * 3600 * ({XZl} - {XW})",
            tolerance=0.10, correctanswerlength=1,
            generalfeedback='<p>Np. \\(X_Z \\approx 13.5\\), \\(X_W \\approx 8.3\\) g/kg → \\(\\Delta X = 5.2\\) g/kg; '
            '\\(\\dot{{m}}_w = 8.33 \\cdot 0.0052 = 0.0433\\) kg/s ≈ 156 l/h (Zad. 7.7 na slajdach) – ok. 2.6 l/min wody, '
            'którą można po uzdatnieniu wykorzystać np. do nawilżania.</p>')
        for var in ['tzl', 'tw8', 'Vd8', 'phil7']:
            copy_dataset_item(root, var, q, preferred=template7, xml_dir=xml_dir)
        changes += append_question(root, q)

    # Zad 7.6: zawilżenie mieszaniny (recyrkulacja). X_M = 9.3..14.2 g/kg; odczyt ±0.3 g/kg na X_W i X_Z
    # → ±0.3 g/kg na X_M (3.2 % przy 9.3) → tolerancja 0.05.
    if find_question(root, 'Cw07_Zad7_6_Recyrkulacja_X') is None:
        q = make_calculated_question(
            'Cw07_Zad7_6_Recyrkulacja_X',
            '<p><b>Ćw. 7 — Recyrkulacja: zawilżenie mieszaniny (lato)</b></p>'
            '<p>Recyrkulacja: \\(r =\\) <b>{rec8}</b> % powietrza wraca z hali (stan W: ' + hala50 + '), '
            'reszta to powietrze zewnętrzne (stan Z: \\(t_Z =\\) <b>{tzl}</b> °C, \\(\\varphi_Z =\\) <b>{phil7}</b> %).</p>'
            '<p>Odczytaj \\(X_W\\) i \\(X_Z\\). ' + wykres + ' Punkt mieszaniny M leży na odcinku Z–W '
            '(reguła dźwigni) – bilans masy wilgoci:</p>'
            '<p>$$X_M = \\frac{{r}}{100} X_W + \\left(1 - \\frac{{r}}{100}\\right) X_Z$$</p>'
            '<p><b>Oblicz zawilżenie mieszaniny \\(X_M\\) [g/kg].</b> Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>',
            f"({{rec8}} / 100 * {XW} + (1 - {{rec8}} / 100) * {XZl}) * 1000",
            tolerance=0.05, correctanswerlength=2,
            generalfeedback='<p>Np. \\(r = 70\\ \\%\\), \\(X_W \\approx 8.3\\), \\(X_Z \\approx 13.5\\) g/kg: '
            '\\(X_M = 0.7 \\cdot 8.3 + 0.3 \\cdot 13.5 = 9.86\\) g/kg (Zad. 7.6 na slajdach; analogicznie '
            '\\(t_M = 25.0\\) °C). Do osuszenia zostaje \\(X_M - X_W = (1 - r/100)(X_Z - X_W)\\) – obciążenie osuszania '
            'maleje o \\(r\\) procent.</p>')
        for var in ['rec8', 'tw8', 'tzl', 'phil7']:
            copy_dataset_item(root, var, q, preferred=template7, xml_dir=xml_dir)
        changes += append_question(root, q)

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
        'Cw02': os.path.join(XML_DIR, 'Cw02_Bilans_Sprezarkowni_Calculated.xml'),
        'Cw03': os.path.join(XML_DIR, 'Cw03_Kociol_Parowy_Calculated.xml'),
        'Cw04': os.path.join(XML_DIR, 'Cw04_Obieg_Rankine_Calculated.xml'),
        'Cw05': os.path.join(XML_DIR, 'Cw05_Odzysk_Ciepla_Calculated.xml'),
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

        if name == 'Cw02':
            process_cw02(path)
        elif name == 'Cw03':
            process_cw03(path)
        elif name == 'Cw04':
            process_cw04(path)
        elif name == 'Cw05':
            process_cw05(path)
        elif name == 'Cw06':
            process_cw06(path)
        elif name == 'Cw07':
            process_cw07(path)

    print("\n✓ Done.")
