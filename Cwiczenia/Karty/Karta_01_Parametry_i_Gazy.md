# 🏭 Karta Projektowa 1: Parametry Stanu i Gazy Doskonałe

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Inwentaryzacja sieci sprężonego powietrza

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| Objętość zbiornika | $V$ | **{V}** | m³ |
| Nadciśnienie (manometr) | $p_{man}$ | **{p_man}** | bar |
| Temperatura otoczenia/gazu | $t$ | **{t}** | °C |
| Ciśnienie atmosferyczne | $p_{atm}$ | **{p_atm}** | mmHg |
| Stała gazowa powietrza | $R$ | 287 | J/(kg·K) |

---

## Zadania do Wykonania

### Zadanie 1.1: Masa powietrza w zbiorniku
Oblicz **ciśnienie absolutne** w zbiorniku, a następnie masę powietrza korzystając z równania Clapeyrona:
$$p \cdot V = m \cdot R \cdot T$$

**Wynik:** $m$ = ______ kg

### Zadanie 1.2: Próba hydrauliczna
Oblicz masę wody potrzebną do napełnienia zbiornika ($\rho_{wody} = 1000$ kg/m³).  
**Wynik:** $m_w$ = ______ kg

### Zadanie 1.2b: Pożar w hali — ciśnienie awaryjne
Temperatura wzrasta do **{t_fire}** °C. Oblicz ciśnienie w zamkniętym zbiorniku (prawo Gay-Lussaca).  
**Wynik:** $p_2$ = ______ kPa (abs)

### Zadanie 1.2c: Mieszanina gazów (Dalton)
Drugi zbiornik: **{y_N2}**% $N_2$ + **{y_O2}**% $O_2$ (objętościowo), $p$ = **{p_mix}** bar (abs), $t$ = **{t_mix}** °C, $V$ = **{V_mix}** m³.  
Oblicz ciśnienia parcjalne i masy składników.

- $R_{N_2} = 297$ J/(kg·K), $R_{O_2} = 260$ J/(kg·K)

**Wynik:** $p_{N_2}$ = ______ kPa, $m_{N_2}$ = ______ kg

### Zadanie 1.2d: Gęstość i objętość właściwa
Porównaj gęstość powietrza w zbiorniku ciśnieniowym z gęstością w warunkach normalnych (101.3 kPa, 273 K).  
**Wynik:** $\rho_{zb}$ = ______ kg/m³, $\rho_n$ = ______ kg/m³

### Zadanie 1.3: Skale temperatur
Zawór bezpieczeństwa otworzy się przy **{T_valve}** °F. Max. temp. procesu: **{t_process}** °C.  
Czy zawór nadaje się?  
**Wynik:** $T_{limit}$ = ______ °C → Zawór _______ (nadaje się / nie nadaje się)

---

## Zadanie Domowe (Raport 1)
Dobierz sprężarkę do napompowania zbiornika od $p_{atm}$ do $p_{rob}$ w czasie 1 godziny.
Przyjmij $t_{sprężania} = 40°C$.

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok | Powiązanie |
|---------|-----|-----|------|------------|
| `{V}` | 3 | 8 | 0.5 | — |
| `{p_man}` | 6 | 12 | 0.5 | — |
| `{t}` | 15 | 35 | 1 | — |
| `{p_atm}` | 740 | 770 | 5 | — |
| `{t_fire}` | 200 | 400 | 50 | — |
| `{y_N2}` | 70 | 85 | 5 | `{y_O2}` = 100 − `{y_N2}` |
| `{p_mix}` | 3 | 8 | 1 | — |
| `{t_mix}` | 15 | 30 | 5 | — |
| `{V_mix}` | 1 | 4 | 0.5 | — |
| `{T_valve}` | 200 | 300 | 10 | — |
| `{t_process}` | 120 | 180 | 10 | — |
