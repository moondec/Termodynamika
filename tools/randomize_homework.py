#!/usr/bin/env python3
"""
Generate Moodle-compatible 'calculated' homework quizzes (cw01–cw07)
with randomized variable pools.

Each numerical question is converted from static 'numerical' type to
a Moodle 'calculated' type with {variable} placeholders and
pre-generated dataset items.

This version uses a GLOBAL DATASET MATRIX so that all quizzes share
the same random values for shared variables (e.g. tw_in).

Usage:
    python tools/randomize_homework.py
"""

import random
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

random.seed(2025)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "Cwiczenia", "homework")

N_ITEMS = 50  # number of pre-generated dataset values


# ─────────────────────────────────────────────
# 1. Global Configuration (Schema)
# ─────────────────────────────────────────────

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
    "r_w":              {"min": 2400, "max": 2550, "dec": 0},
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
        data[key] = {
            "items": gen_items(conf["min"], conf["max"], conf["dec"]),
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
    name, question_html, formula, tolerance, tolerance_type,
    variables_map, global_data, defaultgrade, penalty="0.1000000",
    general_feedback_html=None, correct_answer_format=1,
    correct_answer_length=4
):
    """Build a full <question type='calculated'> element.
    
    variables_map: dict mapping local XML placeholder name -> global data key
                   e.g. {"t1": "cw01_t_otoczenia"}
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
        "V": "cw01_V",
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
                '<![CDATA[<p>Zbiornik o objętości \\( V = \\) <b>{V}</b> m³ '
                'zawiera powietrze przy ciśnieniu atmosferycznym '
                '\\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg '
                'i temperaturze \\( t = \\) <b>{t1}</b>°C.</p>'
                '<p>Oblicz masę powietrza w zbiorniku. '
                'Przyjmij \\( R = 287 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Wynik podaj w <strong>kg</strong> '
                '(zaokrąglij do 1 miejsca po przecinku).</p>'
                '<p><em>Wskazówka:</em> \\( pV = mRT \\)</p>]]>'
            ),
            formula="({patm_mmHg} * 133.322) * {V} / (287 * ({t1} + 273.15))",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Masa powietrza w zbiorniku pełnym [kg]",
            question_html=(
                '<![CDATA[<p>Zbiornik o objętości \\( V = \\) <b>{V}</b> m³ '
                'został naładowany sprężonym powietrzem do ciśnienia '
                '\\( p = \\) <b>{p_full}</b> bar (abs) '
                'i temperatury \\( t = \\) <b>{t_full}</b>°C.</p>'
                '<p>Oblicz masę powietrza w zbiorniku. '
                'Przyjmij \\( R = 287 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Wynik podaj w <strong>kg</strong> '
                '(zaokrąglij do 1 miejsca po przecinku).</p>]]>'
            ),
            formula="{p_full} * 100000 * {V} / (287 * ({t_full} + 273.15))",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Wydajność masowa sprężarki [kg/h]",
            question_html=(
                '<![CDATA[<p>Zbiornik o objętości \\( V = \\) <b>{V}</b> m³ '
                'musi być napompowany od ciśnienia atmosferycznego '
                '(\\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg, '
                '\\( t = \\) <b>{t1}</b>°C) '
                'do ciśnienia roboczego '
                '(\\( p = \\) <b>{p_full}</b> bar, '
                '\\( t = \\) <b>{t_full}</b>°C) '
                'w czasie 1 godziny.</p>'
                '<p>Oblicz wymaganą wydajność masową sprężarki '
                '\\( \\dot{{m}} \\) w <strong>kg/h</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>]]>'
            ),
            formula=(
                "{p_full} * 100000 * {V} / (287 * ({t_full} + 273.15)) "
                "- ({patm_mmHg} * 133.322) * {V} / (287 * ({t1} + 273.15))"
            ),
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw1 Zad. dom. – Wydajność objętościowa sprężarki [m³/h]",
            question_html=(
                '<![CDATA[<p>Sprężarka musi dostarczyć wydajność masową '
                'z poprzedniego zadania. '
                'Warunki ssania: \\( p_{{atm}} = \\) <b>{patm_mmHg}</b> mmHg, '
                '\\( T = \\) <b>{t1}</b>°C.</p>'
                '<p>Oblicz wymaganą wydajność objętościową sprężarki '
                'w warunkach ssania \\( \\dot{{V}} \\) w <strong>m³/h</strong>.</p>'
                '<p>Wynik zaokrąglij do całości.</p>]]>'
            ),
            formula=(
                "({p_full} * 100000 * {V} / (287 * ({t_full} + 273.15)) "
                "- ({patm_mmHg} * 133.322) * {V} / (287 * ({t1} + 273.15))) "
                "* 287 * ({t1} + 273.15) / ({patm_mmHg} * 133.322)"
            ),
            tolerance=3, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_multichoice_question(
            name="Ćw1 Zad. dom. – Dlaczego temperatura rośnie?",
            question_html=(
                '<![CDATA[<p>Dlaczego w zbiorniku po napełnieniu sprężonym '
                'powietrzem temperatura wzrosła?</p>]]>'
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

        build_calculated_question(
            name="Ćw2 Zad. dom. – Strumień wody [kg/s]",
            question_html=(
                '<![CDATA[<p>Z chłodnicy sprężarki odzyskujemy '
                '<b>{eta_odz}</b>% ciepła, tj. '
                '\\( \\dot{{Q}}_{{odz}} = \\) '
                '<b>{eta_odz}</b>/100 × <b>{Qch}</b> kW.</p>'
                '<p>Chcemy podgrzać wodę z <b>{tw_in}</b>°C '
                'do <b>{tw_out}</b>°C. '
                'Ciepło właściwe wody: \\( c_w = 4190 \\text{{ J/(kg·K)}} \\).</p>'
                '<p>Oblicz wymagany strumień masy wody '
                '\\( \\dot{{m}}_w \\) w <strong>kg/s</strong>.</p>'
                '<p><em>Wzór:</em> \\( \\dot{{Q}} = \\dot{{m}}_w \\cdot c_w \\cdot \\Delta T \\)</p>'
                '<p>Wynik podaj z dokładnością do 4 miejsc po przecinku.</p>]]>'
            ),
            formula="{Qch} * {eta_odz} / 100 * 1000 / (4190 * ({tw_out} - {tw_in}))",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2,
            correct_answer_length=4
        ),

        build_calculated_question(
            name="Ćw2 Zad. dom. – Strumień wody [l/min]",
            question_html=(
                '<![CDATA[<p>Z chłodnicy sprężarki można odzyskać ciepło. '
                'Woda ma być podgrzana z <b>{tw_in}</b>°C '
                'do <b>{tw_out}</b>°C.</p>'
                '<p>\\( c_w = 4190 \\text{{ J/(kg·K)}} \\), '
                '\\( \\rho_w = 1000 \\text{{ kg/m}}^3 \\).</p>'
                '<p>Ciepło do dyspozycji: '
                '\\( \\dot{{Q}}_{{odz}} = \\) <b>{Qch}</b> × <b>{eta_odz}</b>/100 kW.</p>'
                '<p>Oblicz strumień objętościowy wody w <strong>l/min</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>]]>'
            ),
            formula="{Qch} * {eta_odz} / 100 * 1000 / (4190 * ({tw_out} - {tw_in})) * 60 * 1000",
            tolerance=3, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_multichoice_question(
            name="Ćw2 Zad. dom. – Interpretacja wyniku",
            question_html=(
                '<![CDATA[<p>Obliczono strumień wody wynikający z odzysku ciepła '
                'ze sprężarki. Która z poniższych interpretacji jest poprawna?</p>]]>'
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
                '<![CDATA[<p>Wykonaj pełny bilans energetyczny sprężarkowni '
                'z odzyskiem ciepła. Uwzględnij:</p>'
                '<ul>'
                '<li>Moc dostarczoną do sprężarki (silnik elektryczny)</li>'
                '<li>Ciepło odprowadzone w chłodnicy</li>'
                '<li>Ciepło odzyskane</li>'
                '<li>Ciepło tracone do otoczenia</li>'
                '</ul>'
                '<p>Narysuj schemat bilansowy i określ, jaka część energii '
                'jest „stracona".</p>]]>'
            ),
            defaultgrade=3,
            graderinfo_html=(
                '<![CDATA[<p>Sprawdź: bilans musi się zgadzać. Ciepło odzyskane = Qch × eta_odz/100.</p>]]>'
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
                '<![CDATA[<p>Kocioł zużywa \\( V_{{gaz}} = \\) <b>{Vgas}</b> m³/h '
                'gazu ziemnego. Przy spalaniu 1 m³ gazu powstaje ok. '
                '<b>{kgH2O}</b> kg wody w spalinach.</p>'
                '<p>Oblicz masowy strumień pary wodnej w spalinach '
                'w <strong>kg/h</strong>.</p>'
                '<p>Wynik zaokrąglij do całości.</p>]]>'
            ),
            formula="{Vgas} * {kgH2O}",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw3 Zad. dom. – Dodatkowe ciepło z kondensacji [kW]",
            question_html=(
                '<![CDATA[<p>W spalinach kotła powstaje '
                '\\( \\dot{{m}}_w = \\) <b>{Vgas}</b> × <b>{kgH2O}</b> kg/h '
                'pary wodnej. Ciepło parowania wody wynosi '
                '\\( r = \\) <b>{r_w}</b> kJ/kg.</p>'
                '<p>Oblicz dodatkowy strumień ciepła '
                '\\( \\dot{{Q}}_{{kond}} \\), który można odzyskać '
                'skraplając <strong>całą</strong> parę wodną ze spalin.</p>'
                '<p>Wynik podaj w <strong>kW</strong>. '
                'Zaokrąglij do całości.</p>]]>'
            ),
            formula="{Vgas} * {kgH2O} * {r_w} / 3600",
            tolerance=3, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_calculated_question(
            name="Ćw3 Zad. dom. – Wzrost sprawności [punkty procentowe]",
            question_html=(
                '<![CDATA[<p>Kocioł ma sprawność \\( \\eta = \\) <b>{eta_kotla}</b>% '
                'i moc cieplną \\( \\dot{{Q}}_{{uż}} = \\) <b>{Quz}</b> kW. '
                'Dodatkowy odzysk ciepła z kondensacji wynosi '
                '\\( \\dot{{Q}}_{{kond}} \\) (obliczone w poprzednim pytaniu).</p>'
                '<p>O ile <strong>punktów procentowych</strong> wzrośnie '
                'sprawność kotłowni po zainstalowaniu kondensacji spalin?</p>'
                '<p>\\( \\Delta\\eta = '
                '\\frac{{\\dot{{Q}}_{{kond}}}}{{\\dot{{Q}}_{{paliwa}}}} '
                '\\cdot 100\\% \\), gdzie '
                '\\( \\dot{{Q}}_{{paliwa}} = '
                '\\frac{{\\dot{{Q}}_{{uż}}}}{{\\eta}} \\)</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>]]>'
            ),
            formula=(
                "({Vgas} * {kgH2O} * {r_w} / 3600) / "
                "({Quz} / ({eta_kotla} / 100)) * 100"
            ),
            tolerance=5, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_multichoice_question(
            name="Ćw3 Zad. dom. – Temperatura punktu rosy spalin",
            question_html=(
                '<![CDATA[<p>Aby kocioł kondensacyjny mógł odzyskiwać ciepło '
                'skraplania, temperatura spalin musi spaść poniżej pewnej '
                'wartości. Jak nazywa się ta temperatura?</p>]]>'
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
                '<![CDATA[<p>Wyjaśnij, dlaczego w praktyce nie zawsze udaje '
                'się odzyskać 100% ciepła kondensacji ze spalin.</p>]]>'
            ),
            defaultgrade=2,
            graderinfo_html=(
                '<![CDATA[<p>Oczekiwane odpowiedzi: Niska tw powrotu, korozyjność.</p>]]>'
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

    questions = [
        build_category("$course$/Ćw. 4 – Opłacalność kogeneracji (Praca domowa)"),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Moc elektryczna generatora [kW]",
            question_html=(
                '<![CDATA[<p>Turbina parowa o mocy teoretycznej '
                '\\( N_t = \\) <b>{Nt}</b> kW napędza generator '
                'o sprawności \\( \\eta_{{gen}} = \\) <b>{eta_gen}</b>%.</p>'
                '<p>Oblicz rzeczywistą moc elektryczną \\( N_{{el}} \\) '
                'w <strong>kW</strong>.</p>'
                '<p>Wynik zaokrąglij do 1 miejsca po przecinku.</p>]]>'
            ),
            formula="{Nt} * {eta_gen} / 100",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Roczna produkcja energii [MWh]",
            question_html=(
                '<![CDATA[<p>Generator o mocy '
                '\\( N_{{el}} = \\) <b>{Nt}</b> × <b>{eta_gen}</b>/100 kW '
                'pracuje <b>{h_rok}</b> h/rok.</p>'
                '<p>Oblicz roczną produkcję energii elektrycznej '
                'w <strong>MWh/rok</strong>.</p>'
                '<p>Wynik zaokrąglij do całości.</p>]]>'
            ),
            formula="{Nt} * {eta_gen} / 100 * {h_rok} / 1000",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Roczny zysk [PLN]",
            question_html=(
                '<![CDATA[<p>Roczna produkcja energii wynika z mocy generatora '
                'i czasu pracy. Cena prądu: <b>{cena_kWh}</b> PLN/kWh.</p>'
                '<p>Oblicz roczny zysk (oszczędność) w <strong>PLN</strong>.</p>'
                '<p>Wynik zaokrąglij do tysięcy.</p>]]>'
            ),
            formula="{Nt} * {eta_gen} / 100 * {h_rok} * {cena_kWh}",
            tolerance=3, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw4 Zad. dom. – Czas zwrotu inwestycji SPBT [lata]",
            question_html=(
                '<![CDATA[<p>Koszt instalacji turbiny: <b>{koszt_inv}</b> PLN. '
                'Roczny zysk wynika z produkcji energii i ceny prądu.</p>'
                '<p>Oblicz prosty czas zwrotu inwestycji SPBT w <strong>latach</strong>.</p>'
                '<p>\\( SPBT = \\frac{{\\text{{Koszt inwestycji}}}}'
                '{{\\text{{Roczny zysk}}}} \\)</p>'
                '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>]]>'
            ),
            formula="{koszt_inv} / ({Nt} * {eta_gen} / 100 * {h_rok} * {cena_kWh})",
            tolerance=5, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2,
            correct_answer_length=2
        ),

        build_multichoice_question(
            name="Ćw4 Zad. dom. – Czy inwestycja się opłaca?",
            question_html=(
                '<![CDATA[<p>Na podstawie obliczeń SPBT, '
                'która z poniższych interpretacji jest NAJLEPSZA?</p>]]>'
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
                '<![CDATA[<p>Wymiennik ciepła spaliny–woda ma moc '
                '\\( \\dot{{Q}} = \\) <b>{Qwym}</b> kW. '
                'Temperatura wylotowa wody: <b>{tw_out_new}</b>°C, '
                'wlotowa: <b>{tw_in}</b>°C.</p>'
                '<p>Ciepło właściwe wody: '
                '\\( c_w = 4{{,}}19 \\text{{ kJ/(kg·K)}} \\).</p>'
                '<p>Oblicz strumień masy wody '
                '\\( \\dot{{m}}_w \\) w <strong>kg/s</strong>.</p>'
                '<p>\\( \\dot{{Q}} = \\dot{{m}}_w \\cdot c_w '
                '\\cdot (T_{{wyj}} - T_{{wej}}) \\)</p>'
                '<p>Wynik podaj z dokładnością do 2 miejsc po przecinku.</p>]]>'
            ),
            formula="{Qwym} / (4.19 * ({tw_out_new} - {tw_in}))",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2,
            correct_answer_length=4
        ),

        build_calculated_question(
            name="Ćw5 Zad. dom. – Generacja entropii [kW/K]",
            question_html=(
                '<![CDATA[<p>Wymiennik ciepła: spaliny chłodzą się '
                'z \\( T_{{sp,wej}} = \\) <b>{Tsp_in}</b> K '
                'do \\( T_{{sp,wyj}} = \\) <b>{Tsp_out}</b> K, '
                'woda grzeje się z \\( T_{{w,wej}} = \\) <b>{tw_in}</b>°C '
                'do \\( T_{{w,wyj}} = \\) <b>{tw_out_new}</b>°C.</p>'
                '<p>Strumień ciepła: \\( \\dot{{Q}} = \\) <b>{Qwym}</b> kW.</p>'
                '<p>Generacja entropii (średnia arytmetyczna):</p>'
                '<p>\\( \\dot{{S}}_{{gen}} = \\dot{{Q}} \\cdot '
                '\\left( \\frac{{1}}{{T_{{w,śr}}}} - '
                '\\frac{{1}}{{T_{{sp,śr}}}} \\right) \\)</p>'
                '<p>Wynik w <strong>kW/K</strong> z dokładnością '
                'do 3 miejsc po przecinku.</p>]]>'
            ),
            formula=(
                "{Qwym} * (1 / (({tw_in} + 273.15 + {tw_out_new} + 273.15) / 2) "
                "- 1 / (({Tsp_in} + {Tsp_out}) / 2))"
            ),
            tolerance=5, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=3,
            correct_answer_length=4
        ),

        build_multichoice_question(
            name="Ćw5 Zad. dom. – Wpływ zbliżenia temperatur",
            question_html=(
                '<![CDATA[<p>Zwiększenie temperatury wylotowej wody zbliża ją '
                'do temperatury spalin. Jaki jest efekt na generację '
                'entropii?</p>]]>'
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
                '<![CDATA[<p>Na podstawie obliczeń odpowiedz na pytania:</p>'
                '<ol>'
                '<li>Czy zbliżenie temperatur czynników zmniejsza generację entropii?</li>'
                '<li>Jaki jest praktyczny kompromis między zmniejszaniem ΔT a wielkością wymiennika?</li>'
                '<li>Czy istnieje teoretyczna granica, przy której generacja entropii wynosi zero?</li>'
                '</ol>]]>'
            ),
            defaultgrade=3,
            graderinfo_html=(
                '<![CDATA[<p>1. Tak. 2. Mała ΔT = duży wymiennik (koszt). 3. Tak, ale wymaga nieskończonej powierzchni.</p>]]>'
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

        build_calculated_question(
            name="Ćw6 Zad. dom. – Temperatura ssania po przegrzaniu [°C]",
            question_html=(
                '<![CDATA[<p>W obiegu chłodniczym z czynnikiem R134a '
                'temperatura parowania wynosi '
                '\\( t_0 = \\) <b>{t0}</b>°C. '
                'Stosujemy przegrzanie par na ssaniu sprężarki '
                'o \\( \\Delta T_{{sh}} = \\) <b>{dTsh}</b> K.</p>'
                '<p>Jaka jest temperatura czynnika na ssaniu sprężarki '
                '\\( t_1 \\) w <strong>°C</strong>?</p>]]>'
            ),
            formula="{t0} + {dTsh}",
            tolerance=0.1, tolerance_type=1,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw6 Zad. dom. – Temperatura cieczy po dochłodzeniu [°C]",
            question_html=(
                '<![CDATA[<p>Temperatura skraplania czynnika R134a wynosi '
                '\\( t_k = \\) <b>{tk}</b>°C. '
                'Stosujemy dochłodzenie cieczy '
                'o \\( \\Delta T_{{sc}} = \\) <b>{dTsc}</b> K.</p>'
                '<p>Jaka jest temperatura czynnika przed dławieniem '
                '\\( t_3 \\) w <strong>°C</strong>?</p>]]>'
            ),
            formula="{tk} - {dTsc}",
            tolerance=0.1, tolerance_type=1,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_multichoice_question(
            name="Ćw6 Zad. dom. – Wpływ dochłodzenia na wydajność chłodniczą",
            question_html=(
                '<![CDATA[<p>Dochłodzenie cieczy przed dławieniem powoduje, '
                'że entalpia czynnika przed zaworem rozprężnym jest '
                '<strong>niższa</strong>. Jaki jest efekt na wydajność '
                'chłodniczą \\( q_0 \\)?</p>]]>'
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
                '<![CDATA[<p>Przegrzanie par na ssaniu sprężarki powoduje, '
                'że punkt 1 na wykresie p-h przesuwa się w prawo '
                '(wyższa entalpia na ssaniu). Jaki jest efekt na pracę '
                'sprężarki \\( l_k \\)?</p>]]>'
            ),
            answers=[
                ("Praca sprężarki \\( l_k \\) rośnie, bo sprężamy z wyższej entalpii.", 100),
                ("Praca sprężarki maleje.", 0),
                ("Praca sprężarki nie zmienia się.", 0),
                ("Przegrzanie wpływa tylko na temperaturę.", 0),
            ],
            defaultgrade=2
        ),

        build_essay_question(
            name="Ćw6 Zad. dom. – Nowy EER z przegrzaniem i dochłodzeniem",
            question_html=(
                '<![CDATA[<p>Narysuj na wykresie log p–h obieg chłodniczy '
                'R134a z przegrzaniem i dochłodzeniem.</p>'
                '<p>Na podstawie odczytanych entalpii oblicz:</p>'
                '<ol>'
                '<li>Nowy efekt chłodniczy \\( q_0 = h_1 - h_4 \\) [kJ/kg]</li>'
                '<li>Nową pracę sprężarki \\( l_k = h_2 - h_1 \\) [kJ/kg]</li>'
                '<li>Nowy wskaźnik EER = \\( q_0 / l_k \\)</li>'
                '</ol>'
                '<p>Porównaj z wartością EER z ćwiczeń.</p>]]>'
            ),
            defaultgrade=5,
            graderinfo_html=(
                '<![CDATA[<p>Przegrzanie zwiększa l_k, dochłodzenie zwiększa q_0. Bilans netto: EER rośnie nieznacznie.</p>]]>'
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

    questions = [
        build_category("$course$/Ćw. 7 – Odzysk ciepła w centrali wentylacyjnej (Praca domowa)"),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Temperatura za rekuperatorem [°C]",
            question_html=(
                '<![CDATA[<p>Rekuperator krzyżowy o sprawności '
                '\\( \\eta = \\) <b>{eta_rek}</b>% '
                'podgrzewa powietrze czerpane z '
                '\\( t_{{cz}} = \\) <b>{t_cz}</b>°C ciepłem powietrza '
                'wyrzucanego z hali (\\( t_{{wy}} = \\) <b>{t_wy}</b>°C).</p>'
                '<p>Temperatura powietrza za rekuperatorem:</p>'
                '<p>\\( t_{{za}} = t_{{cz}} + \\eta \\cdot (t_{{wy}} - t_{{cz}}) \\)</p>'
                '<p>Oblicz \\( t_{{za}} \\) w <strong>°C</strong>. '
                'Wynik zaokrąglij do całości.</p>]]>'
            ),
            formula="{t_cz} + {eta_rek} / 100 * ({t_wy} - {t_cz})",
            tolerance=2, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Oszczędność mocy grzewczej [kW]",
            question_html=(
                '<![CDATA[<p>Rekuperator podgrzewa powietrze z '
                '<b>{t_cz}</b>°C. Temperatura za rekuperatorem wynika '
                'ze sprawności <b>{eta_rek}</b>%.</p>'
                '<p>Strumień powietrza: '
                '\\( \\dot{{V}} = \\) <b>{Vdot_air}</b> m³/h, '
                '\\( \\rho = 1{{,}}2 \\text{{ kg/m}}^3 \\), '
                '\\( c_p = 1{{,}}005 \\text{{ kJ/(kg·K)}} \\).</p>'
                '<p>Oblicz oszczędność mocy grzewczej '
                '\\( \\dot{{Q}}_{{osz}} \\) w <strong>kW</strong>. '
                'Zaokrąglij do całości.</p>'
                '<p>\\( \\dot{{Q}}_{{osz}} = \\dot{{m}} \\cdot c_p \\cdot '
                '\\Delta T_{{osz}} \\)</p>]]>'
            ),
            formula=(
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_cz})"
            ),
            tolerance=3, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=3
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Roczna oszczędność energii [MWh]",
            question_html=(
                '<![CDATA[<p>Oszczędność mocy grzewczej dzięki rekuperatorowi '
                'wynika z obliczeń. '
                'Sezon grzewczy trwa <b>{h_sezon}</b> h/rok.</p>'
                '<p>Oblicz roczną oszczędność energii cieplnej '
                'w <strong>MWh</strong>. Zaokrąglij do całości.</p>]]>'
            ),
            formula=(
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_cz}) * "
                "{h_sezon} / 1000"
            ),
            tolerance=3, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Roczna oszczędność gazu [PLN]",
            question_html=(
                '<![CDATA[<p>Roczna oszczędność energii wynika z obliczeń. '
                'Sprawność kotła gazowego: '
                '\\( \\eta_k = \\) <b>{eta_kotla}</b>%. '
                'Cena gazu: <b>{cena_gaz}</b> PLN/kWh.</p>'
                '<p>Oblicz roczną oszczędność finansową '
                'w <strong>PLN</strong>. Zaokrąglij do tysięcy.</p>]]>'
            ),
            formula=(
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_cz}) * "
                "{h_sezon} / ({eta_kotla} / 100) * {cena_gaz}"
            ),
            tolerance=5, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=2
        ),

        build_calculated_question(
            name="Ćw7 Zad. dom. – Czas zwrotu inwestycji SPBT [lata]",
            question_html=(
                '<![CDATA[<p>Koszt rekuperatora: <b>{koszt_rek}</b> PLN. '
                'Roczna oszczędność wynika z obliczeń.</p>'
                '<p>Oblicz prosty czas zwrotu inwestycji SPBT '
                'w <strong>latach</strong>.</p>'
                '<p>Wynik podaj z dokładnością do 1 miejsca po przecinku.</p>]]>'
            ),
            formula=(
                "{koszt_rek} / ("
                "{Vdot_air} / 3600 * 1.2 * 1.005 * "
                "{eta_rek} / 100 * ({t_wy} - {t_cz}) * "
                "{h_sezon} / ({eta_kotla} / 100) * {cena_gaz})"
            ),
            tolerance=5, tolerance_type=2,
            variables_map=var_map, global_data=global_data, defaultgrade=1,
            correct_answer_length=2
        ),

        build_multichoice_question(
            name="Ćw7 Zad. dom. – Opłacalność rekuperatora",
            question_html=(
                '<![CDATA[<p>Na podstawie obliczonego SPBT, '
                'która interpretacja jest prawidłowa?</p>]]>'
            ),
            answers=[
                ("Inwestycja w rekuperator jest bardzo opłacalna.", 100),
                ("Rekuperator nie jest opłacalny.", 0),
                ("SPBT < 1 roku sugeruje błąd w obliczeniach.", 0),
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
