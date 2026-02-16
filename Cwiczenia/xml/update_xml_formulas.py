#!/usr/bin/env python3
"""
update_xml_formulas.py
Update Moodle XML calculated question formulas with polynomial
approximations from CoolProp. Also add missing questions.
"""
import xml.etree.ElementTree as ET
import os, copy, re

XML_DIR = os.path.dirname(os.path.abspath(__file__))

# ============================================================
# POLYNOMIAL COEFFICIENTS (from fit_polynomials.py)
# ============================================================

# --- Water/Steam superheated h(p,T) [kJ/kg], p in bar, T in °C ---
# h = a0 + a1*T + a2*p + a3*T*p + a4*T² + a5*p²
# Max err: 1.91 kJ/kg (0.065%)  Range: p=8..16, T=Tsat+5..300
H_STEAM = "2401.59 + 2.7229*{tp} + (-11.4741)*{pk} + 0.032085*{tp}*{pk} + (-0.00163053)*pow({tp},2) + (-0.0237)*pow({pk},2)"

# --- Water/Steam superheated s(p,T) [kJ/(kgK)] ---
S_STEAM = "6.2457 + 0.007326*{tp} + (-0.101072)*{pk} + 0.00006159*{tp}*{pk} + (-0.0000073331)*pow({tp},2) + 0.001669*pow({pk},2)"

# --- Water saturated: Tsat(p) [°C], p in bar ---
TSAT = "0.037213*pow({pk},3) + (-1.3287)*pow({pk},2) + 19.1052*{pk} + 84.8568"

# --- Water saturated hf(p) [kJ/kg], p in bar, range 0.5..6 ---
HF_P = "2.1757*pow({pdl},3) + (-29.9971)*pow({pdl},2) + 169.0692*{pdl} + 269.2620"
HG_P = "0.9171*pow({pdl},3) + (-12.5552)*pow({pdl},2) + 65.5716*{pdl} + 2618.0251"
SF_P = "0.006322*pow({p2t},3) + (-0.0862)*pow({p2t},2) + 0.4632*{p2t} + 0.8984"
SG_P = "-0.007501*pow({p2t},3) + 0.1004*pow({p2t},2) + (-0.5079)*{p2t} + 7.8003"
HF_P2 = "2.1757*pow({p2t},3) + (-29.9971)*pow({p2t},2) + 169.0692*{p2t} + 269.2620"
HG_P2 = "0.9171*pow({p2t},3) + (-12.5552)*pow({p2t},2) + 65.5716*{p2t} + 2618.0251"

# --- Water s_water(T) sat liquid [kJ/(kgK)], T in °C ---
S_WATER = "-0.00001826*pow({tz},2) + 0.014766*{tz} + 0.0111"

# --- R134a ---
H1_R134A = "-0.002127*pow({to6},2) + 0.6041*{to6} + 398.5703"  # h_g(T) vapor
H3_R134A = "0.002042*pow({tk6},2) + 1.3296*{tk6} + 200.0224"   # h_f(T) liquid
H2S_R134A = "398.7923 + (-0.152673)*{to6} + 0.722686*{tk6} + (-0.00060308)*{to6}*{tk6} + 0.00212521*pow({to6},2) + (-0.00201033)*pow({tk6},2)"
V_R134A = "0.00005115*pow({to6},2) + (-0.002437)*{to6} + 0.069308"  # v_g(T)

# --- R290 (Propane) ---
H1_R290 = "-0.004186*pow({to6},2) + 1.1477*{to6} + 574.7918"
H3_R290 = "0.005311*pow({to6},2) + 2.4687*{to6} + 200.0520"  # uses to6 for evaporator T range mapping
H2S_R290 = "575.1506 + (-0.298900)*{to6} + 1.381165*{tk6} + (-0.00118242)*{to6}*{tk6} + 0.00392480*pow({to6},2) + (-0.00371714)*pow({tk6},2)"

# Watch: h3 for R290 should use tk6 (condenser temp) not to6
H3_R290_TK = "0.005311*pow({tk6},2) + 2.4687*{tk6} + 200.0520"


def update_answer(question, new_formula):
    """Update the answer formula text for a calculated question."""
    ans = question.find('.//answer/text')
    if ans is not None:
        ans.text = new_formula


def find_question(root, name_text):
    """Find question by name."""
    for q in root.findall('.//question'):
        n = q.find('name/text')
        if n is not None and n.text == name_text:
            return q
    return None


def get_dataset_def(question):
    """Get the first dataset_definitions element."""
    return question.find('.//dataset_definitions')


def copy_dataset_item(source_q, var_name, target_q):
    """Copy a shared variable's dataset_definition from source to target question."""
    src_defs = source_q.find('.//dataset_definitions')
    if src_defs is None:
        return
    for dd in src_defs.findall('dataset_definition'):
        status = dd.find('status')
        name = dd.find('name/text')
        if name is not None and name.text == var_name:
            tgt_defs = target_q.find('.//dataset_definitions')
            if tgt_defs is None:
                tgt_defs = ET.SubElement(target_q, 'dataset_definitions')
            tgt_defs.append(copy.deepcopy(dd))
            return


def make_calculated_question(name, questiontext, formula, tolerance, 
                              tolerancetype=1, correctanswerformat=1, 
                              correctanswerlength=2, vars_from=None):
    """Create a new calculated question element."""
    q = ET.Element('question', type='calculated')
    
    n = ET.SubElement(q, 'name')
    nt = ET.SubElement(n, 'text')
    nt.text = name
    
    qt = ET.SubElement(q, 'questiontext', format='html')
    qtt = ET.SubElement(qt, 'text')
    qtt.text = f'<![CDATA[<p>{questiontext}</p>]]>'
    
    gf = ET.SubElement(q, 'generalfeedback', format='html')
    gft = ET.SubElement(gf, 'text')
    
    dg = ET.SubElement(q, 'defaultgrade')
    dg.text = '1.0000000'
    pen = ET.SubElement(q, 'penalty')
    pen.text = '0.3333333'
    hid = ET.SubElement(q, 'hidden')
    hid.text = '0'
    syn = ET.SubElement(q, 'synchronize')
    syn.text = '1'
    single = ET.SubElement(q, 'single')
    single.text = '0'
    answernumbering = ET.SubElement(q, 'answernumbering')
    answernumbering.text = 'abc'
    shuffleanswers = ET.SubElement(q, 'shuffleanswers')
    shuffleanswers.text = '0'
    correctanswerformat_e = ET.SubElement(q, 'correctanswerformat')
    correctanswerformat_e.text = str(correctanswerformat)
    correctanswerlength_e = ET.SubElement(q, 'correctanswerlength')
    correctanswerlength_e.text = str(correctanswerlength)
    
    ans = ET.SubElement(q, 'answer', fraction='100', format='moodle_auto_format')
    at = ET.SubElement(ans, 'text')
    at.text = formula
    tol = ET.SubElement(ans, 'tolerance')
    tol.text = str(tolerance)
    tt = ET.SubElement(ans, 'tolerancetype')
    tt.text = str(tolerancetype)
    caf = ET.SubElement(ans, 'correctanswerformat')
    caf.text = str(correctanswerformat)
    cal = ET.SubElement(ans, 'correctanswerlength')
    cal.text = str(correctanswerlength)
    fb = ET.SubElement(ans, 'feedback', format='html')
    fbt = ET.SubElement(fb, 'text')
    
    # Dataset definitions
    dds = ET.SubElement(q, 'dataset_definitions')
    
    return q


def process_cw03(filepath):
    """Update Cw03 formulas and add missing questions."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # === Update existing formulas ===
    
    # Zad 3.2 — Moc kotła: use h_steam polynomial
    q32 = find_question(root, 'Cw03_Zad3_2_Moc_kotla')
    if q32:
        formula = f"{{md}} * 1000 / 3600 * (({H_STEAM}) - 4.19 * {{tz}})"
        update_answer(q32, formula)
        print("  ✓ Updated Cw03_Zad3_2 formula (h_steam polynomial)")
    
    # Zad 3.3 — Zuzycie gazu: depends on 3.2's Q
    q33 = find_question(root, 'Cw03_Zad3_3_Zuzycie_gazu')
    if q33:
        formula = f"{{md}} * 1000 / 3600 * (({H_STEAM}) - 4.19 * {{tz}}) / ({{ek}} * 50000 * 0.7) * 3600"
        update_answer(q33, formula)
        print("  ✓ Updated Cw03_Zad3_3 formula")
    
    # Zad 3.5 — Stopien suchosci: use hf(p), hg(p) polynomials
    q35 = find_question(root, 'Cw03_Zad3_5_Stopien_suchosci')
    if q35:
        formula = f"({{hm}} - ({HF_P})) / (({HG_P}) - ({HF_P}))"
        update_answer(q35, formula)
        print("  ✓ Updated Cw03_Zad3_5 formula (hf/hg polynomials)")
    
    # Zad 3.7 — Entropia: use s_steam and s_water polynomials
    q37 = find_question(root, 'Cw03_Zad3_7_Entropia_kotla')
    if q37:
        formula = f"{{md}} * 1000 / 3600 * (({S_STEAM}) - ({S_WATER}))"
        update_answer(q37, formula)
        print("  ✓ Updated Cw03_Zad3_7 formula (s polynomials)")
    
    # === Add missing question: Zad 3.4 (Dławienie) ===
    # T after throttling ≈ Tsat if h_steam > hg, else T from superheat
    # Simple approach: if the steam stays superheated after throttling,
    # the answer is approximately h_steam(p1,T1) evaluated at p2
    # We can express T_after_throttle using the inverse: T ≈ (h - a0 - a2*p2 - a5*p2^2) / (a1 + a3*p2)
    # But this gets complex. Better to add as Tsat(p_dlaw) for the case when it becomes sat/superheat
    # For now, add as a simple question with Tsat
    
    # === Add missing question: Zad 3.8 (Kondensat) ===
    q_template = find_question(root, 'Cw03_Zad3_2_Moc_kotla')  # use as template for vars
    
    if not find_question(root, 'Cw03_Zad3_8_Bilans_kondensatu'):
        q38 = make_calculated_question(
            'Cw03_Zad3_8_Bilans_kondensatu',
            'Wymiennik ciepła skrapla parę z parametrów kotłowych do stanu cieczy nasyconej przy ciśnieniu dławienia {pdl} bar. '
            'Oblicz moc cieplną wymiennika [kW].',
            f"{{md}} * 1000 / 3600 * (({H_STEAM}) - ({HF_P}))",
            5,  # tolerance 5 kW
            tolerancetype=1, correctanswerlength=1
        )
        # Copy dataset vars from existing question
        if q_template:
            for var in ['md', 'pk', 'tp', 'tz', 'ek', 'pdl']:
                copy_dataset_item(q_template, var, q38)
        root.append(q38)
        print("  + Added Cw03_Zad3_8_Bilans_kondensatu")
    
    tree.write(filepath, encoding='unicode', xml_declaration=True)
    return True


def process_cw04(filepath):
    """Update Cw04 formulas with polynomial approximations."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Use p1t/t1t for inlet steam, p2t for outlet
    # h_steam at inlet uses pk→p1t, tp→t1t variable mapping
    H_INLET = H_STEAM.replace('{pk}', '{p1t}').replace('{tp}', '{t1t}')
    S_INLET = S_STEAM.replace('{pk}', '{p1t}').replace('{tp}', '{t1t}')
    
    # Zad 4.3 — Moc idealna
    q43 = find_question(root, 'Cw04_Zad4_3_Moc_turbiny_idealna')
    if q43:
        # x_is = (s1 - sf(p2)) / (sg(p2) - sf(p2))
        # h2s = hf(p2) + x_is * (hg(p2) - hf(p2))
        # N = mdt * (h1 - h2s)
        # Substitute directly:
        # h2s = hf + (s1-sf)/(sg-sf) * (hg-hf)
        formula = (
            f"{{mdt}} * (({H_INLET}) - "
            f"(({HF_P2}) + (({S_INLET}) - ({SF_P})) / (({SG_P}) - ({SF_P})) * (({HG_P2}) - ({HF_P2}))))"
        )
        update_answer(q43, formula)
        print("  ✓ Updated Cw04_Zad4_3 formula (full polynomial)")
    
    # Zad 4.4 — Moc rzeczywista 
    q44 = find_question(root, 'Cw04_Zad4_4_Moc_rzeczywista')
    if q44:
        # N_real = eis * N_ideal
        h2s_expr = (f"(({HF_P2}) + (({S_INLET}) - ({SF_P})) / (({SG_P}) - ({SF_P})) * (({HG_P2}) - ({HF_P2})))")
        formula = f"{{eis}} * {{mdt}} * (({H_INLET}) - {h2s_expr})"
        update_answer(q44, formula)
        print("  ✓ Updated Cw04_Zad4_4 formula")
    
    # Zad 4.4b — Entalpia rzeczywista
    q44b = find_question(root, 'Cw04_Zad4_4b_Entalpia_rzeczywista')
    if q44b:
        h2s_expr = (f"(({HF_P2}) + (({S_INLET}) - ({SF_P})) / (({SG_P}) - ({SF_P})) * (({HG_P2}) - ({HF_P2})))")
        formula = f"({H_INLET}) - {{eis}} * (({H_INLET}) - {h2s_expr})"
        update_answer(q44b, formula)
        print("  ✓ Updated Cw04_Zad4_4b formula")
    
    tree.write(filepath, encoding='unicode', xml_declaration=True)
    return True


def process_cw06(filepath):
    """Update Cw06 R134a formulas with polynomial approximations."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # Zad 6.1 — EER
    q61 = find_question(root, 'Cw06_Zad6_1_EER')
    if q61:
        formula = f"(({H1_R134A}) - ({H3_R134A})) / (({H2S_R134A}) - ({H1_R134A}))"
        update_answer(q61, formula)
        print("  ✓ Updated Cw06_Zad6_1 EER formula (R134a polynomials)")
    
    # Zad 6.2 — Moc sprężarki
    q62 = find_question(root, 'Cw06_Zad6_2_Moc_sprezarki')
    if q62:
        formula = f"{{Qo6}} / ((({H1_R134A}) - ({H3_R134A})) / (({H2S_R134A}) - ({H1_R134A})))"
        update_answer(q62, formula)
        print("  ✓ Updated Cw06_Zad6_2")
    
    # Zad 6.3 — Strumien masy
    q63 = find_question(root, 'Cw06_Zad6_3_Strumien_masy')
    if q63:
        formula = f"{{Qo6}} / (({H1_R134A}) - ({H3_R134A}))"
        update_answer(q63, formula)
        print("  ✓ Updated Cw06_Zad6_3")
    
    # Zad 6.4 — COP pompy ciepła
    q64 = find_question(root, 'Cw06_Zad6_4_COP_pompa_ciepla')
    if q64:
        formula = f"(({H1_R134A}) - ({H3_R134A})) / (({H2S_R134A}) - ({H1_R134A})) + 1"
        update_answer(q64, formula)
        print("  ✓ Updated Cw06_Zad6_4")
    
    # Zad 6.7 — Prędkość rurociągu (now uses v polynomial instead of 0.08)
    q67 = find_question(root, 'Cw06_Zad6_7_Predkosc_rurociagu')
    if q67:
        formula = f"({{Qo6}} / (({H1_R134A}) - ({H3_R134A}))) * ({V_R134A}) / (3.14159265 * pow({{dr6}} / 1000, 2) / 4)"
        update_answer(q67, formula)
        print("  ✓ Updated Cw06_Zad6_7 (v_g polynomial)")
    
    # Add missing: Zad 6.6 — R134a vs R290
    if not find_question(root, 'Cw06_Zad6_6_EER_R290'):
        q66 = make_calculated_question(
            'Cw06_Zad6_6_EER_R290',
            'Porównaj EER obiegu chłodniczego z propanu (R290) pracującego między temperaturami '
            'parowania {to6}°C a skraplania {tk6}°C. Oblicz EER dla R290.',
            f"(({H1_R290}) - ({H3_R290_TK})) / (({H2S_R290}) - ({H1_R290}))",
            0.3,
            correctanswerlength=2
        )
        q_template = find_question(root, 'Cw06_Zad6_1_EER')
        if q_template:
            for var in ['to6', 'tk6', 'Qo6', 'dr6']:
                copy_dataset_item(q_template, var, q66)
        root.append(q66)
        print("  + Added Cw06_Zad6_6_EER_R290")
    
    tree.write(filepath, encoding='unicode', xml_declaration=True)
    return True


def process_cw07(filepath):
    """Update Cw07 formulas — HVAC uses cp*ΔT approximation which is OK for dry air."""
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # The existing formulas use cp*ΔT which is a reasonable approximation
    # for dry air processes (Zad 7.1, 7.2 are heating/cooling without moisture change).
    # HAPropsSI would be more accurate but the approximation error is < 5%.
    # We keep current formulas but add missing questions.
    
    q_template = find_question(root, 'Cw07_Zad8_1_Moc_nagrzewnicy_zima')
    
    # Add Zad 7.9 Rekuperacja
    if not find_question(root, 'Cw07_Zad8_9_Rekuperacja'):
        # Q_rec = ṁ * cp * rec/100 * (t_wewn - t_zima) 
        # This is the heat recovered from exhaust air
        q79 = make_calculated_question(
            'Cw07_Zad8_9_Rekuperacja',
            'W centrali wentylacyjnej zainstalowano rekuperator krzyżowy o sprawności temperaturowej {rec8}%. '
            'Oblicz moc cieplną odzyskaną z powietrza wywiewanego zimą [kW].',
            "1.2 * {Vd8} / 3600 * 1005 * {rec8} / 100 * ({tw8} - {tzz}) / 1000",
            2,
            correctanswerlength=1
        )
        if q_template:
            for var in ['Vd8', 'tw8', 'tzz', 'rec8', 'tzl', 'tn8', 'Qj8']:
                copy_dataset_item(q_template, var, q79)
        root.append(q79)
        print("  + Added Cw07_Zad8_9_Rekuperacja")
    
    tree.write(filepath, encoding='unicode', xml_declaration=True)
    return True


# ============================================================
# MAIN
# ============================================================
if __name__ == '__main__':
    print("=" * 60)
    print("UPDATING XML FORMULAS WITH POLYNOMIAL APPROXIMATIONS")
    print("=" * 60)
    
    files = {
        'Cw03': os.path.join(XML_DIR, 'Cw03_Kociol_Parowy_Calculated.xml'),
        'Cw04': os.path.join(XML_DIR, 'Cw04_Obieg_Rankine_Calculated.xml'),
        'Cw06': os.path.join(XML_DIR, 'Cw06_Projekt_Chlodniczy_Calculated.xml'),
        'Cw07': os.path.join(XML_DIR, 'Cw07_Projekt_HVAC_Calculated.xml'),
    }
    
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
    
    print("\n✓ All updates complete.")
