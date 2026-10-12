#!/usr/bin/env python3
"""
Generate Moodle-compatible 'calculated' homework quizzes (cw01–cw07)
with randomized variable pools.

Each numerical question is converted from static 'numerical' type to
a Moodle 'calculated' type with {variable} placeholders and
pre-generated dataset items.

This version uses a GLOBAL DATASET MATRIX so that all quizzes share
the same random values for shared variables (e.g. tw_in).

Treść pytań (questiontext, graderinfo) jest zapisywana jako zwykły tekst
elementu <text> (ElementTree koduje < > & jako encje). NIE wolno owijać jej
w "<![CDATA[...]]>" – taki napis zostałby zakodowany encjami i Moodle
wyświetliłby studentowi literalne "]]>".

Zasady oceniania (wspólne dla wszystkich pytań calculated):
- tolerancja względna 2 % (tolerancetype 1), podniesiona tylko tam, gdzie
  zaokrąglenie z polecenia daje większy błąd; nominalna (tolerancetype 2)
  tylko dla wyników mogących być równe 0 (Ćw6);
- correctanswerlength zgodne z poleceniem w treści (1 lub 2 miejsca po
  przecinku; Ćw2 Q1: 2 cyfry znaczące, correctanswerformat 2);
- pytania powiązane logicznie zawierają w treści komplet danych (losowania są niezależne)
  wzoru (zbiory są private i niesynchronizowane – student dostaje w każdym
  pytaniu inne losowanie).

Usage:
    python tools/randomize_homework.py [--out DIR]
"""

import random
import os
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

random.seed(2025)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                          "Cwiczenia", "homework")
if "--out" in sys.argv:
    OUTPUT_DIR = sys.argv[sys.argv.index("--out") + 1]

N_ITEMS = 50  # number of pre-generated dataset values


# ─────────────────────────────────────────────
# 1. Global Configuration (Schema)
# ─────────────────────────────────────────────
#
# Klucze opcjonalne:
#   "draw": (a, b) – wartości są losowane z przedziału [a, b] (jak w pierwotnej
#            wersji zbioru), a następnie liniowo przeskalowane do [min, max];
#            dzięki temu zmiana zakresu nie zmienia sekwencji generatora ani
#            pozostałych zbiorów.
#   "seed": n – zbiór losowany osobnym generatorem random.Random(n).randint
#            (zmienna dodana później, nie zaburza sekwencji głównego ziarna).

VARIABLES_SCHEMA = {
    # --- Shared / Global ---
    "tw_in":          {"min": 8, "max": 25, "dec": 0},   # Shared: Cw02, Cw05
    "eta_kotla":      {"min": 88, "max": 94, "dec": 0},  # Shared: Cw03, Cw07

    # --- Cw01 (Sprężarka) ---
    "cw01_V":           {"min": 3, "max": 8, "dec": 0},
    "patm_mmHg":        {"min": 740, "max": 780, "dec": 0},
    "cw01_t_otoczenia": {"min": 15, "max": 30, "dec": 0}, # Dawniej t1
    "p_full":           {"min": 8.0, "max": 12.0, "dec": 1},
    "t_full":           {"min": 35, "max": 50, "dec": 0},

    # --- Cw02 (Odzysk ciepła) ---
    "Qch":              {"min": 6, "max": 12, "dec": 1},
    "eta_odz":          {"min": 70, "max": 90, "dec": 0},
    "tw_out_cw02":      {"min": 40, "max": 55, "dec": 0},

    # --- Cw03 (Kocioł) ---
    "Vgas":             {"min": 100, "max": 250, "dec": 0},
    "kgH2O":            {"min": 1.4, "max": 1.8, "dec": 1},
    # ciepło skraplania wody: max 2501 kJ/kg (0 °C); przy 40–55 °C r = 2370–2406
    # (pierwotny zakres 2400–2550 był niefizyczny)
    "r_w":              {"min": 2380, "max": 2460, "dec": 0, "draw": (2400, 2550)},
    "Quz":              {"min": 1500, "max": 2500, "dec": 0},

    # --- Cw04 (Kogeneracja) ---
    "Nt":               {"min": 100, "max": 250, "dec": 1},
    "eta_gen":          {"min": 85, "max": 95, "dec": 0},
    "h_rok":            {"min": 3000, "max": 5000, "dec": 0},
    "cena_kWh":         {"min": 0.60, "max": 1.00, "dec": 2},
    "koszt_inv":        {"min": 100000, "max": 300000, "dec": 0},

    # --- Cw05 (Wymiennik) ---
    "Qwym":             {"min": 100, "max": 250, "dec": 0},
    "tw_out_cw05":      {"min": 85, "max": 100, "dec": 0},
    "Tsp_in":           {"min": 523, "max": 623, "dec": 0},
    "Tsp_out":          {"min": 393, "max": 473, "dec": 0},

    # --- Cw06 (Chłodnictwo) ---
    "cw06_t_parowania": {"min": -5, "max": 5, "dec": 0}, # Dawniej t0
    "dTsh":             {"min": 3, "max": 8, "dec": 0},
    "tk":               {"min": 35, "max": 45, "dec": 0},
    "dTsc":             {"min": 3, "max": 8, "dec": 0},

    # --- Cw07 (Rekuperacja) ---
    "eta_rek":          {"min": 60, "max": 85, "dec": 0},
    "t_cz":             {"min": -20, "max": -5, "dec": 0},
    "t_wy":             {"min": 20, "max": 24, "dec": 0},
    "Vdot_air":         {"min": 5000, "max": 15000, "dec": 0},
    "h_sezon":          {"min": 2500, "max": 4000, "dec": 0},
    "cena_gaz":         {"min": 0.20, "max": 0.35, "dec": 2},
    "koszt_rek":        {"min": 15000, "max": 40000, "dec": 0},
    # średnia temperatura zewnętrzna w sezonie grzewczym
    "t_sr":             {"min": 5, "max": 13, "dec": 0, "seed": 2026},

    # --- Cw05 (Egzergia) – temperatura otoczenia (hali) T0 = t_hali + 273,15 ---
    "t_hali":           {"min": 15, "max": 25, "dec": 0, "seed": 2027},
}


# ─────────────────────────────────────────────
# 2. Helpers
# ─────────────────────────────────────────────

def gen_items(vmin, vmax, decimals, n=N_ITEMS):
    """Generate n random values uniformly distributed in [vmin, vmax]."""
    items = []
    for _ in range(n):
        val = random.uniform(vmin, vmax)
        val = round(val, decimals)
        items.append(val)
    return items


def fmt_val(val, decimals):
    """Format a float to a string with given decimals."""
    if decimals == 0:
        return str(int(round(val)))
    return f"{val:.{decimals}f}"


def generate_global_data():
    """Generate the master dataset matrix for all variables."""
    data = {}
    for key, conf in VARIABLES_SCHEMA.items():
        if "seed" in conf:
            rng = random.Random(conf["seed"])
            items = [rng.randint(conf["min"], conf["max"]) for _ in range(N_ITEMS)]
        elif "draw" in conf:
            a, b = conf["draw"]
            scale = (conf["max"] - conf["min"]) / (b - a)
            items = [round(conf["min"] + (v - a) * scale, conf["dec"])
                     for v in gen_items(a, b, conf["dec"])]
        else:
            items = gen_items(conf["min"], conf["max"], conf["dec"])
        data[key] = {
            "items": items,
            "min": conf["min"],
            "max": conf["max"],
            "dec": conf["dec"]
        }
    return data


def add_dataset_def(parent, name, vmin, vmax, decimals, items):
    """Add a <dataset_definition> element to XML parent."""
    dd = ET.SubElement(parent, "dataset_definition")

    status = ET.SubElement(dd, "status")
    ET.SubElement(status, "text").text = "private"

    name_el = ET.SubElement(dd, "name")
    ET.SubElement(name_el, "text").text = name

    ET.SubElement(dd, "type").text = "calculated"

    dist = ET.SubElement(dd, "distribution")
    ET.SubElement(dist, "text").text = "uniform"

    mn = ET.SubElement(dd, "minimum")
    ET.SubElement(mn, "text").text = fmt_val(vmin, decimals)

    mx = ET.SubElement(dd, "maximum")
    ET.SubElement(mx, "text").text = fmt_val(vmax, decimals)

    dec = ET.SubElement(dd, "decimals")
    ET.SubElement(dec, "text").text = str(decimals)

    ET.SubElement(dd, "itemcount").text = str(len(items))
    ET.SubElement(dd, "number_of_items").text = str(len(items))

    di_parent = ET.SubElement(dd, "dataset_items")
    for i, val in enumerate(items, 1):
        di = ET.SubElement(di_parent, "dataset_item")
        ET.SubElement(di, "number").text = str(i)
        ET.SubElement(di, "value").text = fmt_val(val, decimals)


def build_calculated_question(
    name, question_html, formula, variables_map, global_data, defaultgrade,
    tolerance=0.02, tolerance_type=1, penalty="0.1000000",
    general_feedback_html=None, correct_answer_format=1,
    correct_answer_length=1
):
    """Build a full <question type='calculated'> element.

    variables_map: dict mapping local XML placeholder name -> global data key
                   e.g. {"t1": "cw01_t_otoczenia"}
    tolerance_type: 1 = względna (ułamek), 2 = nominalna
    correct_answer_format: 1 = miejsca po przecinku, 2 = cyfry znaczące
    """
    q = ET.Element("question", type="calculated")

    # Name
    n = ET.SubElement(q, "name")
    ET.SubElement(n, "text").text = name

    # Question text
    qt = ET.SubElement(q, "questiontext", format="html")
    ET.SubElement(qt, "text").text = question_html

    # General feedback
    gf = ET.SubElement(q, "generalfeedback", format="html")
    ET.SubElement(gf, "text").text = general_feedback_html or ""

    # Grades
    ET.SubElement(q, "defaultgrade").text = f"{float(defaultgrade):.7f}"
    ET.SubElement(q, "penalty").text = penalty
    ET.SubElement(q, "hidden").text = "0"
    ET.SubElement(q, "idnumber")
    ET.SubElement(q, "synchronize").text = "0"
    ET.SubElement(q, "single").text = "0"
    ET.SubElement(q, "answernumbering").text = "abc"
    ET.SubElement(q, "shuffleanswers").text = "1"
    for fb_tag in ("correctfeedback", "partiallycorrectfeedback", "incorrectfeedback"):
        fb = ET.SubElement(q, fb_tag)
        ET.SubElement(fb, "text")

    # Answer with formula
    ans = ET.SubElement(q, "answer", fraction="100")
    ET.SubElement(ans, "text").text = formula
    ET.SubElement(ans, "tolerance").text = str(tolerance)
    ET.SubElement(ans, "tolerancetype").text = str(tolerance_type)
    ET.SubElement(ans, "correctanswerformat").text = str(correct_answer_format)
    ET.SubElement(ans, "correctanswerlength").text = str(correct_answer_length)
    fb = ET.SubElement(ans, "feedback", format="html")
    ET.SubElement(fb, "text")

    # Unit settings
    ET.SubElement(q, "unitgradingtype").text = "0"
    ET.SubElement(q, "unitpenalty").text = "1.0000000"
    ET.SubElement(q, "showunits").text = "3"
    ET.SubElement(q, "unitsleft").text = "0"

    # Dataset definitions
    dds = ET.SubElement(q, "dataset_definitions")

    # Iterate over required variables for this question
    for local_name, global_key in variables_map.items():
        if global_key not in global_data:
            raise KeyError(f"Missing global key: {global_key} for local var: {local_name}")

        g_var = global_data[global_key]
        add_dataset_def(dds, local_name, g_var["min"], g_var["max"],
                        g_var["dec"], g_var["items"])

    return q


def build_multichoice_question(name, question_html, answers, defaultgrade=1, single=True):
    """Build a <question type='multichoice'> element."""
    q = ET.Element("question", type="multichoice")
    n = ET.SubElement(q, "name")
    ET.SubElement(n, "text").text = name

    qt = ET.SubElement(q, "questiontext", format="html")
    ET.SubElement(qt, "text").text = question_html

    ET.SubElement(q, "defaultgrade").text = str(defaultgrade)
    ET.SubElement(q, "penalty").text = "0.3333333"
    ET.SubElement(q, "single").text = "true" if single else "false"
    ET.SubElement(q, "shuffleanswers").text = "true"

    for text, fraction in answers:
        a = ET.SubElement(q, "answer", fraction=str(fraction))
        ET.SubElement(a, "text").text = text

    return q


def build_essay_question(name, question_html, defaultgrade=3, graderinfo_html=None):
    """Build a <question type='essay'> element."""
    q = ET.Element("question", type="essay")
    n = ET.SubElement(q, "name")
    ET.SubElement(n, "text").text = name

    qt = ET.SubElement(q, "questiontext", format="html")
    ET.SubElement(qt, "text").text = question_html

    ET.SubElement(q, "defaultgrade").text = str(defaultgrade)
    ET.SubElement(q, "penalty").text = "0"

    if graderinfo_html:
        gi = ET.SubElement(q, "graderinfo", format="html")
        ET.SubElement(gi, "text").text = graderinfo_html

    return q


def build_category(path):
    """Build a <question type='category'> element."""
    q = ET.Element("question", type="category")
    cat = ET.SubElement(q, "category")
    ET.SubElement(cat, "text").text = path
    return q


def prettify_xml(root):
    """Return a pretty-printed XML string."""
    rough = ET.tostring(root, encoding="unicode", xml_declaration=False)
    rough = '<?xml version="1.0" encoding="UTF-8"?>\n' + rough
    dom = minidom.parseString(rough)
    pretty = dom.toprettyxml(indent="    ", encoding=None)
    lines = pretty.split("\n")
    if lines[0].startswith("<?xml"):
        lines[0] = '<?xml version="1.0" encoding="UTF-8"?>'
    return "\n".join(lines)


def write_quiz(filename, questions):
    """Write a list of question elements to a quiz XML file."""
    root = ET.Element("quiz")
    for q in questions:
        root.append(q)

    xml_str = prettify_xml(root)
    filepath = os.path.join(OUTPUT_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(xml_str)
    print(f"  → {filepath}")


# ─────────────────────────────────────────────
# 3. Quiz Generators
# ─────────────────────────────────────────────

def generate_cw01(global_data):
    """Ćw. 1 — Dobór sprężarki"""
    # Mapping local variable names to global keys
    var_map = {
        "V_zb": "cw01_V",
        "patm_mmHg": "patm_mmHg",
        "t1": "cw01_t_otoczenia",
        "p_full": "p_full",
        "t_full": "t_full",
    }

    questions = [
        build_category("$course$/Ćw. 1 – Dobór sprężarki (Praca domowa)"),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Masa powietrza w zbiorniku pustym [kg]",
            question_html=(
                '<p>Zbiornik o objętości \\( V_{{zb}} = \\) <b>{V_zb}</b> m³ '
                'zawiera powietrze przy ciśnieniu atmosferycznym '
                '\\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg '
                'i temperaturze \\( t = \\) <b>{t1}</b>°C.</p>'
                '<p>Oblicz masę powietrza w zbiorniku. '
                'Przyjmij \\( R = 287 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Wynik podaj w <strong>kg</strong> '
                '(zaokrąglij do 1 miejsca po przecinku).</p>'
                '<p><em>Wskazówka:</em> \\( pV_{{zb}} = mRT \\)</p>'
            ),
            formula="({patm_mmHg} * 133.322) * {V_zb} / (287 * ({t1} + 273.15))",
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Masa powietrza w zbiorniku pełnym [kg]",
            question_html=(
                '<p>Zbiornik o objętości \\( V_{{zb}} = \\) <b>{V_zb}</b> m³ '
                'został naładowany sprężonym powietrzem do ciśnienia '
                '\\( p = \\) <b>{p_full}</b> bar (abs) '
                'i temperatury \\( t = \\) <b>{t_full}</b>°C.</p>'
                '<p>Oblicz masę powietrza w zbiorniku. '
                'Przyjmij \\( R = 287 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Wynik podaj w <strong>kg</strong> '
                '(zaokrąglij do 1 miejsca po przecinku).</p>'
            ),
            formula="{p_full} * 100000 * {V_zb} / (287 * ({t_full} + 273.15))",
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Wydajność masowa sprężarki [kg/h]",
            question_html=(
                '<p>Zbiornik o objętości \\( V_{{zb}} = \\) <b>{V_zb}</b> m³ '
                'musi być napompowany od ciśnienia atmosferycznego '
                '(\\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg, '
                '\\( t = \\) <b>{t1}</b>°C) '
                'do ciśnienia roboczego '
                '(\\( p = \\) <b>{p_full}</b> bar (abs), '
                '\\( t = \\) <b>{t_full}</b>°C) '
                'w czasie 1 godziny.</p>'
                '<p>Oblicz wymaganą wydajność masową sprężarki '
                '\\( \\dot{{m}} \\) w <strong>kg/h</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula=(
                "{p_full} * 100000 * {V_zb} / (287 * ({t_full} + 273.15)) "
                "- ({patm_mmHg} * 133.322) * {V_zb} / (287 * ({t1} + 273.15))"
            ),
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Wydajność objętościowa sprężarki [m³/h]",
            question_html=(
                '<p>Sprężarka ma w ciągu 1 godziny napełnić zbiornik o objętości '
                '\\( V_{{zb}} = \\) <b>{V_zb}</b> m³ od stanu „pustego” '
                '(\\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg, '
                '\\( t = \\) <b>{t1}</b>°C) do stanu „pełnego” '
                '(\\( p = \\) <b>{p_full}</b> bar (abs), '
                '\\( t = \\) <b>{t_full}</b>°C). '
                'Warunki ssania: \\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg, '
                '\\( t = \\) <b>{t1}</b>°C. '
                'Przyjmij \\( R = 287 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Oblicz wymaganą wydajność objętościową sprężarki '
                'w warunkach ssania \\( \\dot{{V}} \\) w <strong>m³/h</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula=(
                "({p_full} * 100000 * {V_zb} / (287 * ({t_full} + 273.15)) "
                "- ({patm_mmHg} * 133.322) * {V_zb} / (287 * ({t1} + 273.15))) "
                "* 287 * ({t1} + 273.15) / ({patm_mmHg} * 133.322)"
            ),
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_multichoice_question(
            name="Ćw1 Zad. dom. – Dlaczego temperatura rośnie?",
            question_html=(
                '<p>Dlaczego w zbiorniku po napełnieniu sprężonym '
                'powietrzem temperatura wzrosła?</p>'
            ),
            answers=[
                ("Praca sprężania zamieniana jest na energię wewnętrzną gazu (I zasada termodynamiki).", 100),
                ("Zbiornik jest ogrzewany przez otoczenie.", 0),
                ("Powietrze się rozszerza i to powoduje wzrost temperatury.", 0),
                ("Ciśnienie atmosferyczne ogrzewa powietrze w zbiorniku.", 0),
            ],
            defaultgrade=1
        ),
    ]

    write_quiz("cw01_praca_domowa.xml", questions)


def generate_cw02(global_data):
    """Ćw. 2 — Odzysk ciepła ze sprężarki"""
    var_map = {
        "Qch": "Qch",
        "eta_odz": "eta_odz",
        "tw_in": "tw_in",       # Shared
        "tw_out": "tw_out_cw02", # Specific
    }

    questions = [
        build_category("$course$/Ćw. 2 – Odzysk ciepła ze sprężarki (Praca domowa)"),

        # wynik 104–385 kg/h (w kg/s byłoby 0,03–0,11 – za mało cyfr); 1 miejsce po przecinku
        build_calculated_question(
            name="Ćw2 Zad. dom. – Strumień wody [kg/h]",
            question_html=(
                '<p>Z chłodnicy sprężarki odzyskujemy '
                '<b>{eta_odz}</b>% ciepła, tj. '
                '\\( \\dot{{Q}}_{{odz}} = \\) '
                '<b>{eta_odz}</b>/100 × <b>{Qch}</b> kW.</p>'
                '<p>Chcemy podgrzać wodę z <b>{tw_in}</b>°C '
                'do <b>{tw_out}</b>°C. '
                'Ciepło właściwe wody: \\( c_w = 4190 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Oblicz wymagany strumień masy wody '
                '\\( \\dot{{m}}_w \\) w <strong>kg/h</strong>.</p>'
                '<p><em>Wzór:</em> \\( \\dot{{Q}} = \\dot{{m}}_w \\cdot c_w \\cdot \\Delta T \\) '
                '(wynik w kg/s pomnóż przez 3600).</p>'
                '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>'
            ),
            formula="{Qch} * {eta_odz} / 100 * 1000 / (4190 * ({tw_out} - {tw_in})) * 3600",
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        # 1 kg/s wody = 60 l/min; zaokrąglenie do 1 miejsca daje do 2,5 % (1,8465 → 1,8)
        build_calculated_question(
            name="Ćw2 Zad. dom. – Strumień wody [l/min]",
            question_html=(
                '<p>Z chłodnicy sprężarki można odzyskać ciepło. '
                'Woda ma być podgrzana z <b>{tw_in}</b>°C '
                'do <b>{tw_out}</b>°C.</p>'
                '<p>\\( c_w = 4190 \\text{{ J/(kg·K)}} \\), '
                '\\( \\rho_w = 1000 \\text{{ kg/m}}^3 \\).</p>'
                '<p>Ciepło do dyspozycji: '
                '\\( \\dot{{Q}}_{{odz}} = \\) <b>{Qch}</b> × <b>{eta_odz}</b>/100 kW.</p>'
                '<p>Oblicz strumień objętościowy wody w <strong>l/min</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula="{Qch} * {eta_odz} / 100 * 1000 / (4190 * ({tw_out} - {tw_in})) * 60",
            tolerance=0.03,
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_multichoice_question(
            name="Ćw2 Zad. dom. – Interpretacja wyniku",
            question_html=(
                '<p>Obliczono strumień wody wynikający z odzysku ciepła '
                'ze sprężarki. Która z poniższych interpretacji jest poprawna?</p>'
            ),
            answers=[
                ("To wystarczy na zasilenie 1–2 umywalek w szatni — odzysk ciepła jest opłacalny.", 100),
                ("To zbyt mały strumień — odzysk ciepła nie ma sensu ekonomicznego.", 0),
                ("Strumień jest zbyt duży i spowoduje problemy z ciśnieniem wody.", 0),
                ("Nie można podgrzewać wody ciepłem ze sprężarki ze względów bezpieczeństwa.", 0),
            ],
            defaultgrade=1
        ),

        build_essay_question(
            name="Ćw2 Zad. dom. – Bilans energetyczny sprężarkowni",
            question_html=(
                '<p>Wykonaj pełny bilans energetyczny sprężarkowni '
                'z odzyskiem ciepła. Uwzględnij:</p>'
                '<ul>'
                '<li>Moc dostarczoną do sprężarki (silnik elektryczny)</li>'
                '<li>Ciepło odprowadzone w chłodnicy</li>'
                '<li>Ciepło odzyskane</li>'
                '<li>Ciepło tracone do otoczenia</li>'
                '</ul>'
                '<p>Narysuj schemat bilansowy i określ, jaka część energii '
                'jest „stracona".</p>'
            ),
            defaultgrade=3,
            graderinfo_html=(
                '<p>Sprawdź: bilans musi się zgadzać. Ciepło odzyskane = Qch × eta_odz/100.</p>'
            )
        ),
    ]

    write_quiz("cw02_praca_domowa.xml", questions)


def generate_cw03(global_data):
    """Ćw. 3 — Kocioł kondensacyjny"""
    var_map = {
        "Vgas": "Vgas",
        "kgH2O": "kgH2O",
        "r_w": "r_w",
        "eta_kotla": "eta_kotla", # Shared
        "Quz": "Quz",
    }

    questions = [
        build_category("$course$/Ćw. 3 – Kocioł kondensacyjny (Praca domowa)"),

        build_calculated_question(
            name="Ćw3 Zad. dom. – Masa pary wodnej w spalinach [kg/h]",
            question_html=(
                '<p>Kocioł zużywa \\( V_{{gaz}} = \\) <b>{Vgas}</b> m³/h '
                'gazu ziemnego. Przy spalaniu 1 m³ gazu powstaje ok. '
                '<b>{kgH2O}</b> kg wody w spalinach.</p>'
                '<p>Oblicz masowy strumień pary wodnej w spalinach '
                'w <strong>kg/h</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula="{Vgas} * {kgH2O}",
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw3 Zad. dom. – Dodatkowe ciepło z kondensacji [kW]",
            question_html=(
                '<p>W spalinach kotła powstaje '
                '\\( \\dot{{m}}_w = \\) <b>{Vgas}</b> × <b>{kgH2O}</b> kg/h '
                'pary wodnej. Ciepło parowania wody wynosi '
                '\\( r = \\) <b>{r_w}</b> kJ/kg.</p>'
                '<p>Oblicz dodatkowy strumień ciepła '
                '\\( \\dot{{Q}}_{{kond}} \\), który można odzyskać '
                'skraplając <strong>całą</strong> parę wodną ze spalin.</p>'
                '<p>Wynik podaj w <strong>kW</strong>. '
                'Zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula="{Vgas} * {kgH2O} * {r_w} / 3600",
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_calculated_question(
            name="Ćw3 Zad. dom. – Wzrost sprawności [punkty procentowe]",
            question_html=(
                '<p>Kocioł ma sprawność \\( \\eta = \\) <b>{eta_kotla}</b>% '
                'i moc cieplną \\( \\dot{{Q}}_{{uż}} = \\) <b>{Quz}</b> kW. '
                'Kocioł zużywa \\( V_{{gaz}} = \\) <b>{Vgas}</b> m³/h gazu; '
                'przy spalaniu 1 m³ gazu powstaje ok. <b>{kgH2O}</b> kg wody w spalinach, '
                'ciepło skraplania \\( r = \\) <b>{r_w}</b> kJ/kg. '
                'Dodatkowy odzysk ciepła z kondensacji '
                '\\( \\dot{{Q}}_{{kond}} \\) wynika ze skroplenia całej pary wodnej ze spalin.</p>'
                '<p>O ile <strong>punktów procentowych</strong> wzrośnie '
                'sprawność kotłowni po zainstalowaniu kondensacji spalin?</p>'
                '<p>\\( \\Delta\\eta = '
                '\\frac{{\\dot{{Q}}_{{kond}}}}{{\\dot{{Q}}_{{paliwa}}}} '
                '\\cdot 100\\% \\), gdzie '
                '\\( \\dot{{Q}}_{{paliwa}} = '
                '\\frac{{\\dot{{Q}}_{{uż}}}}{{\\eta}} \\)</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula=(
                "({Vgas} * {kgH2O} * {r_w} / 3600) / "
                "({Quz} / ({eta_kotla} / 100)) * 100"
            ),
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_multichoice_question(
            name="Ćw3 Zad. dom. – Temperatura punktu rosy spalin",
            question_html=(
                '<p>Aby kocioł kondensacyjny mógł odzyskiwać ciepło '
                'skraplania, temperatura spalin musi spaść poniżej pewnej '
                'wartości. Jak nazywa się ta temperatura?</p>'
            ),
            answers=[
                ("Temperatura punktu rosy spalin (ok. 55°C dla gazu ziemnego)", 100),
                ("Temperatura krytyczna wody (374°C)", 0),
                ("Temperatura nasycenia przy ciśnieniu atmosferycznym (100°C)", 0),
                ("Temperatura zapłonu gazu ziemnego", 0),
            ],
            defaultgrade=1
        ),

        build_essay_question(
            name="Ćw3 Zad. dom. – Warunki opłacalności kotła kondensacyjnego",
            question_html=(
                '<p>Wyjaśnij, dlaczego w praktyce nie zawsze udaje '
                'się odzyskać 100% ciepła kondensacji ze spalin.</p>'
            ),
            defaultgrade=2,
            graderinfo_html=(
                '<p>Oczekiwane odpowiedzi: (1) kondensacja zachodzi tylko wtedy, gdy '
                'temperatura wody powrotnej jest niższa od punktu rosy spalin (ok. 55 °C '
                'dla gazu ziemnego) – przy wysokiej temperaturze powrotu (np. 60–70 °C) '
                'para nie skrapla się wcale lub tylko częściowo; (2) nawet przy niskim '
                'powrocie spaliny opuszczają kocioł jako nasycone w temperaturze powyżej '
                'otoczenia, więc część pary zawsze uchodzi; (3) kondensat jest kwaśny '
                '(korozja) – potrzebne materiały odporne i odprowadzenie kondensatu; '
                '(4) ciepło skraplania ma niską temperaturę (40–55 °C), co ogranicza '
                'jego wykorzystanie (np. tylko podgrzew wody zasilającej).</p>'
            )
        ),
    ]

    write_quiz("cw03_praca_domowa.xml", questions)


def generate_cw04(global_data):
    """Ćw. 4 — Opłacalność kogeneracji"""
    var_map = {
        "Nt": "Nt",
        "eta_gen": "eta_gen",
        "h_rok": "h_rok",
        "cena_kWh": "cena_kWh",
        "koszt_inv": "koszt_inv",
    }
    # zmienna {Nt} to rzeczywista moc na wale N_r (jak w Zad. 4.4); nazwa zbioru bez zmian
    nel = ('\\( N_{{el}} = N_r \\cdot \\eta_{{gen}} = \\) '
           '<b>{Nt}</b> kW × <b>{eta_gen}</b>/100')

    questions = [
        build_category("$course$/Ćw. 4 – Opłacalność kogeneracji (Praca domowa)"),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Moc elektryczna generatora [kW]",
            question_html=(
                '<p>Turbina parowa o rzeczywistej mocy na wale (jak \\( N_r \\) w Zad. 4.4) '
                '\\( N_r = \\) <b>{Nt}</b> kW napędza generator '
                'o sprawności \\( \\eta_{{gen}} = \\) <b>{eta_gen}</b>%.</p>'
                '<p>Oblicz moc elektryczną \\( N_{{el}} = N_r \\cdot \\eta_{{gen}} \\) '
                'w <strong>kW</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula="{Nt} * {eta_gen} / 100",
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Roczna produkcja energii [MWh]",
            question_html=(
                '<p>Generator o mocy ' + nel + ' '
                'pracuje <b>{h_rok}</b> h/rok.</p>'
                '<p>Oblicz roczną produkcję energii elektrycznej '
                'w <strong>MWh/rok</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula="{Nt} * {eta_gen} / 100 * {h_rok} / 1000",
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Roczny zysk [PLN]",
            question_html=(
                '<p>Generator o mocy ' + nel + ' pracuje <b>{h_rok}</b> h/rok. '
                'Cena prądu: <b>{cena_kWh}</b> PLN/kWh.</p>'
                '<p>Oblicz roczny zysk (oszczędność) w <strong>PLN</strong>.</p>'
                '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>'
            ),
            formula="{Nt} * {eta_gen} / 100 * {h_rok} * {cena_kWh}",
            variables_map=var_map, global_data=global_data, defaultgrade=2,
            correct_answer_length=2
        ),

        # SPBT 0,13–1,25 roku: zaokrąglenie do 2 miejsc daje do 2,1 % (0,14296 → 0,14)
        build_calculated_question(
            name="Ćw4 Zad. dom. – Czas zwrotu inwestycji SPBT [lata]",
            question_html=(
                '<p>Koszt instalacji turbiny: <b>{koszt_inv}</b> PLN. '
                'Roczny zysk wynika z produkcji energii i ceny prądu: generator o mocy ' + nel + ' '
                'pracuje <b>{h_rok}</b> h/rok, cena prądu <b>{cena_kWh}</b> PLN/kWh.</p>'
                '<p>Oblicz prosty czas zwrotu inwestycji SPBT w <strong>latach</strong>.</p>'
                '<p>\\( SPBT = \\frac{{\\text{{Koszt inwestycji}}}}'
                '{{\\text{{Roczny zysk}}}} \\)</p>'
                '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>'
            ),
            formula="{koszt_inv} / ({Nt} * {eta_gen} / 100 * {h_rok} * {cena_kWh})",
            tolerance=0.03,
            variables_map=var_map, global_data=global_data, defaultgrade=2,
            correct_answer_length=2
        ),

        build_multichoice_question(
            name="Ćw4 Zad. dom. – Czy inwestycja się opłaca?",
            question_html=(
                '<p>Na podstawie obliczeń SPBT, '
                'która z poniższych interpretacji jest NAJLEPSZA?</p>'
            ),
            answers=[
                ("Inwestycja jest bardzo opłacalna — kogeneracja zamiast dławienia pary to duży zysk.", 100),
                ("Inwestycja jest ryzykowna, bo turbina może się zepsuć.", 0),
                ("SPBT < 1 roku oznacza, że obliczenia muszą zawierać błąd.", 0),
                ("Dławienie pary na zaworze jest lepszym rozwiązaniem.", 0),
            ],
            defaultgrade=1
        ),
    ]

    write_quiz("cw04_praca_domowa.xml", questions)


def generate_cw05(global_data):
    """Ćw. 5 — Optymalizacja wymiennika ciepła"""
    var_map = {
        "Qwym": "Qwym",
        "tw_out_new": "tw_out_cw05", # Specific
        "tw_in": "tw_in",           # Shared
        "Tsp_in": "Tsp_in",
        "Tsp_out": "Tsp_out",
    }

    questions = [
        build_category("$course$/Ćw. 5 – Optymalizacja wymiennika ciepła (Praca domowa)"),

        build_calculated_question(
            name="Ćw5 Zad. dom. – Nowy strumień wody [kg/s]",
            question_html=(
                '<p>Wymiennik ciepła spaliny–woda ma moc '
                '\\( \\dot{{Q}} = \\) <b>{Qwym}</b> kW. '
                'Temperatura wylotowa wody: <b>{tw_out_new}</b>°C, '
                'wlotowa: <b>{tw_in}</b>°C.</p>'
                '<p>Ciepło właściwe wody: '
                '\\( c_w = 4{{,}}19 \\text{{ kJ/(kg·K)}} \\).</p>'
                '<p>Oblicz strumień masy wody '
                '\\( \\dot{{m}}_w \\) w <strong>kg/s</strong>.</p>'
                '<p>\\( \\dot{{Q}} = \\dot{{m}}_w \\cdot c_w '
                '\\cdot (T_{{wyj}} - T_{{wej}}) \\)</p>'
                '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>'
            ),
            formula="{Qwym} / (4.19 * ({tw_out_new} - {tw_in}))",
            variables_map=var_map, global_data=global_data, defaultgrade=2,
            correct_answer_length=2
        ),

        # metoda logarytmiczna jak w Zad. 5.2 (ΔS_i = ṁ c ln(T_wyj/T_wej)),
        # pojemności cieplne z bilansu energii; wynik w W/K (111,7–270,9)
        build_calculated_question(
            name="Ćw5 Zad. dom. – Generacja entropii [W/K]",
            question_html=(
                '<p>Wymiennik ciepła: spaliny chłodzą się '
                'z \\( T_{{sp,wej}} = \\) <b>{Tsp_in}</b> K '
                'do \\( T_{{sp,wyj}} = \\) <b>{Tsp_out}</b> K, '
                'woda grzeje się z \\( t_{{w,wej}} = \\) <b>{tw_in}</b>°C '
                'do \\( t_{{w,wyj}} = \\) <b>{tw_out_new}</b>°C.</p>'
                '<p>Strumień ciepła: \\( \\dot{{Q}} = \\) <b>{Qwym}</b> kW.</p>'
                '<p>Oblicz generację entropii w wymienniku (jak w Zad. 5.2):</p>'
                '<p>\\( \\dot{{S}}_{{gen}} = \\Delta\\dot{{S}}_{{sp}} + \\Delta\\dot{{S}}_{{w}}, '
                '\\qquad \\Delta\\dot{{S}}_i = \\dot{{m}}_i \\, c_i \\, '
                '\\ln\\frac{{T_{{i,wyj}}}}{{T_{{i,wej}}}} \\)</p>'
                '<p>Pojemności cieplne strumieni wynikają z bilansu energii: '
                '\\( \\dot{{m}}_w c_w = \\dot{{Q}} / (t_{{w,wyj}} - t_{{w,wej}}) \\), '
                '\\( \\dot{{m}}_s c_s = \\dot{{Q}} / (T_{{sp,wej}} - T_{{sp,wyj}}) \\). '
                'Temperatury wody przelicz na K.</p>'
                '<p>Wynik podaj w <strong>W/K</strong> z dokładnością '
                'do 1 miejsca po przecinku.</p>'
            ),
            formula=(
                "{Qwym} * 1000 * (log(({tw_out_new} + 273.15) / ({tw_in} + 273.15)) "
                "/ ({tw_out_new} - {tw_in}) - log({Tsp_in} / {Tsp_out}) / ({Tsp_in} - {Tsp_out}))"
            ),
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        # Gouy–Stodola jak w Zad. 5.3: B_str = T0 * S_gen, T0 = t_hali + 273,15 (temperatura
        # hali z karty); S_gen z pełnych danych jak w pytaniu wyżej (losowania niezależne).
        # Wynik 32–81 kW; 1 miejsce po przecinku, tolerancja 2 %.
        build_calculated_question(
            name="Ćw5 Zad. dom. – Strata egzergii [kW]",
            question_html=(
                '<p>Wymiennik ciepła: spaliny chłodzą się '
                'z \\( T_{{sp,wej}} = \\) <b>{Tsp_in}</b> K '
                'do \\( T_{{sp,wyj}} = \\) <b>{Tsp_out}</b> K, '
                'woda grzeje się z \\( t_{{w,wej}} = \\) <b>{tw_in}</b>°C '
                'do \\( t_{{w,wyj}} = \\) <b>{tw_out_new}</b>°C. '
                'Strumień ciepła: \\( \\dot{{Q}} = \\) <b>{Qwym}</b> kW. '
                'Temperatura otoczenia (hali): \\( t_0 = \\) <b>{t_hali}</b>°C.</p>'
                '<p>Oblicz generację entropii w wymienniku jak w Zad. 5.2 '
                '(\\( \\dot{{S}}_{{gen}} = \\dot{{m}}_s c_s \\ln\\frac{{T_{{sp,wyj}}}}{{T_{{sp,wej}}}} '
                '+ \\dot{{m}}_w c_w \\ln\\frac{{T_{{w,wyj}}}}{{T_{{w,wej}}}} \\), '
                'pojemności cieplne z bilansu energii: '
                '\\( \\dot{{m}}_w c_w = \\dot{{Q}} / (t_{{w,wyj}} - t_{{w,wej}}) \\), '
                '\\( \\dot{{m}}_s c_s = \\dot{{Q}} / (T_{{sp,wej}} - T_{{sp,wyj}}) \\), '
                'temperatury wody w K), a następnie stratę egzergii '
                'z twierdzenia Gouy–Stodoli (Zad. 5.3):</p>'
                '<p>\\( \\dot{{B}}_{{str}} = T_0 \\cdot \\dot{{S}}_{{gen}}, '
                '\\qquad T_0 = t_0 + 273{{,}}15 \\)</p>'
                '<p>Wynik podaj w <strong>kW</strong> z dokładnością '
                'do 1 miejsca po przecinku.</p>'
            ),
            formula=(
                "({t_hali} + 273.15) * {Qwym} * (log(({tw_out_new} + 273.15) / ({tw_in} + 273.15)) "
                "/ ({tw_out_new} - {tw_in}) - log({Tsp_in} / {Tsp_out}) / ({Tsp_in} - {Tsp_out}))"
            ),
            variables_map=dict(var_map, t_hali="t_hali"), global_data=global_data,
            defaultgrade=3,
            general_feedback_html=(
                '<p>Tok rozwiązania: \\( \\dot{{S}}_{{gen}} \\) jak w Zad. 5.2 (W/K), '
                '\\( T_0 = t_0 + 273{{,}}15 \\) K, '
                '\\( \\dot{{B}}_{{str}} = T_0 \\cdot \\dot{{S}}_{{gen}} \\) (W → kW). '
                'Slajd Ć5 „Zadanie 5.3: Strata Egzergii (Twierdzenie Gouy–Stodoli)”, '
                'pkt 3 zadania domowego (Raport 5).</p>'
            )
        ),

        build_multichoice_question(
            name="Ćw5 Zad. dom. – Wpływ zbliżenia temperatur",
            question_html=(
                '<p>Zwiększenie temperatury wylotowej wody zbliża ją '
                'do temperatury spalin. Jaki jest efekt na generację '
                'entropii?</p>'
            ),
            answers=[
                ("Generacja entropii maleje — zbliżenie temperatur czynników zmniejsza nieodwracalność wymiany ciepła.", 100),
                ("Generacja entropii rośnie.", 0),
                ("Generacja entropii nie zmienia się.", 0),
                ("Nie można tego określić bez znajomości geometrii.", 0),
            ],
            defaultgrade=1
        ),

        build_essay_question(
            name="Ćw5 Zad. dom. – Wnioski z optymalizacji wymiennika",
            question_html=(
                '<p>Na podstawie obliczeń odpowiedz na pytania:</p>'
                '<ol>'
                '<li>Czy zbliżenie temperatur czynników zmniejsza generację entropii?</li>'
                '<li>Jaki jest praktyczny kompromis między zmniejszaniem ΔT a wielkością wymiennika?</li>'
                '<li>Czy istnieje teoretyczna granica, przy której generacja entropii wynosi zero?</li>'
                '</ol>'
            ),
            defaultgrade=3,
            graderinfo_html=(
                '<p>1. Tak. 2. Mała ΔT = duży wymiennik (koszt). 3. Tak, ale wymaga nieskończonej powierzchni.</p>'
            )
        ),
    ]

    write_quiz("cw05_praca_domowa.xml", questions)


def generate_cw06(global_data):
    """Ćw. 6 — Rzeczywisty obieg chłodniczy"""
    var_map = {
        "t0": "cw06_t_parowania", # Specific
        "dTsh": "dTsh",
        "tk": "tk",
        "dTsc": "dTsc",
    }

    questions = [
        build_category("$course$/Ćw. 6 – Rzeczywisty obieg chłodniczy (Praca domowa)"),

        # wynik może wynosić 0 °C (t0 = -5, dTsh = 5) – tolerancja nominalna 0,1
        build_calculated_question(
            name="Ćw6 Zad. dom. – Temperatura ssania po przegrzaniu [°C]",
            question_html=(
                '<p>W obiegu chłodniczym z czynnikiem R134a '
                'temperatura parowania wynosi '
                '\\( t_0 = \\) <b>{t0}</b>°C. '
                'Stosujemy przegrzanie par na ssaniu sprężarki '
                'o \\( \\Delta T_{{sh}} = \\) <b>{dTsh}</b> K.</p>'
                '<p>Jaka jest temperatura czynnika na ssaniu sprężarki '
                '\\( t_1 \\) w <strong>°C</strong>?</p>'
                '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>'
            ),
            formula="{t0} + {dTsh}",
            tolerance=0.1, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw6 Zad. dom. – Temperatura cieczy po dochłodzeniu [°C]",
            question_html=(
                '<p>Temperatura skraplania czynnika R134a wynosi '
                '\\( t_k = \\) <b>{tk}</b>°C. '
                'Stosujemy dochłodzenie cieczy '
                'o \\( \\Delta T_{{sc}} = \\) <b>{dTsc}</b> K.</p>'
                '<p>Jaka jest temperatura czynnika przed dławieniem '
                '\\( t_3 \\) w <strong>°C</strong>?</p>'
                '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>'
            ),
            formula="{tk} - {dTsc}",
            tolerance=0.1, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_multichoice_question(
            name="Ćw6 Zad. dom. – Wpływ dochłodzenia na wydajność chłodniczą",
            question_html=(
                '<p>Dochłodzenie cieczy przed dławieniem powoduje, '
                'że entalpia czynnika przed zaworem rozprężnym jest '
                '<strong>niższa</strong>. Jaki jest efekt na wydajność '
                'chłodniczą \\( q_0 \\)?</p>'
            ),
            answers=[
                ("Wydajność chłodnicza \\( q_0 \\) rośnie, bo entalpia przed dławieniem jest niższa.", 100),
                ("Wydajność chłodnicza maleje, bo dochłodzenie wymaga dodatkowej energii.", 0),
                ("Wydajność chłodnicza nie zmienia się.", 0),
                ("Wpływ zależy od rodzaju czynnika chłodniczego.", 0),
            ],
            defaultgrade=2
        ),

        build_multichoice_question(
            name="Ćw6 Zad. dom. – Wpływ przegrzania na pracę sprężarki",
            question_html=(
                '<p>Przegrzanie par na ssaniu sprężarki powoduje, '
                'że punkt 1 na wykresie p-h przesuwa się w prawo '
                '(wyższa entalpia na ssaniu). Jaki jest efekt na pracę '
                'sprężarki \\( l_k \\)?</p>'
            ),
            answers=[
                ("Praca sprężarki \\( l_k \\) nieznacznie rośnie – w obszarze pary przegrzanej "
                 "izentropy na wykresie p-h „rozchylają się”, więc przy tym samym sprężu "
                 "przyrost entalpii \\( h_2 - h_1 \\) jest większy.", 100),
                ("Praca sprężarki maleje.", 0),
                ("Praca sprężarki nie zmienia się.", 0),
                ("Przegrzanie wpływa tylko na temperaturę.", 0),
            ],
            defaultgrade=2
        ),

        build_essay_question(
            name="Ćw6 Zad. dom. – Nowy EER z przegrzaniem i dochłodzeniem",
            question_html=(
                '<p>Narysuj na wykresie log p–h obieg chłodniczy '
                'R134a z przegrzaniem i dochłodzeniem.</p>'
                '<p>Na podstawie odczytanych entalpii oblicz:</p>'
                '<ol>'
                '<li>Nowy efekt chłodniczy \\( q_0 = h_1 - h_4 \\) [kJ/kg]</li>'
                '<li>Nową pracę sprężarki \\( l_k = h_2 - h_1 \\) [kJ/kg]</li>'
                '<li>Nowy wskaźnik EER = \\( q_0 / l_k \\)</li>'
                '</ol>'
                '<p>Porównaj z wartością EER z ćwiczeń.</p>'
            ),
            defaultgrade=5,
            graderinfo_html=(
                '<p>Przegrzanie zwiększa nieco i q_0, i l_k (dla R134a EER praktycznie '
                'bez zmian – chodzi o ochronę sprężarki), dochłodzenie zwiększa q_0 bez '
                'zmiany l_k. Bilans netto: EER rośnie o kilka procent. Orientacyjnie '
                '(CoolProp, t_0 = 2 °C, t_k = 40 °C, ΔT_sh = ΔT_sc = 5 K): h_1 ≈ 404, '
                'h_2 ≈ 429, h_3 = h_4 ≈ 249 kJ/kg, q_0 ≈ 155 kJ/kg, l_k ≈ 25 kJ/kg, '
                'EER ≈ 6,2 wobec ≈ 5,8–5,9 dla obiegu bez przegrzania i dochłodzenia '
                '(odczyt z wykresu może różnić się o kilka kJ/kg).</p>'
            )
        ),
    ]

    write_quiz("cw06_praca_domowa.xml", questions)


def generate_cw07(global_data):
    """Ćw. 7 — Odzysk ciepła w centrali wentylacyjnej"""
    var_map = {
        "eta_rek": "eta_rek",
        "t_cz": "t_cz",
        "t_wy": "t_wy",
        "Vdot_air": "Vdot_air",
        "h_sezon": "h_sezon",
        "cena_gaz": "cena_gaz",
        "eta_kotla": "eta_kotla", # Shared
        "koszt_rek": "koszt_rek",
    }
    # Q3–Q5: roczna oszczędność liczona dla ŚREDNIEJ temperatury zewnętrznej
    # w sezonie t_sr (Zad. 7.9 cd.), nie dla temperatury obliczeniowej t_cz
    var_map_sezon = dict(var_map, t_sr="t_sr")

    rho_cp = ('(\\( \\rho = 1{{,}}2 \\text{{ kg/m}}^3 \\), '
              '\\( c_p = 1{{,}}005 \\text{{ kJ/(kg·K)}} \\))')
    dane = ('rekuperator o sprawności \\( \\eta = \\) <b>{eta_rek}</b>%, '
            'strumień \\( \\dot{{V}} = \\) <b>{Vdot_air}</b> m³/h ' + rho_cp + ', '
            '\\( t_{{wy}} = \\) <b>{t_wy}</b>°C, średnia temperatura zewnętrzna '
            'w sezonie \\( t_{{śr}} = \\) <b>{t_sr}</b>°C, sezon <b>{h_sezon}</b> h/rok')

    questions = [
        build_category("$course$/Ćw. 7 – Odzysk ciepła w centrali wentylacyjnej (Praca domowa)"),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Temperatura za rekuperatorem [°C]",
            question_html=(
                '<p>Rekuperator krzyżowy o sprawności '
                '\\( \\eta = \\) <b>{eta_rek}</b>% '
                'podgrzewa powietrze czerpane z '
                '\\( t_{{cz}} = \\) <b>{t_cz}</b>°C ciepłem powietrza '
                'wyrzucanego z hali (\\( t_{{wy}} = \\) <b>{t_wy}</b>°C).</p>'
                '<p>Temperatura powietrza za rekuperatorem:</p>'
                '<p>\\( t_{{za}} = t_{{cz}} + \\eta \\cdot (t_{{wy}} - t_{{cz}}) \\)</p>'
                '<p>Oblicz \\( t_{{za}} \\) w <strong>°C</strong>. '
                'Wynik zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula="{t_cz} + {eta_rek} / 100 * ({t_wy} - {t_cz})",
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Oszczędność mocy grzewczej [kW]",
            question_html=(
                '<p>Rekuperator o sprawności \\( \\eta = \\) <b>{eta_rek}</b>% '
                'podgrzewa powietrze czerpane z \\( t_{{cz}} = \\) <b>{t_cz}</b>°C '
                'ciepłem powietrza wyrzucanego z hali (\\( t_{{wy}} = \\) <b>{t_wy}</b>°C); '
                '\\( \\Delta T_{{osz}} = t_{{za}} - t_{{cz}} = \\eta \\cdot (t_{{wy}} - t_{{cz}}) \\).</p>'
                '<p>Strumień powietrza: '
                '\\( \\dot{{V}} = \\) <b>{Vdot_air}</b> m³/h, '
                '\\( \\rho = 1{{,}}2 \\text{{ kg/m}}^3 \\), '
                '\\( c_p = 1{{,}}005 \\text{{ kJ/(kg·K)}} \\).</p>'
                '<p>Oblicz oszczędność mocy grzewczej '
                '\\( \\dot{{Q}}_{{osz}} \\) w <strong>kW</strong> (warunki obliczeniowe). '
                'Zaokrąglij do 1 miejsca po przecinku.</p>'
                '<p>\\( \\dot{{Q}}_{{osz}} = \\dot{{m}} \\cdot c_p \\cdot '
                '\\Delta T_{{osz}} \\)</p>'
            ),
            formula=(
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_cz})"
            ),
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Roczna oszczędność energii [MWh]",
            question_html=(
                '<p>Rekuperator o sprawności \\( \\eta = \\) <b>{eta_rek}</b>% '
                'pracuje w centrali o strumieniu \\( \\dot{{V}} = \\) <b>{Vdot_air}</b> m³/h '
                + rho_cp + '; powietrze wyrzucane z hali ma \\( t_{{wy}} = \\) <b>{t_wy}</b>°C. '
                'Sezon grzewczy trwa <b>{h_sezon}</b> h/rok, a <strong>średnia</strong> '
                'temperatura zewnętrzna w sezonie wynosi \\( t_{{śr}} = \\) <b>{t_sr}</b>°C '
                '(temperatura obliczeniowa \\( t_{{cz}} \\) występuje tylko przez kilka dni '
                'w roku – jak w Zad. 7.9 cd.).</p>'
                '<p>Oblicz roczną oszczędność energii cieplnej w <strong>MWh</strong> '
                'dla średniej mocy odzyskiwanej w sezonie: '
                '\\( \\Delta\\dot{{Q}}_{{śr}} = \\dot{{m}} \\cdot c_p \\cdot \\eta \\cdot '
                '(t_{{wy}} - t_{{śr}}) \\). Zaokrąglij do 1 miejsca po przecinku.</p>'
            ),
            formula=(
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_sr}) * "
                "{h_sezon} / 1000"
            ),
            variables_map=var_map_sezon, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Roczna oszczędność gazu [PLN]",
            question_html=(
                '<p>Roczna oszczędność energii: ' + dane + '. '
                'Ciepło dostarcza kocioł gazowy o sprawności '
                '\\( \\eta_k = \\) <b>{eta_kotla}</b>%. '
                'Cena gazu: <b>{cena_gaz}</b> PLN/kWh (energii chemicznej paliwa).</p>'
                '<p>Oblicz roczną oszczędność finansową '
                'w <strong>PLN</strong>. Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>'
            ),
            formula=(
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_sr}) * "
                "{h_sezon} / ({eta_kotla} / 100) * {cena_gaz}"
            ),
            variables_map=var_map_sezon, global_data=global_data, defaultgrade=2,
            correct_answer_length=2
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Czas zwrotu inwestycji SPBT [lata]",
            question_html=(
                '<p>Koszt rekuperatora: <b>{koszt_rek}</b> PLN. '
                'Roczna oszczędność finansowa: ' + dane + ', '
                'sprawność kotła \\( \\eta_k = \\) <b>{eta_kotla}</b>%, '
                'cena gazu <b>{cena_gaz}</b> PLN/kWh.</p>'
                '<p>Oblicz prosty czas zwrotu inwestycji SPBT '
                'w <strong>latach</strong>.</p>'
                '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>'
            ),
            formula=(
                "{koszt_rek} / ("
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_sr}) * "
                "{h_sezon} / ({eta_kotla} / 100) * {cena_gaz})"
            ),
            variables_map=var_map_sezon, global_data=global_data, defaultgrade=1,
            correct_answer_length=2
        ),

        build_multichoice_question(
            name="Ćw7 Zad. dom. – Opłacalność rekuperatora",
            question_html=(
                '<p>Na podstawie obliczonego SPBT, '
                'która interpretacja jest prawidłowa?</p>'
            ),
            answers=[
                ("Inwestycja w rekuperator jest opłacalna – okres zwrotu jest krótki "
                 "w porównaniu z trwałością urządzenia (15–20 lat).", 100),
                ("Rekuperator nie jest opłacalny.", 0),
                ("Tak krótki SPBT (poniżej kilku lat) sugeruje błąd w obliczeniach.", 0),
                ("Rekuperator jest niepotrzebny.", 0),
            ],
            defaultgrade=1
        ),
    ]

    write_quiz("cw07_praca_domowa.xml", questions)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    print("Generowanie quizów domowych z GLOBALNYMI zmiennymi (v2)...")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. Generate master dataset
    global_data = generate_global_data()
    print(f"Wygenerowano macierz danych dla {len(global_data)} zmiennych.")

    # 2. Generate quizzes using this master data
    generate_cw01(global_data)
    generate_cw02(global_data)
    generate_cw03(global_data)
    generate_cw04(global_data)
    generate_cw05(global_data)
    generate_cw06(global_data)
    generate_cw07(global_data)

    print(f"\nGotowe! Wygenerowano 7 plików w {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
