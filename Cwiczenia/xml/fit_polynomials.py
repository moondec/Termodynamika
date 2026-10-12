#!/usr/bin/env python3
"""Generate polynomial fits for Moodle calculated question formulas.
Uses CoolProp for reference data, numpy for polynomial fitting.

Postacie aproksymacji dla pary wodnej (stałe użyte w update_xml_formulas.py
i w plikach Cw03/Cw04_*_Calculated.xml):
- nasycenie h'(p), h''(p), s'(p), s''(p): wielomian 3. stopnia w ln(p),
  p = 0.5..6 bar (błąd h <= 0.1 kJ/kg, s <= 0.0003 kJ/(kgK));
- para przegrzana h(p,T), s(p,T): pełny wielomian 3. stopnia w zmiennych
  centrowanych (T-250, p-12.5), p = 10..15 bar, T = 200..300 °C
  (błąd h 0.03 kJ/kg, s 0.00005 kJ/(kgK)).
Poprzednie postacie (kwadratowe w T,p i sześcienne w p) dawały błąd mocy
turbiny w Cw04 do 2.76 %, powyżej tolerancji 2 %.
Wymaga: numpy, CoolProp (środowisko z tymi pakietami).
"""
import numpy as np
import os, sys

# Opcjonalna ścieżka do pakietów (jeśli CoolProp nie jest w aktywnym środowisku)
_EXTRA = '/Users/marekurbaniak/.virtualenvs/termo/lib/python3.13/site-packages'
if os.path.isdir(_EXTRA):
    sys.path.insert(0, _EXTRA)
from CoolProp.CoolProp import PropsSI, HAPropsSI


def poly_ln_str(c, var="{P}"):
    """Moodle string for a polynomial in ln(var); c from np.polyfit (hi->lo)."""
    c = c[::-1]
    parts = [f"{c[0]:.6g}"]
    for i, ci in enumerate(c[1:], 1):
        term = f"log({var})" if i == 1 else f"pow(log({var}),{i})"
        parts.append(f"({ci:+.6g})*{term}" if ci < 0 else f"{ci:.6g}*{term}")
    return " + ".join(parts)


# pełny wielomian 3. stopnia w (tt, pp) = (T-250, p-12.5)
SH_TERMS = [("1", lambda a, b: a * 0 + 1), ("tt", lambda a, b: a), ("pp", lambda a, b: b),
            ("tt*pp", lambda a, b: a * b), ("pow(tt,2)", lambda a, b: a * a),
            ("pow(pp,2)", lambda a, b: b * b), ("pow(tt,3)", lambda a, b: a ** 3),
            ("pow(tt,2)*pp", lambda a, b: a * a * b), ("tt*pow(pp,2)", lambda a, b: a * b * b),
            ("pow(pp,3)", lambda a, b: b ** 3)]


def sh_design(T, P):
    tt, pp = T - 250, P - 12.5
    return np.column_stack([f(tt, pp) for _, f in SH_TERMS])


def sh_str(c):
    """Moodle string for the centered cubic; {T} in °C, {P} in bar."""
    parts = []
    for (name, _), ci in zip(SH_TERMS, c):
        s = f"{ci:.6g}"
        parts.append(s if name == "1" else (f"({s})*{name}" if ci < 0 else f"{s}*{name}"))
    return " + ".join(parts).replace("tt", "({T}-250)").replace("pp", "({P}-12.5)")

print("=" * 70)
print("POLYNOMIAL FITS FOR MOODLE XML FORMULAS")
print("=" * 70)

# ============================================================
# 1. WATER/STEAM — h(p,T) superheated
#    Range: p = 10..15 bar, T = 200..300 °C (zbiory Cw03/Cw04)
#    Fit: full cubic in (T-250, p-12.5)
# ============================================================
print("\n--- h_steam(p, T) [kJ/kg] --- range: p=10..15 bar, T=200..300°C")
pp = np.linspace(10, 15, 11)   # bar
tt = np.linspace(200, 300, 21)  # °C
P, T = np.meshgrid(pp, tt)
P_flat = P.flatten()
T_flat = T.flatten()
h_flat = np.array([PropsSI("H", "P", p*1e5, "T", t+273.15, "Water")/1000
                    for p, t in zip(P_flat, T_flat)])

A = sh_design(T_flat, P_flat)
coef_h, res, _, _ = np.linalg.lstsq(A, h_flat, rcond=None)
h_pred = A @ coef_h
err = np.max(np.abs(h_flat - h_pred))
HSH = sh_str(coef_h)
print(f"  h = {HSH}")
print(f"  Max error: {err:.3f} kJ/kg ({err/np.mean(h_flat)*100:.4f}%)")

# ============================================================
# 2. WATER/STEAM — s(p,T) superheated (same form)
# ============================================================
print("\n--- s_steam(p, T) [kJ/(kgK)] --- range: p=10..15 bar, T=200..300°C")
s_flat = np.array([PropsSI("S", "P", p*1e5, "T", t+273.15, "Water")/1000
                    for p, t in zip(P_flat, T_flat)])
coef_s, _, _, _ = np.linalg.lstsq(A, s_flat, rcond=None)
s_pred = A @ coef_s
err_s = np.max(np.abs(s_flat - s_pred))
SSH = sh_str(coef_s)
print(f"  s = {SSH}")
print(f"  Max error: {err_s:.6f} kJ/(kgK) ({err_s/np.mean(s_flat)*100:.4f}%)")

# ============================================================
# 3. WATER — h_water(T) saturated liquid
#    Range: T = 40..80°C
# ============================================================
print("\n--- h_water(T) sat. liquid [kJ/kg] --- range: T=40..80°C")
tw = np.arange(40, 85, 5)
hw = np.array([PropsSI("H", "T", t+273.15, "Q", 0, "Water")/1000 for t in tw])
coef_hw = np.polyfit(tw, hw, 2)
hw_pred = np.polyval(coef_hw, tw)
err_hw = np.max(np.abs(hw - hw_pred))
print(f"  h = {coef_hw[0]:.6f}*T^2 + {coef_hw[1]:.4f}*T + {coef_hw[2]:.4f}")
print(f"  Simpler: h ≈ 4.19*T (old) vs exact max err = {np.max(np.abs(hw - 4.19*tw)):.2f}")
print(f"  Poly max error: {err_hw:.3f} kJ/kg")

# ============================================================
# 4. WATER — Tsat(p) saturation temperature
#    Range: p = 1..16 bar
# ============================================================
print("\n--- Tsat(p) [°C] --- range: p=1..16 bar")
ps = np.arange(1, 17, 1)
Ts = np.array([PropsSI("T", "P", p*1e5, "Q", 0, "Water")-273.15 for p in ps])
coef_Ts = np.polyfit(ps, Ts, 3)
Ts_pred = np.polyval(coef_Ts, ps)
err_Ts = np.max(np.abs(Ts - Ts_pred))
print(f"  Tsat = {coef_Ts[0]:.6f}*p^3 + {coef_Ts[1]:.4f}*p^2 + {coef_Ts[2]:.4f}*p + {coef_Ts[3]:.4f}")
print(f"  Max error: {err_Ts:.2f} °C")
# Verify
for p in [1, 2, 4, 8, 10, 12, 16]:
    real = PropsSI("T", "P", p*1e5, "Q", 0, "Water")-273.15
    pred = np.polyval(coef_Ts, p)
    print(f"    p={p:2d} bar: real={real:.1f}, poly={pred:.1f}, Δ={abs(real-pred):.1f}°C")

# ============================================================
# 5. WATER — h'(p), h''(p), s'(p), s''(p) saturation
#    Range: p = 0.5..6 bar (for Cw03/04 p_dlaw / p2_turb)
#    Fit: cubic in ln(p) (saturation curves are nearly linear in ln p)
# ============================================================
print("\n--- Saturation props h'/h''/s'/s'' vs p [bar] --- range: p=0.5..6, cubic in ln(p)")
ps2 = np.linspace(0.5, 6, 111)
u2 = np.log(ps2)
hf = np.array([PropsSI("H", "P", p*1e5, "Q", 0, "Water")/1000 for p in ps2])
hg = np.array([PropsSI("H", "P", p*1e5, "Q", 1, "Water")/1000 for p in ps2])
sf = np.array([PropsSI("S", "P", p*1e5, "Q", 0, "Water")/1000 for p in ps2])
sg = np.array([PropsSI("S", "P", p*1e5, "Q", 1, "Water")/1000 for p in ps2])

SAT = {}
for name, data in [("hp", hf), ("hpp", hg), ("sp", sf), ("spp", sg)]:
    c = np.polyfit(u2, data, 3)
    pred = np.polyval(c, u2)
    err = np.max(np.abs(data - pred))
    SAT[name] = poly_ln_str(c)
    print(f"  {name}(p) = {SAT[name]}  (max err: {err:.4f})")

# ============================================================
# 6. R134a — h_sat_vapor(T), h_sat_liquid(T), s_sat_vapor(T)
#    Range: T = -5..5 °C (evaporator), T = 35..55 °C (condenser)
# ============================================================
print("\n--- R134a h/s at saturation --- range: T=-5..55°C")
tr = np.arange(-5, 56, 1)
h1r = np.array([PropsSI("H", "T", t+273.15, "Q", 1, "R134a")/1000 for t in tr])
h3r = np.array([PropsSI("H", "T", t+273.15, "Q", 0, "R134a")/1000 for t in tr])
s1r = np.array([PropsSI("S", "T", t+273.15, "Q", 1, "R134a")/1000 for t in tr])

c_h1r = np.polyfit(tr, h1r, 2)
c_h3r = np.polyfit(tr, h3r, 2)
c_s1r = np.polyfit(tr, s1r, 2)
for name, c, data in [("h_g(T)", c_h1r, h1r), ("h_f(T)", c_h3r, h3r), ("s_g(T)", c_s1r, s1r)]:
    pred = np.polyval(c, tr)
    err = np.max(np.abs(data - pred))
    print(f"  {name} = {c[0]:.8f}*T^2 + {c[1]:.6f}*T + {c[2]:.4f}  (max err: {err:.3f})")

# ============================================================
# 7. R134a — P_sat(T) and h2s approximation
#    For isentropic compression: h2s(to, tk)
# ============================================================
print("\n--- R134a isentropic compression h2s(to, tk) ---")
to_range = np.arange(-5, 6, 1)
tk_range = np.arange(35, 56, 1)
TO, TK = np.meshgrid(to_range, tk_range)
to_f = TO.flatten()
tk_f = TK.flatten()
h2s_f = []
for to, tk in zip(to_f, tk_f):
    s1 = PropsSI("S", "T", to+273.15, "Q", 1, "R134a")
    Pk = PropsSI("P", "T", tk+273.15, "Q", 0, "R134a")
    h2 = PropsSI("H", "P", Pk, "S", s1, "R134a") / 1000
    h2s_f.append(h2)
h2s_f = np.array(h2s_f)

A2 = np.column_stack([np.ones_like(to_f), to_f, tk_f, to_f*tk_f, to_f**2, tk_f**2])
c_h2s, _, _, _ = np.linalg.lstsq(A2, h2s_f, rcond=None)
pred = A2 @ c_h2s
err = np.max(np.abs(h2s_f - pred))
print(f"  h2s = {c_h2s[0]:.4f} + {c_h2s[1]:.6f}*to + {c_h2s[2]:.6f}*tk + {c_h2s[3]:.8f}*to*tk + {c_h2s[4]:.8f}*to^2 + {c_h2s[5]:.8f}*tk^2")
print(f"  Max error: {err:.2f} kJ/kg ({err/np.mean(h2s_f)*100:.3f}%)")

# ============================================================
# 8. R134a — v (specific volume of sat. vapor)
# ============================================================
print("\n--- R134a v_sat_vapor(T) [m³/kg] --- range: T=-5..5°C")
to_v = np.arange(-5, 6, 1)
v_r = np.array([1/PropsSI("D", "T", t+273.15, "Q", 1, "R134a") for t in to_v])
c_v = np.polyfit(to_v, v_r, 2)
pred_v = np.polyval(c_v, to_v)
err_v = np.max(np.abs(v_r - pred_v))
print(f"  v(T) = {c_v[0]:.10f}*T^2 + {c_v[1]:.8f}*T + {c_v[2]:.6f}  (max err: {err_v:.6f} m³/kg)")

# ============================================================
# 9. R290 (Propane) — same props
# ============================================================
print("\n--- R290 h/s at saturation for EER comparison ---")
h1_290 = np.array([PropsSI("H", "T", t+273.15, "Q", 1, "R290")/1000 for t in tr])
h3_290 = np.array([PropsSI("H", "T", t+273.15, "Q", 0, "R290")/1000 for t in tr])
c_h1_290 = np.polyfit(tr, h1_290, 2)
c_h3_290 = np.polyfit(tr, h3_290, 2)
for name, c, data in [("h_g R290(T)", c_h1_290, h1_290), ("h_f R290(T)", c_h3_290, h3_290)]:
    pred = np.polyval(c, tr)
    err = np.max(np.abs(data - pred))
    print(f"  {name} = {c[0]:.8f}*T^2 + {c[1]:.6f}*T + {c[2]:.4f}  (max err: {err:.3f})")

# R290 h2s(to, tk)
h2s_290 = []
for to, tk in zip(to_f, tk_f):
    s1 = PropsSI("S", "T", to+273.15, "Q", 1, "R290")
    Pk = PropsSI("P", "T", tk+273.15, "Q", 0, "R290")
    h2 = PropsSI("H", "P", Pk, "S", s1, "R290") / 1000
    h2s_290.append(h2)
h2s_290 = np.array(h2s_290)
c_h2s_290, _, _, _ = np.linalg.lstsq(A2, h2s_290, rcond=None)
pred_290 = A2 @ c_h2s_290
err_290 = np.max(np.abs(h2s_290 - pred_290))
print(f"  h2s R290 = {c_h2s_290[0]:.4f} + {c_h2s_290[1]:.6f}*to + {c_h2s_290[2]:.6f}*tk + {c_h2s_290[3]:.8f}*to*tk + {c_h2s_290[4]:.8f}*to^2 + {c_h2s_290[5]:.8f}*tk^2")
print(f"  Max error: {err_290:.2f} kJ/kg ({err_290/np.mean(h2s_290)*100:.3f}%)")

print("\n\n=== MOODLE FORMULA TEMPLATES ===\n")

# Szablony: {T} = temperatura [°C], {P} = ciśnienie [bar] -> w update_xml_formulas.py
# podstawiane są nazwy zmiennych Moodle (tp/pk, t1t/p1t, pdl, p2t).
print("Cw03_Zad3_2: h_steam(p,T) - h_water(T)")
print(f"  HSH = {HSH}")
print(f"  h_water ≈ 4.19*{{tz}}")
print(f"  Formula: {{md}}*1000/3600 * ((HSH[tp,pk]) - 4.19*{{tz}})")

print(f"\nCw03_Zad3_5: x = (hm - hp(p)) / (hpp(p) - hp(p))")
print(f"  HP  = {SAT['hp']}")
print(f"  HPP = {SAT['hpp']}")

print(f"\nCw03_Zad3_7: ds = s_steam(p,T) - s_water(T)")
print(f"  SSH = {SSH}")
# s_water (sat liquid) fit
sw = np.array([PropsSI("S", "T", t+273.15, "Q", 0, "Water")/1000 for t in tw])
c_sw = np.polyfit(tw, sw, 2)
print(f"  s_water(T) = {c_sw[0]:.8f}*T^2 + {c_sw[1]:.6f}*T + {c_sw[2]:.4f}")

print(f"\nCw04 saturation at p2 (x_2s = (s1 - SP)/(SPP - SP), h_2s = HP + x_2s*(HPP - HP)):")
print(f"  SP  = {SAT['sp']}")
print(f"  SPP = {SAT['spp']}")
print(f"  HP  = {SAT['hp']}")
print(f"  HPP = {SAT['hpp']}")

# R134a
print(f"\nCw06 R134a:")
print(f"  h_g(T) = {c_h1r[0]:.6f}*T^2 + {c_h1r[1]:.4f}*T + {c_h1r[2]:.4f}")
print(f"  h_f(T) = {c_h3r[0]:.6f}*T^2 + {c_h3r[1]:.4f}*T + {c_h3r[2]:.4f}")
print(f"  h2s(to,tk) = {c_h2s[0]:.4f} + ({c_h2s[1]:.6f})*to + {c_h2s[2]:.6f}*tk + ({c_h2s[3]:.8f})*to*tk + ({c_h2s[4]:.8f})*to^2 + {c_h2s[5]:.8f}*tk^2")
print(f"  v_g(T) = {c_v[0]:.8f}*T^2 + ({c_v[1]:.6f})*T + {c_v[2]:.6f}")

print("\nDONE.")
