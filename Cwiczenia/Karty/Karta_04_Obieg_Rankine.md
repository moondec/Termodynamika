# 🏭 Karta Projektowa 4: Obieg Rankine'a — Mikroturbina

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Analiza mikroturbiny parowej (kogeneracja)

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| Ciśnienie wlotowe | $p_1$ | **{p1_turb}** | bar |
| Temperatura wlotowa | $t_1$ | **{t1_turb}** | °C |
| Ciśnienie wylotowe | $p_2$ | **{p2_turb}** | bar |
| Strumień masy pary | $\dot{m}$ | **{m_dot_turb}** | kg/s |
| Sprawność izentropowa | $\eta_{is}$ | **{eta_is}** | — |

---

## Zadania do Wykonania

### Zadanie 4.1: Ekspansja izentropowa ($s = const$)
Z tablic: $h_1$, $s_1$ dla ($p_1$, $t_1$). Sprawdź stan na wylocie ($s_2 = s_1$, $p_2$).  
**Wynik:** $h_1$ = ______ kJ/kg, $s_1$ = ______ kJ/(kg·K)

### Zadanie 4.2: Stopień suchości ($x_2$)
Jeśli $s_2 < s''(p_2)$ → para mokra.  
$$x_2 = \frac{s_2 - s'}{s'' - s'}$$
**Wynik:** $x_2$ = ______

### Zadanie 4.3: Moc turbiny
$$h_{2s} = h' + x_2 \cdot (h'' - h')$$
$$N_t = \dot{m} \cdot (h_1 - h_{2s})$$
**Wynik:** $N_t$ = ______ kW

### Zadanie 4.4: Sprawność izentropowa turbiny
$$h_{2r} = h_1 - \eta_{is} \cdot (h_1 - h_{2s})$$
$$N_r = \dot{m} \cdot (h_1 - h_{2r})$$
**Wynik:** $h_{2r}$ = ______ kJ/kg, $N_r$ = ______ kW

### Zadanie 4.5: Analiza wariantowa
Kocioł dostarczy parę **{p1_alt}** bar, **{t1_alt}** °C. Powtórz obliczenia.  
**Wynik:** $N_t'$ = ______ kW, Zmiana mocy: ______ %

### Zadanie 4.6: Sprawność Carnota
$$\eta_C = 1 - \frac{T_{zimne}}{T_{gorące}}$$
Porównaj sprawność Carnota z rzeczywistą sprawnością obiegu.  
**Wynik:** $\eta_C$ = ______ %

---

## Zadanie Domowe (Raport 4)
Oblicz opłacalność kogeneracji: koszt turbiny = **{koszt_turb}** PLN, $\eta_{gen}$ = 90%, cena prądu = 0.80 PLN/kWh, praca = 4000 h/rok.

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok |
|---------|-----|-----|------|
| `{p1_turb}` | 8 | 14 | 1 |
| `{t1_turb}` | 200 | 300 | 25 |
| `{p2_turb}` | 1 | 3 | 0.5 |
| `{m_dot_turb}` | 0.3 | 0.8 | 0.05 |
| `{eta_is}` | 0.75 | 0.85 | 0.05 |
| `{p1_alt}` | 12 | 20 | 2 |
| `{t1_alt}` | 250 | 350 | 25 |
| `{koszt_turb}` | 100000 | 200000 | 25000 |
