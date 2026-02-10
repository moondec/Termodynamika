# 🏭 Karta Projektowa 6: Projekt Chłodniczy

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Chłodzenie magazynu surowców

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| Wydajność chłodnicza | $\dot{Q}_o$ | **{Qo}** | kW |
| Temp. parowania | $t_o$ | **{to}** | °C |
| Temp. skraplania | $t_k$ | **{tk}** | °C |
| Czynnik chłodniczy | — | R134a | — |

---

## Odczyt z wykresu p-h (R134a)

Odczytaj z wykresu log(p)-h dla czynnika R134a:

| Punkt | Opis | $h$ [kJ/kg] |
|-------|------|-------------|
| 1 | Para nasycona ($t_o$) | ______ |
| 2 | Po sprężaniu ($s=const$ do $p_k$) | ______ |
| 3 | Ciecz nasycona ($t_k$) | ______ |
| 4 | Po dławieniu ($h_4 = h_3$) | ______ |

---

## Zadania do Wykonania

### Zadanie 6.1–6.3: Podstawowy obieg
- Wydajność chłodnicza: $q_o = h_1 - h_4$ → $\dot{m} = \dot{Q}_o / q_o$
- Moc sprężarki: $N = \dot{m} \cdot (h_2 - h_1)$
- EER = $q_o / (h_2 - h_1)$

**Wynik:** $\dot{m}$ = ______ kg/s, $N$ = ______ kW, EER = ______

### Zadanie 6.4: Pompa ciepła
$COP_{PC} = Q_k / N$ (ten sam obieg, ale celem jest $Q_k$).  
**Wynik:** $COP_{PC}$ = ______

### Zadanie 6.5: Wpływ temperatury skraplania
Nowa $t_k$ = **{tk_alt}** °C. Odczytaj nowe $h_2, h_3$ z wykresu.  
**Wynik:** $EER_{nowy}$ = ______, Pogorszenie: ______ %

### Zadanie 6.6: Porównanie R134a vs R290
Odczytaj z wykresu R290 (propan): $h_1, h_2, h_3$ dla tych samych temperatur.  
**Wynik:** $EER_{R290}$ = ______, $\dot{m}_{R290}$ = ______ kg/s

### Zadanie 6.7: Dobór rurociągu ssawnego
Średnica rury: $d$ = **{d_rura}** mm. Objętość właściwa na ssaniu: z wykresu.  
$$w = \frac{\dot{m} \cdot v_1}{\pi d^2 / 4}$$
**Wynik:** $w$ = ______ m/s → Czy prędkość jest dopuszczalna (8–15 m/s)?

---

## Zadanie Domowe (Raport 6)
Rzeczywisty obieg: przegrzanie par $\Delta T_{sh}$ = 5K, dochłodzenie cieczy $\Delta T_{sc}$ = 5K. Oblicz nowy EER.

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok |
|---------|-----|-----|------|
| `{Qo}` | 200 | 500 | 50 |
| `{to}` | -5 | 5 | 1 |
| `{tk}` | 35 | 45 | 5 |
| `{tk_alt}` | 45 | 55 | 5 |
| `{d_rura}` | 50 | 100 | 10 |
