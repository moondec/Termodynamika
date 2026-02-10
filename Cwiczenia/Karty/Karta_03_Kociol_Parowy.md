# 🏭 Karta Projektowa 3: Bilans Kotłowni Parowej

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Weryfikacja kotłowni parowej

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| Ciśnienie pary wylotowej | $p$ | **{p_kociol}** | bar (abs) |
| Temperatura pary wylotowej | $t$ | **{t_para}** | °C |
| Strumień masy pary | $\dot{m}$ | **{m_dot}** | t/h |
| Temp. wody zasilającej | $t_{zas}$ | **{t_zas}** | °C |
| Sprawność kotła | $\eta_k$ | **{eta_k}** | — |
| Wartość opałowa gazu | $W_d$ | 50 | MJ/kg |

---

## Zadania do Wykonania

### Zadanie 3.1: Stan pary (tablice)
Sprawdź w tablicach nasycenia temperaturę $t_{sat}$ dla $p$ = **{p_kociol}** bar.  
Porównaj z $t$ = **{t_para}** °C → Stan pary: ____________

### Zadanie 3.2: Bilans energii kotła
Odczytaj z tablic: $h_1$ (woda, **{t_zas}** °C), $h_2$ (para, **{p_kociol}** bar, **{t_para}** °C).  
$$\dot{Q} = \dot{m} \cdot (h_2 - h_1)$$
**Wynik:** $\dot{Q}$ = ______ kW

### Zadanie 3.3: Zużycie paliwa
**Wynik:** $\dot{V}_{gaz}$ = ______ m³/h (gęstość gazu $\rho = 0.7$ kg/m³)

### Zadanie 3.4: Dławienie pary
Redukcja ciśnienia z **{p_kociol}** bar do **{p_dlawienie}** bar.  
Proces izentalpowy ($h = const$). Odczytaj temperaturę po dławieniu z tablic.  
**Wynik:** $t_3$ ≈ ______ °C

### Zadanie 3.5: Para mokra — stopień suchości
Pomiar w odbiorniku: $p$ = **{p_mokra}** bar, zmierzona $h$ = **{h_mokra}** kJ/kg.  
$$x = \frac{h - h'}{h'' - h'}$$
**Wynik:** $x$ = ______

### Zadanie 3.6: Interpolacja w tablicach
Para przegrzana: $p$ = **{p_interp}** bar, $t$ = **{t_interp}** °C.  
Wykonaj interpolację liniową dla $h$ i $s$.  
**Wynik:** $h$ ≈ ______ kJ/kg, $s$ ≈ ______ kJ/(kg·K)

### Zadanie 3.7: Entropia w kotle
Oblicz $\Delta s$ między wodą zasilającą a parą wylotową.  
**Wynik:** $\Delta s$ = ______ kJ/(kg·K)

### Zadanie 3.8: Bilans kondensatu
Para skrapla się z **{p_dlawienie}** bar do wrzątku ($h'$).  
**Wynik:** $q_{wym}$ = ______ kJ/kg, $\dot{Q}_{wym}$ = ______ kW

---

## Zadanie Domowe (Raport 3)
Kocioł kondensacyjny — oblicz dodatkowy odzysk ciepła ze skraplania pary wodnej ze spalin.

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok |
|---------|-----|-----|------|
| `{p_kociol}` | 8 | 16 | 1 |
| `{t_para}` | 200 | 300 | 25 |
| `{m_dot}` | 1.5 | 3.0 | 0.5 |
| `{t_zas}` | 40 | 80 | 10 |
| `{eta_k}` | 0.85 | 0.95 | 0.05 |
| `{p_dlawienie}` | 1 | 4 | 1 |
| `{p_mokra}` | 2 | 6 | 1 |
| `{h_mokra}` | 2200 | 2600 | 50 |
| `{p_interp}` | 8 | 14 | 2 |
| `{t_interp}` | 225 | 275 | 25 |
