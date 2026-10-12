#!/usr/bin/env python3
"""Generate Moodle XML files for exam questions.
- egzamin_teoria.xml: multichoice + truefalse (40 questions)
- egzamin_zadania.xml: calculated type with 50 dataset items (randomized)
Category: egzamin

Usage: python generate_exam_xml.py [--out DIR]
(default output directory: the directory of this script)
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os, random, math, re, sys

random.seed(42)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
if '--out' in sys.argv:
    OUT_DIR = sys.argv[sys.argv.index('--out') + 1]
NUM_DATASETS = 50

# ============================================================
# HELPERS
# ============================================================
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

# Moodle traktuje każde {nazwa} w treści pytania calculated jako zmienną zbioru.
# Nawiasy klamrowe w LaTeX, które nie są zmiennymi (np. \dot{Q}, Q_{odpr}),
# trzeba podwoić ({{Q}}), inaczej Moodle zgłosi brak zbioru danych.
_BRACE_RE = re.compile(r'(?<!\{)\{([^\W\d]\w*)\}(?!\})')

def protect_latex_braces(text, variables):
    """Double {name} braces that are not dataset variables (LaTeX subscripts etc.)."""
    names = {v[0] for v in variables}
    return _BRACE_RE.sub(
        lambda m: m.group(0) if m.group(1) in names else '{{' + m.group(1) + '}}', text)

def precision_note(decimals):
    slowo = '1 miejsca' if decimals == 1 else f'{decimals} miejsc'
    return f'<p><i>Wynik podaj z dokładnością do {slowo} po przecinku.</i></p>'

def gen_values(vmin, vmax, decimals, n=NUM_DATASETS):
    """Generate n random values in [vmin, vmax] with given decimals."""
    step = 10**(-decimals) if decimals > 0 else 1
    vals = []
    for _ in range(n):
        v = random.uniform(vmin, vmax)
        v = round(v / step) * step
        v = round(v, max(decimals, 0))
        vals.append(v)
    return vals

def add_dataset(parent, name, vmin, vmax, decimals, status='private'):
    """Add a dataset_definition element with generated items."""
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

def add_calculated_question(quiz, name, html, formula, grade, variables, decimals,
                            tolerance=0.02, tol_type=1, feedback=None):
    """Add a calculated question with dataset definitions.
    variables: list of (varname, min, max, decimals)
    formula: Moodle formula string using {varname}
    decimals: liczba miejsc po przecinku poprawnej odpowiedzi (correctanswerlength);
        zdanie o dokładności jest wstawiane przed akapitem "Podaj ...".
    tolerance/tol_type: domyślnie 2 % względna (tolerancetype 1).
    feedback: informacja zwrotna ogólna (HTML; tok rozwiązania + odsyłacz do wykładu).
    """
    assert html.count('<p><b>Podaj ') == 1, name
    # Wskazówki nie trafiają do treści pytania zaliczeniowego (student ma sobie
    # poradzić sam); przenoszone są do informacji zwrotnej ogólnej, widocznej po
    # zakończeniu podejścia. Wersja treningowa (generate_exam_trening_xml.py) ma
    # własne treści.
    hints = re.findall(r'<p><i>Wskazówka:\s*(.*?)</i></p>', html, flags=re.S)
    html = re.sub(r'<p><i>Wskazówka:.*?</i></p>', '', html, flags=re.S)
    if hints:
        hint_html = ''.join(f'<p><i>Wskazówka: {h.strip()}</i></p>' for h in hints)
        feedback = hint_html + (feedback or '')
    html = html.replace('<p><b>Podaj ', precision_note(decimals) + '<p><b>Podaj ')
    html = protect_latex_braces(html, variables)
    q = ET.SubElement(quiz, 'question', type='calculated')
    q_name = ET.SubElement(q, 'name')
    ET.SubElement(q_name, 'text').text = name
    q_qt = ET.SubElement(q, 'questiontext', format='html')
    ET.SubElement(q_qt, 'text').text = html
    q_gf = ET.SubElement(q, 'generalfeedback', format='html')
    gf_text = ET.SubElement(q_gf, 'text')
    if feedback:
        gf_text.text = protect_latex_braces(feedback, variables)
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
    ET.SubElement(a, 'correctanswerlength').text = str(decimals)
    fb = ET.SubElement(a, 'feedback', format='html')
    ET.SubElement(fb, 'text')
    ET.SubElement(q, 'unitgradingtype').text = '0'
    ET.SubElement(q, 'unitpenalty').text = '0.1000000'
    ET.SubElement(q, 'showunits').text = '3'
    ET.SubElement(q, 'unitsleft').text = '0'
    dds = ET.SubElement(q, 'dataset_definitions')
    for vname, vmin, vmax, vdec in variables:
        add_dataset(dds, vname, vmin, vmax, vdec)

# ============================================================
# 1. TEORIA — multichoice & truefalse (unchanged logic)
# ============================================================
# Informacja zwrotna ogólna: gdzie w wykładach jest omówione dane zagadnienie.
TEORIA_ZRODLA = {
    "P01_Uklad_zamkniety": "W1 „Zamknięty / Otwarty / Izolowany”",
    "P02_Entalpia": "W2 „Definicja i Znaczenie” (H = U + pV)",
    "P03_Praca_techniczna": "W8 „Praca absolutna, techniczna i bilans”; W3 „Praca Techniczna (L_t)”",
    "P04_Energia_wewnetrzna": "W2 „Energia wewnętrzna”; W8 „Przypomnienie: gaz doskonały”",
    "P05_Dlawienie": "W3 „Zastosowanie: Dławienie – Proces Izentalpowy”",
    "P06_Punkt_krytyczny": "W1 „Punkt Krytyczny”; W4 „Gaz rzeczywisty – izotermy van der Waalsa”; W5 wykres p–T",
    "P07_Stopien_suchosci": "W5 „3. Stopień Suchości (x)”",
    "P08_Entalpia_pary_mokrej": "W5 „Obliczanie Właściwości Pary Mokrej”",
    "P09_Izoterma": "W8 „2. Przemiana Izotermiczna”",
    "P10_Izentropa": "W8 „Klasyfikacja Procesów Politropowych”; W3 „Praca Sprężania Gazu Doskonałego”",
    "P11_Praca_izochory": "W8 „3. Przemiana Izochoryczna”",
    "P12_Zwiazek_Mayera": "W2 „Ciepła właściwe – Równanie Mayera”; W4 „Relacja Mayera (Wyprowadzenie)”",
    "P13_Kelvin_Planck": "W6 „3. Sformułowania II Zasady – Sformułowanie Kelvina-Plancka”",
    "P14_Carnot": "W6 „Wnioski z Carnota”",
    "P15_Chlodzenie": "W6 „Chłodziarka i pompa ciepła”; W11 „1. Idea Chłodzenia (Obieg Lewobieżny)”",
    "P16_Otto": "W9 „3. Obieg Otto (Zapłon Iskrowy – ZI)”",
    "P17_Diesel": "W9 „Obieg Diesla (ZS)”",
    "P18_COP_pompa": "W6 „Współczynniki Efektywności (COP)”; W11 „Mierniki Efektywności (COP)”",
    "P19_Entropia_izolat": "W7 „Zasada wzrostu entropii”",
    "P20_Fourier": "W14 „2. Przewodzenie i Prawo Fouriera”",
    "P21_Stefan_Boltzmann": "W14 „Promieniowanie – Prawo Stefana-Boltzmanna”",
    "P22_Egzergia": "W15 „4. Egzergia: Ilość vs Jakość”; W3 „Analiza Egzergetyczna (Wstęp)”",
    "P23_LHV_HHV": "W15 „3. Wartość Opałowa (W_d)”",
    "P24_Nadmiar_powietrza": "W15 „Współczynnik Nadmiaru Powietrza (λ)”",
    "P31_Rankine_skraplacz": "W10 „2. Obieg Clausiusa-Rankine'a”; „Podsumowanie W10”",
    "P32_Mieszanie_hX": "W12 „Przemiana 4: Mieszanie Strumieni Powietrza”",
    "P33_HHV_LHV": "W15 „3. Wartość Opałowa (W_d)”",
    "P34_DeltaT_lm": "W14 „5. Wymienniki Ciepła”",
    "P35_Kociol_kondensacyjny": "W15 „3. Wartość Opałowa (W_d)” – kotły kondensacyjne",
    "P36_COP_PC_vs_ch": "W6 „Współczynniki Efektywności (COP)”; W11 „Mierniki Efektywności”",
    "P37_Sublimacja": "W4 „Fazy i przemiany fazowe”; W5 wykres p–T wody",
    "P38_Praca_izobary": "W8 „4. Przemiana Izobaryczna”",
    "P39_Joule_Thomson": "W3 „Zjawisko Joule'a-Thomsona – Dławienie Adiabatyczne”",
    "P40_Gouy_Stodola": "W15 „5. Prawo Gouy-Stodoli”; W3 „Analiza Egzergetyczna”",
    "P25_PF_Ogrzewanie_phi": "W12 „5. Przemiany Charakterystyczne – 1. Ogrzewanie izobaryczne (X = const)”",
    "P26_PF_Skraplacz": "W10 „Podsumowanie W10”",
    "P27_PF_Przeciwprad": "W14 „Współprąd vs Przeciwprąd – Porównanie”",
    "P28_PF_Dlawienie_odwr": "W11 „3-4 Zawór rozprężny”; W6 „Przykłady Procesów Nieodwracalnych”",
    "P29_PF_Eta_Carnot": "W6 „Sprawność obiegu Carnota”; „Podsumowanie W6”",
    "P30_PF_Kogeneracja": "W15 „6. Kogeneracja (CHP)”",
}

def zrodlo_feedback(name):
    src = TEORIA_ZRODLA.get(name)
    return f"<p>Zagadnienie omówione na wykładzie: {src}.</p>" if src else ""

# Pytania dublujące wiedzę z innego pytania – osobna podkategoria, żeby przy
# losowaniu z kategorii student nie dostał obu naraz.
TEORIA_REZERWA = {"P33_HHV_LHV", "P36_COP_PC_vs_ch"}

def make_teoria():
    quiz = ET.Element('quiz')
    cat = ET.SubElement(quiz, 'question', type='category')
    cat_cat = ET.SubElement(cat, 'category')
    ET.SubElement(cat_cat, 'text').text = '$course$/top/egzamin/teoria'
    cat_info = ET.SubElement(cat, 'info', format='moodle_auto_format')
    ET.SubElement(cat_info, 'text').text = 'Pytania jednokrotnego wyboru i prawda/fałsz — egzamin z Termodynamiki Technicznej.'
    ET.SubElement(cat, 'idnumber')

    questions = [
        ("P01_Uklad_zamkniety",
         "<p><b>P1.</b> Układ termodynamiczny zamknięty to układ, który:</p>",
         [("nie wymienia z otoczeniem ani masy, ani energii", 0),
          ("wymienia z otoczeniem energię, ale nie wymienia masy", 100),
          ("wymienia z otoczeniem zarówno masę, jak i energię", 0),
          ("ma stałą temperaturę", 0)]),
        ("P02_Entalpia",
         "<p><b>P2.</b> Entalpia \\(H\\) jest zdefiniowana jako:</p>",
         [("energia wewnętrzna gazu przy stałej objętości", 0),
          ("suma ciepła i pracy wymienionej z otoczeniem", 0),
          ("funkcja stanu równa \\(U + pV\\)", 100),
          ("miara nieuporządkowania układu", 0)]),
        ("P03_Praca_techniczna",
         "<p><b>P3.</b> Praca techniczna \\(L_t\\) jest równa:</p>",
         [("\\(\\int p \\, dV\\)", 0), ("\\(-\\int V \\, dp\\)", 100),
          ("\\(\\Delta U\\)", 0), ("\\(\\int V \\, dp\\)", 0)]),
        ("P04_Energia_wewnetrzna",
         "<p><b>P4.</b> Energia wewnętrzna gazu doskonałego zależy wyłącznie od:</p>",
         [("ciśnienia", 0), ("objętości", 0), ("temperatury", 100),
          ("ciśnienia i objętości jednocześnie", 0)]),
        ("P05_Dlawienie",
         "<p><b>P5.</b> Dławienie (przepływ przez zawór dławiący) jest procesem:</p>",
         [("izotermicznym", 0), ("izentropowym", 0), ("izentalpowym", 100), ("izochorycznym", 0)]),
        ("P06_Punkt_krytyczny",
         "<p><b>P6.</b> Punkt krytyczny substancji to stan, powyżej którego:</p>",
         [("substancja istnieje wyłącznie w fazie stałej", 0),
          ("współistnieją trzy fazy (punkt potrójny)", 0),
          ("zanika rozróżnienie między cieczą a gazem", 100),
          ("temperatura wrzenia przestaje zależeć od ciśnienia", 0)]),
        ("P07_Stopien_suchosci",
         "<p><b>P7.</b> Stopień suchości pary mokrej \\(x = 0{,}85\\) oznacza, że mieszanina zawiera:</p>",
         [("85% cieczy i 15% pary (udziały masowe)", 0), ("85% pary i 15% cieczy (udziały masowe)", 100),
          ("parę przegrzaną o 85 K powyżej temperatury nasycenia", 0),
          ("parę o wilgotności względnej 85%", 0)]),
        ("P08_Entalpia_pary_mokrej",
         "<p><b>P8.</b> Entalpia pary mokrej o stopniu suchości \\(x\\) wynosi:</p>",
         [("\\(h_x = h'' - x \\cdot r\\)", 0), ("\\(h_x = h' + x \\cdot r\\)", 100),
          ("\\(h_x = x \\cdot h'\\)", 0), ("\\(h_x = h' \\cdot h'' / x\\)", 0)]),
        ("P09_Izoterma",
         "<p><b>P9.</b> W przemianie izotermicznej gazu doskonałego całe dostarczone ciepło:</p>",
         [("zwiększa energię wewnętrzną gazu", 0), ("wynosi zero", 0),
          ("zamienia się w pracę objętościową", 100), ("zwiększa temperaturę gazu", 0)]),
        ("P10_Izentropa",
         "<p><b>P10.</b> Wykładnik politropy \\(n = \\kappa\\) odpowiada przemianie:</p>",
         [("izotermicznej", 0), ("izobarycznej", 0), ("izochorycznej", 0),
          ("izentropowej", 100)]),
        ("P11_Praca_izochory",
         "<p><b>P11.</b> Praca objętościowa przemiany izochorycznej wynosi:</p>",
         [("\\(mRT \\ln(V_2 / V_1)\\)", 0), ("\\(mc_v \\Delta T\\)", 0),
          ("\\(mc_p \\Delta T\\)", 0), ("zero", 100)]),
        ("P12_Zwiazek_Mayera",
         "<p><b>P12.</b> Związek Mayera dla gazu doskonałego ma postać:</p>",
         [("\\(c_p \\cdot c_v = R\\)", 0), ("\\(c_p - c_v = R\\)", 100),
          ("\\(c_p + c_v = R\\)", 0), ("\\(c_p / c_v = R\\)", 0)]),
        ("P13_Kelvin_Planck",
         "<p><b>P13.</b> Sformułowanie Kelvina-Plancka II Zasady mówi, że:</p>",
         [("ciepło może samoistnie przepływać od ciała zimnego do ciepłego", 0),
          ("nie można zbudować silnika cyklicznego zamieniającego całe pobrane ciepło w pracę", 100),
          ("entropia układu izolowanego może maleć", 0),
          ("sprawność każdego silnika wynosi 100%", 0)]),
        ("P14_Carnot",
         "<p><b>P14.</b> Sprawność obiegu Carnota zależy wyłącznie od:</p>",
         [("rodzaju czynnika roboczego", 0), ("ciśnienia maksymalnego w obiegu", 0),
          ("objętości cylindra", 0), ("temperatur źródła górnego i dolnego", 100)]),
        ("P15_Chlodzenie",
         "<p><b>P15.</b> Urządzenie chłodnicze to maszyna, która:</p>",
         [("zamienia ciepło bezpośrednio w pracę", 0),
          ("pobiera pracę, aby przenosić ciepło z ciała zimnego do ciepłego", 100),
          ("pracuje w obiegu prawobieżnym", 0), ("nie wymaga zasilania energią", 0)]),
        ("P16_Otto",
         "<p><b>P16.</b> W obiegu Otto ciepło jest dostarczane do czynnika:</p>",
         [("przy stałym ciśnieniu (izobarycznie)", 0), ("przy stałej temperaturze (izotermicznie)", 0),
          ("przy stałej objętości (izochorycznie)", 100), ("przy stałej entropii (izentropowo)", 0)]),
        ("P17_Diesel",
         "<p><b>P17.</b> W obiegu Diesla ciepło jest dostarczane do czynnika:</p>",
         [("przy stałym ciśnieniu (izobarycznie)", 100), ("przy stałej temperaturze (izotermicznie)", 0),
          ("przy stałej objętości (izochorycznie)", 0), ("przy stałej entropii (izentropowo)", 0)]),
        ("P18_COP_pompa",
         "<p><b>P18.</b> Współczynnik wydajności grzejnej pompy ciepła (COP) jest:</p>",
         [("zawsze mniejszy od 1", 0), ("zawsze równy 1", 0),
          ("zawsze większy od 1", 100), ("zależny wyłącznie od rodzaju czynnika", 0)]),
        ("P19_Entropia_izolat",
         "<p><b>P19.</b> Entropia układu izolowanego w procesie nieodwracalnym:</p>",
         [("maleje", 0), ("nie zmienia się", 0), ("rośnie", 100),
          ("może zarówno rosnąć, jak i maleć", 0)]),
        ("P20_Fourier",
         "<p><b>P20.</b> Przewodzenie ciepła (prawo Fouriera) polega na:</p>",
         [("ruchu makroskopowych porcji płynu", 0), ("emisji promieniowania elektromagnetycznego", 0),
          ("przekazywaniu energii między cząsteczkami, proporcjonalnym do gradientu temperatury", 100),
          ("wymianie masy między układem a otoczeniem", 0)]),
        ("P21_Stefan_Boltzmann",
         "<p><b>P21.</b> Strumień ciepła emitowanego przez ciało doskonale czarne jest proporcjonalny do:</p>",
         [("\\(T\\)", 0), ("\\(T^2\\)", 0), ("\\(T^3\\)", 0), ("\\(T^4\\)", 100)]),
        ("P22_Egzergia",
         "<p><b>P22.</b> Egzergia to:</p>",
         [("całkowita energia wewnętrzna układu", 0),
          ("maksymalna praca, jaką można uzyskać z układu w stosunku do stanu otoczenia", 100),
          ("energia tracona w każdym procesie", 0), ("synonim entalpii", 0)]),
        ("P23_LHV_HHV",
         "<p><b>P23.</b> Wartość opałowa (LHV) różni się od ciepła spalania (HHV) tym, że:</p>",
         [("nie uwzględnia ciepła parowania wody w spalinach", 100),
          ("uwzględnia dodatkowe ciepło od azotu", 0),
          ("jest zawsze większa od HHV", 0), ("odnosi się tylko do paliw gazowych", 0)]),
        ("P24_Nadmiar_powietrza",
         "<p><b>P24.</b> Współczynnik nadmiaru powietrza \\(\\lambda > 1\\) oznacza:</p>",
         [("brak tlenu w strefie spalania", 0), ("spalanie stechiometryczne", 0),
          ("nadmiar tlenu ponad ilość stechiometryczną", 100),
          ("spalanie niezupełne z wydzielaniem sadzy", 0)]),
        ("P31_Rankine_skraplacz",
         "<p><b>P31.</b> W obiegu Rankine'a skraplacz służy do:</p>",
         [("podgrzania wody zasilającej", 0), ("sprężania pary przed turbiną", 0),
          ("skroplenia pary po ekspansji w turbinie, zamykając obieg", 100),
          ("odgazowania wody kotłowej", 0)]),
        ("P32_Mieszanie_hX",
         "<p><b>P32.</b> Przy mieszaniu dwóch strumieni powietrza wilgotnego punkt M na wykresie h-X leży:</p>",
         [("poza odcinkiem łączącym punkty obu strumieni", 0),
          ("na odcinku łączącym punkty obu strumieni, dzieląc go proporcjonalnie do mas", 100),
          ("zawsze w punkcie środkowym odcinka", 0), ("na krzywej nasycenia", 0)]),
        ("P33_HHV_LHV",
         "<p><b>P33.</b> Ciepło spalania (HHV) jest większe od wartości opałowej (LHV), ponieważ:</p>",
         [("uwzględnia ciepło przegrzania spalin powyżej 100 °C", 0),
          ("uwzględnia ciepło skroplenia wody zawartej w spalinach", 100),
          ("pomija straty kominowe", 0), ("dotyczy wyłącznie paliw stałych", 0)]),
        ("P34_DeltaT_lm",
         "<p><b>P34.</b> Średnia logarytmiczna różnica temperatur stosowana jest do obliczeń:</p>",
         [("sprawności obiegu Carnota", 0), ("mocy sprężarki", 0),
          ("wymienników ciepła", 100), ("ciepła spalania paliw", 0)]),
        ("P35_Kociol_kondensacyjny",
         "<p><b>P35.</b> Kocioł kondensacyjny osiąga sprawność > 100% (w odniesieniu do LHV), ponieważ:</p>",
         [("wytwarza energię z niczego", 0),
          ("odzyskuje ciepło skroplenia pary wodnej ze spalin", 100),
          ("wykorzystuje energię elektryczną", 0), ("pracuje w próżni", 0)]),
        ("P36_COP_PC_vs_ch",
         "<p><b>P36.</b> Współczynnik wydajności grzejnej pompy ciepła \\(COP_{PC}\\) jest zawsze:</p>",
         [("mniejszy od COP chłodziarki o 1", 0), ("większy od COP chłodziarki o 1", 100),
          ("równy COP chłodziarki", 0), ("równy sprawności Carnota", 0)]),
        ("P37_Sublimacja",
         "<p><b>P37.</b> Sublimacja to przemiana fazowa polegająca na:</p>",
         [("przejściu cieczy w gaz", 0), ("przejściu ciała stałego bezpośrednio w gaz", 100),
          ("przejściu gazu w ciecz", 0), ("przejściu cieczy w ciało stałe", 0)]),
        ("P38_Praca_izobary",
         "<p><b>P38.</b> Praca objętościowa przemiany izobarycznej wynosi:</p>",
         [("zero", 0), ("\\(p(V_2 - V_1)\\)", 100),
          ("\\(mRT \\ln(V_2/V_1)\\)", 0), ("\\(mc_v \\Delta T\\)", 0)]),
        ("P39_Joule_Thomson",
         "<p><b>P39.</b> Efekt Joule'a-Thomsona opisuje zmianę temperatury gazu podczas:</p>",
         [("sprężania izentropowego", 0), ("ogrzewania izobarycznego", 0),
          ("dławienia", 100),
          ("ekspansji izotermicznej", 0)]),
        ("P40_Gouy_Stodola",
         "<p><b>P40.</b> Prawo Gouy-Stodoli wiąże straty egzergii z:</p>",
         [("ciśnieniem otoczenia i zmianą objętości", 0),
          ("temperaturą otoczenia i generacją entropii", 100),
          ("masą czynnika roboczego", 0), ("sprawnością Carnota", 0)]),
    ]

    tf_questions = [
        ("P25_PF_Ogrzewanie_phi",
         "<p><b>P25.</b> Ogrzewanie powietrza wilgotnego przy stałym ciśnieniu (bez dodawania wody) powoduje spadek jego wilgotności względnej \\(\\varphi\\).</p>", True),
        ("P26_PF_Skraplacz",
         "<p><b>P26.</b> Obniżenie ciśnienia w skraplaczu siłowni parowej zwiększa pracę użyteczną turbiny.</p>", True),
        ("P27_PF_Przeciwprad",
         "<p><b>P27.</b> Wymiennik przeciwprądowy pozwala osiągnąć większą średnią różnicę temperatur niż wymiennik współprądowy przy tych samych temperaturach wlotowych i tych samych strumieniach płynów.</p>", True),
        ("P28_PF_Dlawienie_odwr",
         "<p><b>P28.</b> Proces dławienia w zaworze redukcyjnym jest odwracalny.</p>", False),
        ("P29_PF_Eta_Carnot",
         "<p><b>P29.</b> Sprawność termiczna rzeczywistego obiegu silnikowego może przekroczyć sprawność Carnota dla tych samych temperatur skrajnych.</p>", False),
        ("P30_PF_Kogeneracja",
         "<p><b>P30.</b> Kogeneracja (CHP) to jednoczesne wytwarzanie energii elektrycznej i ciepła użytkowego z tego samego paliwa.</p>", True),
    ]

    def add_multichoice(name, qtext, answers):
        q = ET.SubElement(quiz, 'question', type='multichoice')
        q_name = ET.SubElement(q, 'name')
        ET.SubElement(q_name, 'text').text = name
        q_qt = ET.SubElement(q, 'questiontext', format='html')
        ET.SubElement(q_qt, 'text').text = qtext
        q_gf = ET.SubElement(q, 'generalfeedback', format='html')
        ET.SubElement(q_gf, 'text').text = zrodlo_feedback(name)
        ET.SubElement(q, 'defaultgrade').text = '1.0000000'
        ET.SubElement(q, 'penalty').text = '0.3333333'
        ET.SubElement(q, 'hidden').text = '0'
        ET.SubElement(q, 'idnumber')
        ET.SubElement(q, 'single').text = 'true'
        ET.SubElement(q, 'shuffleanswers').text = '1'
        ET.SubElement(q, 'answernumbering').text = 'abc'
        cf = ET.SubElement(q, 'correctfeedback', format='html')
        ET.SubElement(cf, 'text').text = 'Poprawna odpowiedź.'
        pf = ET.SubElement(q, 'partiallycorrectfeedback', format='html')
        ET.SubElement(pf, 'text')
        inc = ET.SubElement(q, 'incorrectfeedback', format='html')
        ET.SubElement(inc, 'text').text = 'Niepoprawna odpowiedź.'
        for atext, frac in answers:
            a = ET.SubElement(q, 'answer', fraction=str(frac), format='html')
            ET.SubElement(a, 'text').text = f'<p>{atext}</p>'
            fb = ET.SubElement(a, 'feedback', format='html')
            ET.SubElement(fb, 'text')

    for name, qtext, answers in questions:
        if name not in TEORIA_REZERWA:
            add_multichoice(name, qtext, answers)

    for name, qtext, correct in tf_questions:
        q = ET.SubElement(quiz, 'question', type='truefalse')
        q_name = ET.SubElement(q, 'name')
        ET.SubElement(q_name, 'text').text = name
        q_qt = ET.SubElement(q, 'questiontext', format='html')
        ET.SubElement(q_qt, 'text').text = qtext
        q_gf = ET.SubElement(q, 'generalfeedback', format='html')
        ET.SubElement(q_gf, 'text').text = zrodlo_feedback(name)
        ET.SubElement(q, 'defaultgrade').text = '1.0000000'
        ET.SubElement(q, 'penalty').text = '1.0000000'
        ET.SubElement(q, 'hidden').text = '0'
        ET.SubElement(q, 'idnumber')
        a_true = ET.SubElement(q, 'answer', fraction=str(100 if correct else 0), format='moodle_auto_format')
        ET.SubElement(a_true, 'text').text = 'true'
        fb_t = ET.SubElement(a_true, 'feedback', format='html')
        ET.SubElement(fb_t, 'text')
        a_false = ET.SubElement(q, 'answer', fraction=str(0 if correct else 100), format='moodle_auto_format')
        ET.SubElement(a_false, 'text').text = 'false'
        fb_f = ET.SubElement(a_false, 'feedback', format='html')
        ET.SubElement(fb_f, 'text')

    cat2 = ET.SubElement(quiz, 'question', type='category')
    cat2_cat = ET.SubElement(cat2, 'category')
    ET.SubElement(cat2_cat, 'text').text = '$course$/top/egzamin/teoria/rezerwa'
    cat2_info = ET.SubElement(cat2, 'info', format='moodle_auto_format')
    ET.SubElement(cat2_info, 'text').text = ('Warianty pytań z kategorii „teoria” sprawdzające tę samą wiedzę '
                                             '(P33 ↔ P23, P36 ↔ P18). Nie losować razem z oryginałami.')
    ET.SubElement(cat2, 'idnumber')
    for name, qtext, answers in questions:
        if name in TEORIA_REZERWA:
            add_multichoice(name, qtext, answers)

    write_xml(quiz, 'egzamin_teoria.xml')
    print(f"  Total theory questions: {len(questions) + len(tf_questions)}")

# ============================================================
# 2. ZADANIA — calculated type with datasets
# ============================================================
def make_zadania():
    quiz = ET.Element('quiz')
    cat = ET.SubElement(quiz, 'question', type='category')
    cat_cat = ET.SubElement(cat, 'category')
    ET.SubElement(cat_cat, 'text').text = '$course$/top/egzamin/zadania'
    cat_info = ET.SubElement(cat, 'info', format='moodle_auto_format')
    ET.SubElement(cat_info, 'text').text = 'Zadania obliczeniowe (calculated) — egzamin z Termodynamiki Technicznej.'
    ET.SubElement(cat, 'idnumber')

    # ---- Zad 1: Izochora powietrze ----
    add_calculated_question(quiz,
        "Zad01_Izochora_powietrze",
        "<p><b>Zadanie 1 — Ogrzewanie gazu przy stałej objętości</b></p>"
        "<p>W zamkniętym zbiorniku o stałej objętości znajduje się <b>{m}</b> kg powietrza "
        "o temperaturze <b>{T1}</b> °C. Gaz ogrzano do temperatury <b>{T2}</b> °C. "
        "Ciepło właściwe powietrza przy stałej objętości wynosi \\(c_v\\) = 0,718 kJ/(kg·K). "
        "Obliczyć ilość ciepła doprowadzonego do gazu.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — przemiany, izochora.</i></p>"
        "<p><b>Podaj \\(Q\\) [kJ]:</b></p>",
        "{m} * 0.718 * ({T2} - {T1})",
        3.0, [("m", 1.0, 5.0, 1), ("T1", 5, 30, 0), ("T2", 200, 400, 0)],
        decimals=1)

    # ---- Zad 1b: Izochora metan ----
    add_calculated_question(quiz,
        "Zad01b_Izochora_metan",
        "<p><b>Zadanie 1b — Ogrzewanie metanu przy stałej objętości</b></p>"
        "<p>W zamkniętym zbiorniku o stałej objętości znajduje się <b>{m}</b> kg metanu "
        "(\\(CH_4\\), \\(c_v\\) = 1,708 kJ/(kg·K)) o temperaturze <b>{T1}</b> °C. "
        "Gaz ogrzano do temperatury <b>{T2}</b> °C. Obliczyć ilość ciepła doprowadzonego do gazu.</p>"
        "<p><i>Wskazówka: I Zasada dla układu zamkniętego przy V = const.</i></p>"
        "<p><b>Podaj \\(Q\\) [kJ]:</b></p>",
        "{m} * 1.708 * ({T2} - {T1})",
        3.0, [("m", 0.5, 3.0, 1), ("T1", 10, 30, 0), ("T2", 200, 350, 0)],
        decimals=1)

    # ---- Zad 2: Turbina ----
    add_calculated_question(quiz,
        "Zad02_Turbina",
        "<p><b>Zadanie 2 — Moc turbiny parowej</b></p>"
        "<p>Przez turbinę przepływa para wodna ze strumieniem masy <b>{mdot}</b> kg/s. "
        "Entalpia właściwa na wlocie wynosi <b>{h1}</b> kJ/kg, na wylocie <b>{h2}</b> kJ/kg. "
        "Prędkość pary na wlocie to \\(\\omega_1\\) = <b>{c1}</b> m/s, na wylocie \\(\\omega_2\\) = <b>{c2}</b> m/s. "
        "Turbina jest adiabatyczna. Obliczyć moc mechaniczną na wale turbiny.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — bilans turbiny/sprężarki.</i></p>"
        "<p><b>Podaj \\(P\\) [kW]:</b></p>",
        "{mdot} * (({h1} - {h2}) + ({c1}*{c1} - {c2}*{c2}) / 2000)",
        3.0, [("mdot", 80, 160, 0), ("h1", 3200, 3500, 0),
         ("h2", 2300, 2600, 0), ("c1", 30, 80, 0), ("c2", 5, 20, 0)],
        decimals=1)

    # ---- Zad 2b: Sprężarka ----
    add_calculated_question(quiz,
        "Zad02b_Sprezarka",
        "<p><b>Zadanie 2b — Moc sprężarki</b></p>"
        "<p>Sprężarka adiabatyczna spręża powietrze ze strumieniem masy <b>{mdot}</b> kg/s. "
        "Entalpia właściwa na wlocie wynosi <b>{h1}</b> kJ/kg, na wylocie <b>{h2}</b> kJ/kg. "
        "Różnice energii kinetycznej pominąć. Obliczyć moc napędową sprężarki.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — bilans turbiny/sprężarki.</i></p>"
        "<p><b>Podaj \\(P\\) [kW]:</b></p>",
        "{mdot} * ({h2} - {h1})",
        3.0, [("mdot", 2.0, 6.0, 1), ("h1", 280, 320, 0), ("h2", 480, 560, 0)],
        decimals=1)

    # ---- Zad 3a: Carnot sprawność ----
    add_calculated_question(quiz,
        "Zad03a_Carnot_sprawnosc",
        "<p><b>Zadanie 3a — Sprawność obiegu Carnota</b></p>"
        "<p>Siłownia parowa pracuje między temperaturą pary <b>{TH}</b> °C (kocioł) "
        "a temperaturą wody chłodzącej <b>{TL}</b> °C (skraplacz). "
        "Obliczyć sprawność obiegu Carnota (podać jako ułamek, np. 0,72).</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — sprawności obiegów. Temperatury w kelwinach.</i></p>"
        "<p><b>Podaj \\(\\eta_C\\) [-]:</b></p>",
        "1 - ({TL} + 273.15) / ({TH} + 273.15)",
        2.0, [("TH", 500, 900, 0), ("TL", 15, 35, 0)],
        decimals=2)

    # ---- Zad 3b: Q_odpr w GJ ----
    add_calculated_question(quiz,
        "Zad03b_Q_odpr_GJ",
        "<p><b>Zadanie 3b — Straty ciepła w skraplaczu</b></p>"
        "<p>(kontynuacja Zadania 3a) Siłownia parowa pracuje między temperaturą pary <b>{TH}</b> °C (kocioł) "
        "a temperaturą wody chłodzącej <b>{TL}</b> °C (skraplacz). Moc elektryczna bloku wynosi <b>{Pel}</b> MW, "
        "a jego sprawność rzeczywista stanowi <b>{efrac}</b> sprawności Carnota. "
        "Obliczyć ilość ciepła odprowadzonego w skraplaczu w ciągu <b>{th}</b> godzin pracy.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — związek moc–ciepło. 1 MWh = 3,6 GJ.</i></p>"
        "<p><b>Podaj \\(Q_{odpr}\\) [GJ]:</b></p>",
        "({Pel} / ({efrac} * (1 - ({TL}+273.15)/({TH}+273.15))) - {Pel}) * {th} * 3.6",
        5.0, [("TH", 500, 900, 0), ("TL", 15, 35, 0),
         ("Pel", 200, 500, 0), ("efrac", 0.40, 0.55, 2), ("th", 8, 24, 0)],
        decimals=1)

    # ---- Zad 6: Izentropa sprężanie ----
    add_calculated_question(quiz,
        "Zad06_Izentropa",
        "<p><b>Zadanie 6 — Izentropowe sprężanie powietrza</b></p>"
        "<p>Powietrze o temperaturze <b>{T1}</b> °C i ciśnieniu <b>{p1}</b> bar sprężono izentropowo "
        "do ciśnienia <b>{p2}</b> bar. Obliczyć temperaturę końcową gazu po sprężeniu. "
        "Przyjąć \\(\\kappa\\) = 1,40.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — przemiany, izentropa. Temperatury w kelwinach.</i></p>"
        "<p><b>Podaj \\(T_2\\) [°C]:</b></p>",
        "({T1} + 273.15) * pow({p2}/{p1}, 0.285714) - 273.15",
        3.0, [("T1", 10, 30, 0), ("p1", 1, 2, 0), ("p2", 5, 12, 0)],
        decimals=1)

    # ---- Zad 7: COP chłodziarki ----
    add_calculated_question(quiz,
        "Zad07_Chlodziarka",
        "<p><b>Zadanie 7 — Chłodziarka (obieg lewobieżny)</b></p>"
        "<p>Chłodziarka pracuje między temperaturą wnętrza <b>{TL}</b> °C a temperaturą "
        "otoczenia <b>{TH}</b> °C. Moc sprężarki wynosi <b>{P}</b> kW. "
        "Obliczyć maksymalny (Carnota) współczynnik wydajności chłodniczej COP "
        "oraz maksymalny strumień ciepła odbieranego z wnętrza.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — COP chłodziarki. Temperatury w kelwinach.</i></p>"
        "<p><b>Podaj \\(\\dot{Q}_L\\) [kW]:</b></p>",
        "{P} * ({TL} + 273.15) / (({TH} + 273.15) - ({TL} + 273.15))",
        3.0, [("TL", -25, -10, 0), ("TH", 25, 40, 0), ("P", 0.3, 1.5, 1)],
        decimals=2)

    # ---- Zad 8: Izoterma rozprężanie ----
    add_calculated_question(quiz,
        "Zad08_Izoterma",
        "<p><b>Zadanie 8 — Rozprężanie izotermiczne gazu</b></p>"
        "<p>W cylindrze z tłokiem znajduje się <b>{m}</b> kg powietrza o temperaturze <b>{T1}</b> °C "
        "i ciśnieniu <b>{p1}</b> bar. Gaz rozprężono izotermicznie do ciśnienia <b>{p2}</b> bar. "
        "Obliczyć pracę objętościową wykonaną przez gaz. Przyjąć \\(R\\) = 287 J/(kg·K).</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — przemiany, izoterma. Temperatury w kelwinach.</i></p>"
        "<p><b>Podaj \\(L\\) [kJ]:</b></p>",
        "{m} * 0.287 * ({T1} + 273.15) * log({p1}/{p2})",
        3.0, [("m", 1.0, 4.0, 1), ("T1", 15, 35, 0), ("p1", 5, 12, 0), ("p2", 1, 2, 0)],
        decimals=1)

    # ---- Zad 9: Kocioł ----
    add_calculated_question(quiz,
        "Zad09_Kociol",
        "<p><b>Zadanie 9 — Kocioł parowy (bilans energii)</b></p>"
        "<p>W kotle parowym wytwarzane jest izobarycznie <b>{mdot}</b> t/h pary wodnej przegrzanej "
        "o entalpii <b>{h2}</b> kJ/kg. Woda zasilająca kocioł ma temperaturę <b>{tw}</b> °C "
        "(entalpia wody: \\(h_1 \\approx c_w \\cdot t_w\\), gdzie \\(c_w\\) = 4,19 kJ/(kg·K)). "
        "Obliczyć strumień ciepła, jaki powinien być doprowadzony do kotła.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — bilans kotła/wymiennika. Przelicz t/h na kg/s.</i></p>"
        "<p><b>Podaj \\(\\dot{Q}\\) [kW]:</b></p>",
        "({mdot} * 1000 / 3600) * ({h2} - 4.19 * {tw})",
        3.0, [("mdot", 2.0, 6.0, 1), ("h2", 2900, 3200, 0), ("tw", 20, 40, 0)],
        decimals=1)

    # ---- Zad 11: Klimatyzator (pompa ciepła) ----
    add_calculated_question(quiz,
        "Zad11_Klimatyzator",
        "<p><b>Zadanie 11 — Sprawność klimatyzatora (pompa ciepła)</b></p>"
        "<p>Klimatyzator pracujący w trybie grzania pobiera ciepło z powietrza zewnętrznego "
        "o temperaturze <b>{TL}</b> °C i oddaje je do pomieszczenia o temperaturze <b>{TH}</b> °C. "
        "Moc elektryczna sprężarki wynosi <b>{P}</b> kW, a rzeczywisty współczynnik COP urządzenia "
        "stanowi <b>{efrac}</b> wartości COP Carnota. Obliczyć strumień ciepła dostarczanego "
        "do pomieszczenia.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — COP pompy ciepła. Temperatury w kelwinach.</i></p>"
        "<p><b>Podaj \\(\\dot{Q}_H\\) [kW]:</b></p>",
        "{P} * {efrac} * ({TH}+273.15) / (({TH}+273.15) - ({TL}+273.15))",
        3.0, [("TL", -10, 0, 0), ("TH", 18, 25, 0), ("P", 1.5, 4.0, 1),
         ("efrac", 0.30, 0.50, 2)],
        decimals=2)

    # ---- Zad 12: Rekuperator ----
    add_calculated_question(quiz,
        "Zad12_Rekuperator",
        "<p><b>Zadanie 12 — Rekuperator powietrza (sprawność temperaturowa)</b></p>"
        "<p>W rekuperatorze krzyżowym powietrze nawiewane (świeże) o temperaturze <b>{tzew}</b> °C "
        "jest podgrzewane powietrzem wywiewanym (zużytym) o temperaturze <b>{twew}</b> °C. "
        "Sprawność temperaturowa rekuperatora wynosi <b>{eta}</b> %. "
        "Obliczyć temperaturę powietrza nawiewanego po przejściu przez rekuperator.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — sprawność rekuperatora.</i></p>"
        "<p><b>Podaj \\(t_{naw,wy}\\) [°C]:</b></p>",
        "{tzew} + {eta}/100 * ({twew} - {tzew})",
        3.0, [("tzew", -20, -5, 0), ("twew", 18, 24, 0), ("eta", 60, 85, 0)],
        decimals=2)

    # ---- Zad 13a: Mieszanie — temperatura ----
    add_calculated_question(quiz,
        "Zad13a_Mieszanie_t",
        "<p><b>Zadanie 13a — Mieszanie strumieni powietrza wilgotnego</b></p>"
        "<p>W centrali wentylacyjnej miesza się dwa strumienie powietrza:</p>"
        "<ul>"
        "<li>Strumień 1 (zewnętrzny): <b>{m1}</b> kg/s, temperatura <b>{t1}</b> °C.</li>"
        "<li>Strumień 2 (obiegowy): <b>{m2}</b> kg/s, temperatura <b>{t2}</b> °C.</li>"
        "</ul>"
        "<p>Obliczyć temperaturę powietrza po zmieszaniu.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — mieszanie strumieni.</i></p>"
        "<p><b>Podaj \\(t_M\\) [°C]:</b></p>",
        "({m1}*{t1} + {m2}*{t2}) / ({m1}+{m2})",
        3.0, [("m1", 0.5, 1.5, 1), ("t1", -15, -5, 0),
         ("m2", 1.5, 3.5, 1), ("t2", 18, 25, 0)],
        decimals=2)

    # ---- Zad 13b: Mieszanie — zawilżenie ----
    add_calculated_question(quiz,
        "Zad13b_Mieszanie_X",
        "<p><b>Zadanie 13b — Mieszanie strumieni (zawilżenie)</b></p>"
        "<p>(kontynuacja Zadania 13a) Zawilżenie strumieni wynosi: "
        "\\(X_1\\) = <b>{X1}</b> g/kg, \\(X_2\\) = <b>{X2}</b> g/kg. "
        "Strumienie masy: <b>{m1}</b> kg/s i <b>{m2}</b> kg/s. "
        "Obliczyć zawilżenie powietrza po zmieszaniu.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — mieszanie strumieni.</i></p>"
        "<p><b>Podaj \\(X_M\\) [g/kg]:</b></p>",
        "({m1}*{X1} + {m2}*{X2}) / ({m1}+{m2})",
        3.0, [("m1", 0.5, 1.5, 1), ("X1", 1.0, 3.0, 1),
         ("m2", 1.5, 3.5, 1), ("X2", 6.0, 10.0, 1)],
        decimals=2)

    # ------------------------------------------------------------------
    # Pytania dodane później (Baza_Pytan_Zadania.md: 3b, 4, 4b, 5, 5b, 10, 10b).
    # Dopisane NA KOŃCU, żeby nie przesunąć sekwencji generatora losowego
    # dla zbiorów Zad01–Zad13b.
    # ------------------------------------------------------------------

    # ---- Zad 3c: Elektrownia gazowa (Brayton) – strumień ciepła doprowadzonego ----
    # eta_C = 0,73–0,82; eta_rzecz = efrac*eta_C = 0,33–0,49; Q_dop = Pel/eta_rzecz
    add_calculated_question(quiz,
        "Zad03c_Elektrownia_gazowa",
        "<p><b>Zadanie 3c — Sprawność elektrowni gazowej</b></p>"
        "<p>Turbina gazowa pracuje w obiegu Braytona między temperaturą spalin za komorą spalania "
        "<b>{TH}</b> °C a temperaturą powietrza na wlocie do sprężarki <b>{TL}</b> °C. "
        "Moc elektryczna bloku wynosi <b>{Pel}</b> MW, a jego sprawność rzeczywista stanowi "
        "<b>{efrac}</b> sprawności Carnota dla tych temperatur. "
        "Obliczyć strumień ciepła doprowadzonego w komorze spalania.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — sprawności obiegów, związek moc–ciepło "
        "(\\(\\dot{Q}_{dop} = P/\\eta\\)). Temperatury w kelwinach.</i></p>"
        "<p><b>Podaj \\(\\dot{Q}_{dop}\\) [MW]:</b></p>",
        "{Pel} / ({efrac} * (1 - ({TL} + 273.15) / ({TH} + 273.15)))",
        4.0, [("TH", 900, 1300, 0), ("TL", 10, 30, 0),
         ("Pel", 50, 300, 0), ("efrac", 0.45, 0.60, 2)],
        decimals=1,
        feedback="<p>Tok rozwiązania: \\(\\eta_C = 1 - T_L/T_H\\) (K), "
                 "\\(\\eta_{rz} = {efrac} \\cdot \\eta_C\\), "
                 "\\(\\dot{Q}_{dop} = P_{el}/\\eta_{rz}\\). "
                 "Wykład W9 „6. Obieg Joule'a-Braytona”, W6 „Sprawność obiegu Carnota”.</p>")

    # ---- Zad 4: Ściana dwuwarstwowa (U) ----
    # R' = d1/1,30 + d2/0,035 (m2K/W) = 2,4–4,8 -> U = 0,21–0,42; zaokrąglenie do 2 miejsc
    # daje do 2,4 % przy U ~0,21 -> tolerancja 3 %
    add_calculated_question(quiz,
        "Zad04_Sciana_dwuwarstwowa",
        "<p><b>Zadanie 4 — Przenikanie ciepła przez ścianę dwuwarstwową</b></p>"
        "<p>Ściana składa się z dwóch warstw:</p>"
        "<ul>"
        "<li>beton o grubości <b>{d1}</b> cm i \\(\\lambda_1\\) = 1,30 W/(m·K),</li>"
        "<li>wełna mineralna o grubości <b>{d2}</b> cm i \\(\\lambda_2\\) = 0,035 W/(m·K).</li>"
        "</ul>"
        "<p>Pominąć opory przejmowania ciepła na powierzchniach "
        "(\\(R'_{si} = R'_{se} = 0\\)). Obliczyć współczynnik przenikania ciepła \\(U\\) przegrody.</p>"
        "<p><i>Wskazówka: opory warstw dodaje się szeregowo: "
        "\\(U = 1 / \\sum(\\delta_i / \\lambda_i)\\). Grubości przelicz na metry.</i></p>"
        "<p><b>Podaj \\(U\\) [W/(m²·K)]:</b></p>",
        "1 / ({d1} / 100 / 1.30 + {d2} / 100 / 0.035)",
        3.0, [("d1", 15, 30, 0), ("d2", 8, 16, 0)],
        decimals=2, tolerance=0.03,
        feedback="<p>Tok rozwiązania: \\(R' = \\delta_1/\\lambda_1 + \\delta_2/\\lambda_2\\) "
                 "[m²·K/W], \\(U = 1/R'\\). Wykład W14 „Przenikanie Ciepła (Współczynnik U)” "
                 "i „Rozwiązanie Zadania” (cegła + styropian).</p>")

    # ---- Zad 4b: Ściana trójwarstwowa (U) ----
    # R' = d1/0,70 + d2/0,77 + d3/0,040 = 1,7–4,3 -> U = 0,23–0,60; tolerancja 3 % (jak Zad04)
    add_calculated_question(quiz,
        "Zad04b_Sciana_trojwarstwowa",
        "<p><b>Zadanie 4b — Ściana trójwarstwowa</b></p>"
        "<p>Ściana składa się z trzech warstw:</p>"
        "<ul>"
        "<li>tynk wewnętrzny o grubości <b>{d1}</b> cm i \\(\\lambda_1\\) = 0,70 W/(m·K),</li>"
        "<li>cegła o grubości <b>{d2}</b> cm i \\(\\lambda_2\\) = 0,77 W/(m·K),</li>"
        "<li>styropian o grubości <b>{d3}</b> cm i \\(\\lambda_3\\) = 0,040 W/(m·K).</li>"
        "</ul>"
        "<p>Pominąć opory przejmowania ciepła na powierzchniach. "
        "Obliczyć współczynnik przenikania ciepła \\(U\\) przegrody.</p>"
        "<p><i>Wskazówka: opory warstw dodaje się szeregowo: "
        "\\(U = 1 / \\sum(\\delta_i / \\lambda_i)\\). Grubości przelicz na metry.</i></p>"
        "<p><b>Podaj \\(U\\) [W/(m²·K)]:</b></p>",
        "1 / ({d1} / 100 / 0.70 + {d2} / 100 / 0.77 + {d3} / 100 / 0.040)",
        3.0, [("d1", 1, 3, 0), ("d2", 12, 38, 0), ("d3", 6, 15, 0)],
        decimals=2, tolerance=0.03,
        feedback="<p>Tok rozwiązania: \\(R' = \\sum \\delta_i/\\lambda_i\\) [m²·K/W], "
                 "\\(U = 1/R'\\). Wykład W14 „Przenikanie Ciepła (Współczynnik U)”.</p>")

    # ---- Zad 5: Nawilżanie adiabatyczne (h = const) ----
    # h = 1,005 t + X(2501 + 1,86 t) [kJ/kg, X w kg/kg]; h1 = h2 daje w postaci zamkniętej:
    # X2 [g/kg] = X1 + dt*(1005 + 1,86*X1)/(2501 + 1,86*(t1 - dt)).
    # Zakresy: gorące suche powietrze (phi1 = 10–27 %), stan 2 zawsze poniżej nasycenia
    # (najgorzej t2 = 20 °C, X2 = 12,8 g/kg -> phi2 ~ 86 %). X2 = 7,2–12,7 g/kg.
    # Tolerancja 5 %: odczyt X2 z wykresu h-X +-0,3 g/kg daje do ~4 % przy X2 ~7 g/kg.
    add_calculated_question(quiz,
        "Zad05_Nawilzanie_adiabatyczne",
        "<p><b>Zadanie 5 — Nawilżanie adiabatyczne powietrza</b></p>"
        "<p>Powietrze o temperaturze <b>{t1}</b> °C i zawilżeniu <b>{X1}</b> g/kg wpływa do komory "
        "zraszania, gdzie jest nawilżane rozpyloną wodą (ciśnienie 0,1 MPa). W wyniku odparowania "
        "wody temperatura powietrza spada o <b>{dt}</b> K. Obliczyć zawilżenie powietrza "
        "po nawilżeniu \\(X_2\\).</p>"
        "<p><i>Wskazówka: nawilżanie wodą przebiega przy \\(h\\) = const — stan 2 leży na "
        "izentalpie \\(h_1 = h_2\\) przechodzącej przez stan 1, w temperaturze "
        "\\(t_2 = t_1 - \\Delta t\\). Odczytaj \\(X_2\\) z wykresu h‑X (od punktu 1 wzdłuż "
        "izentalpy do izotermy \\(t_2\\)) albo oblicz: zapisz \\(h_1 = h_2\\) ze wzoru na "
        "entalpię (Karta Wzorów — powietrze wilgotne) i wyznacz \\(X_2\\).</i></p>"
        "<p><b>Podaj \\(X_2\\) [g/kg]:</b></p>",
        "{X1} + {dt} * (1005 + 1.86 * {X1}) / (2501 + 1.86 * ({t1} - {dt}))",
        4.0, [("t1", 32, 40, 0), ("X1", 4.0, 8.0, 1), ("dt", 8, 12, 0)],
        decimals=1, tolerance=0.05,
        feedback="<p>Tok rozwiązania: \\(h_1 = 1{,}005\\,t_1 + X_1(2501 + 1{,}86\\,t_1)\\) "
                 "(X w kg/kg), \\(t_2 = t_1 - \\Delta t\\), z \\(h_2 = h_1\\): "
                 "\\(X_2 = (h_1 - 1{,}005\\,t_2)/(2501 + 1{,}86\\,t_2)\\) "
                 "(na wykresie h‑X: punkt 2 na izentalpie przez punkt 1). Wykład W12 „Nawilżanie Adiabatyczne (Wodą)”.</p>")

    # ---- Zad 5b: Ogrzewanie powietrza w nagrzewnicy (X = const) ----
    # phi2 = phi1 * ps(t1)/ps(t2); ps z równania Magnusa (610,94*exp(17,625 t/(t+243,04)) Pa,
    # błąd < 0,4 % w 0–50 °C). Wynik 8,6–47 %. Tolerancja 3 %: tablice p_s / wykres h-X.
    add_calculated_question(quiz,
        "Zad05b_Nagrzewnica",
        "<p><b>Zadanie 5b — Ogrzewanie powietrza w nagrzewnicy</b></p>"
        "<p>Powietrze wilgotne o temperaturze <b>{t1}</b> °C, wilgotności względnej "
        "<b>{phi1}</b> % i ciśnieniu barometrycznym 1013 hPa przepływa przez nagrzewnicę "
        "elektryczną, która podnosi jego temperaturę do <b>{t2}</b> °C. "
        "Obliczyć wilgotność względną powietrza na wylocie z nagrzewnicy.</p>"
        "<p><i>Wskazówka: ogrzewanie bez dodawania wody — zawilżenie \\(X\\) i ciśnienie "
        "cząstkowe pary \\(p_w\\) nie zmieniają się; zmienia się tylko \\(\\varphi = p_w/p_s(t)\\), "
        "bo rośnie ciśnienie nasycenia \\(p_s(t)\\). Ciśnienia nasycenia odczytaj z tablic "
        "(lub \\(\\varphi_2\\) wprost z wykresu h‑X).</i></p>"
        "<p><b>Podaj \\(\\varphi_2\\) [%]:</b></p>",
        "{phi1} * exp(17.625 * {t1} / ({t1} + 243.04)) / exp(17.625 * {t2} / ({t2} + 243.04))",
        3.0, [("t1", 0, 10, 0), ("phi1", 60, 90, 0), ("t2", 20, 30, 0)],
        decimals=1, tolerance=0.03,
        feedback="<p>Tok rozwiązania: \\(p_w = \\varphi_1 \\, p_s(t_1)\\) = const, "
                 "\\(\\varphi_2 = p_w / p_s(t_2) = \\varphi_1 \\, p_s(t_1)/p_s(t_2)\\). "
                 "Wykład W12 „Przykłady Obliczeniowe – Zadanie 1: Ogrzewanie Powietrza”, "
                 "„Przemiana 1: Ogrzewanie izobaryczne (X = const)”.</p>")

    # ---- Zad 10: Wymiennik przeciwprądowy (Q = U A dT_lm) ----
    # Przeciwprąd: dT1 = t1g - t2z (koniec gorący) = 10–30 K, dT2 = t2g - t1z (koniec zimny)
    # = 32–50 K – zakresy rozłączne, więc dT1 != dT2 (ln(1) = 0 nie wystąpi).
    # Spadek t gorącej (30–50 K) < przyrost t zimnej (52–70 K) -> C_g > C_z, spójne z dT1 < dT2.
    add_calculated_question(quiz,
        "Zad10_Wymiennik_przeciwprad",
        "<p><b>Zadanie 10 — Wymiennik ciepła przeciwprądowy (strumień ciepła)</b></p>"
        "<p>W wymienniku przeciwprądowym woda jest ogrzewana od <b>{t1z}</b> °C do <b>{t2z}</b> °C "
        "strumieniem gorącej wody, która wchodzi z temperaturą <b>{t1g}</b> °C i wychodzi "
        "z temperaturą <b>{t2g}</b> °C. Współczynnik przenikania ciepła wymiennika wynosi "
        "\\(U\\) = <b>{U}</b> W/(m²·K), a powierzchnia wymiany ciepła <b>{A}</b> m². "
        "Obliczyć strumień ciepła wymienianego w wymienniku.</p>"
        "<p><i>Wskazówka: \\(\\dot{Q} = U A \\, \\Delta T_{lm}\\), "
        "\\(\\Delta T_{lm} = (\\Delta T_1 - \\Delta T_2) / \\ln(\\Delta T_1 / \\Delta T_2)\\); "
        "w przeciwprądzie \\(\\Delta T_1 = t_{g,we} - t_{z,wy}\\), "
        "\\(\\Delta T_2 = t_{g,wy} - t_{z,we}\\).</i></p>"
        "<p><b>Podaj \\(\\dot{Q}\\) [kW]:</b></p>",
        "{U} * {A} * (({t1g} - {t2z}) - ({t2g} - {t1z})) / log(({t1g} - {t2z}) / ({t2g} - {t1z})) / 1000",
        4.0, [("t1z", 10, 18, 0), ("t2z", 70, 80, 0), ("t1g", 90, 100, 0), ("t2g", 50, 60, 0),
         ("U", 800, 1500, 0), ("A", 5, 20, 0)],
        decimals=1,
        feedback="<p>Tok rozwiązania: \\(\\Delta T_1 = t_{g,we} - t_{z,wy}\\), "
                 "\\(\\Delta T_2 = t_{g,wy} - t_{z,we}\\), "
                 "\\(\\Delta T_{lm} = (\\Delta T_1 - \\Delta T_2)/\\ln(\\Delta T_1/\\Delta T_2)\\), "
                 "\\(\\dot{Q} = U A \\Delta T_{lm}\\) (W → kW). "
                 "Wykład W14 „5. Wymienniki Ciepła”, „Współprąd vs Przeciwprąd”.</p>")

    # ---- Zad 10b: Wymiennik współprądowy olej–woda ----
    # Współprąd: dT1 = t1g - t1z (wlot) = 75–105 K, dT2 = t2g - t2z (wylot) = 15–35 K
    # – zakresy rozłączne, dT2 > 0 zawsze (we współprądzie t_g,wy > t_z,wy).
    add_calculated_question(quiz,
        "Zad10b_Wymiennik_wspolprad",
        "<p><b>Zadanie 10b — Wymiennik współprądowy</b></p>"
        "<p>W wymienniku współprądowym olej jest chłodzony od <b>{t1g}</b> °C do <b>{t2g}</b> °C "
        "wodą wchodzącą z temperaturą <b>{t1z}</b> °C i wychodzącą z temperaturą <b>{t2z}</b> °C. "
        "Współczynnik przenikania ciepła wynosi \\(U\\) = <b>{U}</b> W/(m²·K), "
        "powierzchnia wymiany ciepła <b>{A}</b> m². "
        "Obliczyć strumień ciepła wymienianego w wymienniku.</p>"
        "<p><i>Wskazówka: dla wymiennika współprądowego \\(\\Delta T_1 = t_{g,we} - t_{z,we}\\), "
        "\\(\\Delta T_2 = t_{g,wy} - t_{z,wy}\\). Dalej: "
        "\\(\\dot{Q} = U A \\, \\Delta T_{lm}\\), "
        "\\(\\Delta T_{lm} = (\\Delta T_1 - \\Delta T_2) / \\ln(\\Delta T_1 / \\Delta T_2)\\).</i></p>"
        "<p><b>Podaj \\(\\dot{Q}\\) [kW]:</b></p>",
        "{U} * {A} * (({t1g} - {t1z}) - ({t2g} - {t2z})) / log(({t1g} - {t1z}) / ({t2g} - {t2z})) / 1000",
        4.0, [("t1g", 100, 120, 0), ("t2g", 60, 70, 0), ("t1z", 15, 25, 0), ("t2z", 35, 45, 0),
         ("U", 200, 400, 0), ("A", 5, 15, 0)],
        decimals=1,
        feedback="<p>Tok rozwiązania: \\(\\Delta T_1 = t_{g,we} - t_{z,we}\\), "
                 "\\(\\Delta T_2 = t_{g,wy} - t_{z,wy}\\), "
                 "\\(\\Delta T_{lm} = (\\Delta T_1 - \\Delta T_2)/\\ln(\\Delta T_1/\\Delta T_2)\\), "
                 "\\(\\dot{Q} = U A \\Delta T_{lm}\\) (W → kW). "
                 "Wykład W14 „5. Wymienniki Ciepła”, „Współprąd vs Przeciwprąd”.</p>")

    write_xml(quiz, 'egzamin_zadania.xml')
    print(f"  Total calculated questions generated.")

# ============================================================
if __name__ == '__main__':
    print("Generating Moodle XML for exam...")
    make_teoria()
    make_zadania()
    print("Done.")
