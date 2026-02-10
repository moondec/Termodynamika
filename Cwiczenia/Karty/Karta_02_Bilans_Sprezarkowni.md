# 🏭 Karta Projektowa 2: Bilans Sprężarkowni

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Dobór i weryfikacja sprężarki tłokowej

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| Ciśnienie ssania | $p_1$ | **{p1}** | bar |
| Ciśnienie tłoczenia | $p_2$ | **{p2}** | bar |
| Temperatura ssania | $t_1$ | **{t1}** | °C |
| Wydajność normalna | $\dot{V}_n$ | **{Vn}** | m³/h |
| Wykładnik politropy | $n$ | **{n}** | — |
| Stała gazowa powietrza | $R$ | 287 | J/(kg·K) |
| Ciepło właściwe | $c_p$ | 1005 | J/(kg·K) |

---

## Zadania do Wykonania

### Zadanie 2.1: Praca techniczna sprężania
Oblicz jednostkową pracę techniczną $l_t$ dla przemiany politropowej:
$$l_t = \frac{n}{n-1} R T_1 \left[\left(\frac{p_2}{p_1}\right)^{\frac{n-1}{n}} - 1\right]$$

**Wynik:** $l_t$ = ______ kJ/kg

### Zadanie 2.2: Moc silnika napędowego
Oblicz strumień masy i moc teoretyczną sprężarki.  
Sprawność mechaniczna: $\eta_m = 0.9$.  
**Wynik:** $N_t$ = ______ kW, $N_{silnika}$ = ______ kW

### Zadanie 2.3: Temperatura tłoczenia
$$T_2 = T_1 \cdot \left(\frac{p_2}{p_1}\right)^{\frac{n-1}{n}}$$
**Wynik:** $t_2$ = ______ °C

### Zadanie 2.4: Bilans ciepła chłodnicy
Schłodzenie powietrza do **{t_chlod}** °C po sprężarce.  
**Wynik:** $\dot{Q}$ = ______ kW

### Zadanie 2.5: Sprężanie dwustopniowe
Ciśnienie pośrednie: $p_{pośr} = \sqrt{p_1 \cdot p_2}$.  
Chłodzenie międzystopniowe do **{t_chlod}** °C.  
**Wynik:** $T_{I}$ = ______ °C, $T_{II}$ = ______ °C

### Zadanie 2.6: Porównanie procesów
Oblicz $l_t$ dla trzech przemiany: izotermicznej, politropowej i adiabatycznej ($\kappa = 1.4$).  
**Wynik:** $l_{izo}$ = ______, $l_{pol}$ = ______, $l_{adi}$ = ______ kJ/kg

### Zadanie 2.7: Dobór chłodnicy wodnej
Woda $t_{w,in}$ = **{tw_in}** °C, $t_{w,out}$ = **{tw_out}** °C max.  
**Wynik:** $\dot{m}_w$ = ______ kg/s = ______ l/min

### Zadanie 2.8: Wyznaczanie wykładnika politropy
Dane serwisowe: $t_1$ = **{t1_serwis}** °C, $p_1$ = **{p1_serwis}** bar, $t_2$ = **{t2_serwis}** °C, $p_2$ = **{p2_serwis}** bar.  
**Wynik:** $n$ = ______

---

## Zadanie Domowe (Raport 2)
Oblicz, jaki strumień wody [l/min] można podgrzać ciepłem z chłodnicy sprężarki (odzysk 80%, $t_{in}$ = 10°C → $t_{out}$ = 45°C).

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok |
|---------|-----|-----|------|
| `{p1}` | 1.0 | 1.0 | 0 |
| `{p2}` | 7 | 12 | 0.5 |
| `{t1}` | 15 | 25 | 1 |
| `{Vn}` | 60 | 150 | 10 |
| `{n}` | 1.25 | 1.38 | 0.01 |
| `{t_chlod}` | 25 | 40 | 5 |
| `{tw_in}` | 10 | 20 | 5 |
| `{tw_out}` | 35 | 45 | 5 |
| `{t1_serwis}` | 18 | 28 | 2 |
| `{p1_serwis}` | 1.0 | 1.0 | 0 |
| `{t2_serwis}` | 180 | 240 | 10 |
| `{p2_serwis}` | 6 | 10 | 1 |
