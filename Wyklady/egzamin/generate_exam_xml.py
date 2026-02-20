#!/usr/bin/env python3
"""Generate Moodle XML files for exam questions.
- egzamin_teoria.xml: multichoice + truefalse (40 questions)
- egzamin_zadania.xml: calculated type with 50 dataset items (randomized)
Category: egzamin
"""
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os, random, math

random.seed(42)
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
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

def add_calculated_question(quiz, name, html, formula, tolerance, grade,
                            variables, tol_type=2):
    """Add a calculated question with dataset definitions.
    variables: list of (varname, min, max, decimals)
    formula: Moodle formula string using {varname}
    """
    q = ET.SubElement(quiz, 'question', type='calculated')
    q_name = ET.SubElement(q, 'name')
    ET.SubElement(q_name, 'text').text = name
    q_qt = ET.SubElement(q, 'questiontext', format='html')
    ET.SubElement(q_qt, 'text').text = html
    q_gf = ET.SubElement(q, 'generalfeedback', format='html')
    ET.SubElement(q_gf, 'text')
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

# ============================================================
# 1. TEORIA — multichoice & truefalse (unchanged logic)
# ============================================================
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
          ("\\(\\Delta U\\)", 0), ("\\(Q - \\Delta H\\)", 0)]),
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
          ("ciśnienie osiąga wartość maksymalną", 0)]),
        ("P07_Stopien_suchosci",
         "<p><b>P7.</b> Stopień suchości pary mokrej \\(x = 0{,}85\\) oznacza, że mieszanina zawiera:</p>",
         [("85% cieczy i 15% pary", 0), ("85% pary i 15% cieczy", 100),
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
          ("izentropowej (adiabatycznej odwracalnej)", 100)]),
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
          ("dławienia (przepływu przez opór bez wymiany ciepła)", 100),
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
         "<p><b>P27.</b> Wymiennik przeciwprądowy pozwala osiągnąć większą średnią różnicę temperatur niż wymiennik współprądowy przy tych samych warunkach brzegowych.</p>", True),
        ("P28_PF_Dlawienie_odwr",
         "<p><b>P28.</b> Proces dławienia w zaworze redukcyjnym jest odwracalny.</p>", False),
        ("P29_PF_Eta_Carnot",
         "<p><b>P29.</b> Sprawność termiczna rzeczywistego obiegu silnikowego może przekroczyć sprawność Carnota dla tych samych temperatur skrajnych.</p>", False),
        ("P30_PF_Kogeneracja",
         "<p><b>P30.</b> Kogeneracja (CHP) to jednoczesne wytwarzanie energii elektrycznej i ciepła użytkowego z tego samego paliwa.</p>", True),
    ]

    for name, qtext, answers in questions:
        q = ET.SubElement(quiz, 'question', type='multichoice')
        q_name = ET.SubElement(q, 'name')
        ET.SubElement(q_name, 'text').text = name
        q_qt = ET.SubElement(q, 'questiontext', format='html')
        ET.SubElement(q_qt, 'text').text = qtext
        q_gf = ET.SubElement(q, 'generalfeedback', format='html')
        ET.SubElement(q_gf, 'text')
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

    for name, qtext, correct in tf_questions:
        q = ET.SubElement(quiz, 'question', type='truefalse')
        q_name = ET.SubElement(q, 'name')
        ET.SubElement(q_name, 'text').text = name
        q_qt = ET.SubElement(q, 'questiontext', format='html')
        ET.SubElement(q_qt, 'text').text = qtext
        q_gf = ET.SubElement(q, 'generalfeedback', format='html')
        ET.SubElement(q_gf, 'text')
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
        2, 3.0,
        [("m", 1.0, 5.0, 1), ("T1", 5, 30, 0), ("T2", 200, 400, 0)])

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
        2, 3.0,
        [("m", 0.5, 3.0, 1), ("T1", 10, 30, 0), ("T2", 200, 350, 0)])

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
        2, 3.0,
        [("mdot", 80, 160, 0), ("h1", 3200, 3500, 0),
         ("h2", 2300, 2600, 0), ("c1", 30, 80, 0), ("c2", 5, 20, 0)])

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
        2, 3.0,
        [("mdot", 2.0, 6.0, 1), ("h1", 280, 320, 0), ("h2", 480, 560, 0)])

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
        0.01, 2.0,
        [("TH", 500, 900, 0), ("TL", 15, 35, 0)])

    # ---- Zad 3b: Q_odpr w GJ ----
    add_calculated_question(quiz,
        "Zad03b_Q_odpr_GJ",
        "<p><b>Zadanie 3b — Straty ciepła w skraplaczu</b></p>"
        "<p>(kontynuacja Zadania 3a) Moc elektryczna bloku wynosi <b>{Pel}</b> MW, "
        "a jego sprawność rzeczywista stanowi <b>{efrac}</b> sprawności Carnota. "
        "Obliczyć ilość ciepła odprowadzonego w skraplaczu w ciągu <b>{th}</b> godzin pracy.</p>"
        "<p><i>Wskazówka: Patrz Karta Wzorów — związek moc–ciepło. 1 MWh = 3,6 GJ.</i></p>"
        "<p><b>Podaj \\(Q_{odpr}\\) [GJ]:</b></p>",
        "({Pel} / ({efrac} * (1 - ({TL}+273.15)/({TH}+273.15))) - {Pel}) * {th} * 3.6",
        5, 5.0,
        [("TH", 500, 900, 0), ("TL", 15, 35, 0),
         ("Pel", 200, 500, 0), ("efrac", 0.40, 0.55, 2), ("th", 8, 24, 0)])

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
        2, 3.0,
        [("T1", 10, 30, 0), ("p1", 1, 2, 0), ("p2", 5, 12, 0)])

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
        2, 3.0,
        [("TL", -25, -10, 0), ("TH", 25, 40, 0), ("P", 0.3, 1.5, 1)])

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
        2, 3.0,
        [("m", 1.0, 4.0, 1), ("T1", 15, 35, 0), ("p1", 5, 12, 0), ("p2", 1, 2, 0)])

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
        5, 3.0,
        [("mdot", 2.0, 6.0, 1), ("h2", 2900, 3200, 0), ("tw", 20, 40, 0)])

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
        2, 3.0,
        [("TL", -10, 0, 0), ("TH", 18, 25, 0), ("P", 1.5, 4.0, 1),
         ("efrac", 0.30, 0.50, 2)])

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
        1, 3.0,
        [("tzew", -20, -5, 0), ("twew", 18, 24, 0), ("eta", 60, 85, 0)])

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
        1, 3.0,
        [("m1", 0.5, 1.5, 1), ("t1", -15, -5, 0),
         ("m2", 1.5, 3.5, 1), ("t2", 18, 25, 0)])

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
        0.5, 3.0,
        [("m1", 0.5, 1.5, 1), ("X1", 1.0, 3.0, 1),
         ("m2", 1.5, 3.5, 1), ("X2", 6.0, 10.0, 1)])

    write_xml(quiz, 'egzamin_zadania.xml')
    print(f"  Total calculated questions generated.")

# ============================================================
if __name__ == '__main__':
    print("Generating Moodle XML for exam...")
    make_teoria()
    make_zadania()
    print("Done.")
