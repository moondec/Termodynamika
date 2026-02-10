# 🏭 Karta Projektowa 5: Odzysk Ciepła Odpadowego

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Wymiennik ciepła na spalinach kotłowni

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| Strumień masy spalin | $\dot{m}_s$ | **{ms}** | kg/s |
| Temp. spalin na wejściu | $t_{s,in}$ | **{ts_in}** | °C |
| Temp. spalin na wyjściu | $t_{s,out}$ | **{ts_out}** | °C |
| Temp. wody na wejściu | $t_{w,in}$ | **{tw_in}** | °C |
| Temp. wody na wyjściu | $t_{w,out}$ | **{tw_out}** | °C |
| $c_p$ spalin | — | 1000 | J/(kg·K) |
| $c_p$ wody | — | 4190 | J/(kg·K) |
| Temp. otoczenia | $T_0$ | **{T0}** | °C |

---

## Zadania do Wykonania

### Zadanie 5.1: Bilans energii wymiennika
$$\dot{Q}_{spaliny} = \dot{m}_s \cdot c_s \cdot (t_{s,in} - t_{s,out})$$
$$\dot{m}_w = \frac{\dot{Q}}{c_w \cdot (t_{w,out} - t_{w,in})}$$
**Wynik:** $\dot{Q}$ = ______ kW, $\dot{m}_w$ = ______ kg/s

### Zadanie 5.2: Generacja entropii (II Zasada)
$$\Delta \dot{S}_{spaliny} = \dot{m}_s \cdot c_s \cdot \ln(T_{s,out}/T_{s,in})$$
$$\Delta \dot{S}_{woda} = \dot{m}_w \cdot c_w \cdot \ln(T_{w,out}/T_{w,in})$$
**Wynik:** $\Delta \dot{S}_{gen}$ = ______ W/K

### Zadanie 5.3: Strata egzergii (Gouy-Stodola)
$$W_{stracona} = T_0 \cdot \Delta \dot{S}_{gen}$$
**Wynik:** $W_{stracona}$ = ______ kW

### Zadanie 5.4: Sprawność Carnota wymiennika
Maksymalna praca z silnika Carnota między $T_{s,in}$ a $T_0$.  
**Wynik:** $\eta_C$ = ______ %, $W_{max}$ = ______ kW, $\psi$ = ______ %

### Zadanie 5.5: Przeciwprąd vs współprąd
Dla wymiennika **przeciwprądowego**: jaką $t_{w,out}$ można osiągnąć?  
Oblicz nową generację entropii i porównaj.  
**Wynik:** $\Delta \dot{S}_{gen,pp}$ = ______ W/K, Redukcja: ______ %

### Zadanie 5.6: Kaskada wymienników
Wymiennik A: spaliny **{ts_in}** → **{t_kaskada}** °C (woda kotłowa do 90°C).  
Wymiennik B: spaliny **{t_kaskada}** → **{ts_out}** °C (woda użytkowa do 50°C).  
**Wynik:** $\dot{Q}_A$ = ______ kW, $\dot{Q}_B$ = ______ kW

---

## Zadanie Domowe (Raport 5)
Zwiększ $t_{w,out}$ do 95°C. Jak zmieni się generacja entropii?

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok |
|---------|-----|-----|------|
| `{ms}` | 0.5 | 2.0 | 0.25 |
| `{ts_in}` | 250 | 350 | 25 |
| `{ts_out}` | 120 | 180 | 10 |
| `{tw_in}` | 15 | 25 | 5 |
| `{tw_out}` | 60 | 90 | 10 |
| `{T0}` | 15 | 25 | 5 |
| `{t_kaskada}` | 200 | 240 | 10 |
