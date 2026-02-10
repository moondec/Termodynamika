# 🏭 Karta Projektowa 8: Projekt Klimatyzacji (HVAC)

## Projekt: Modernizacja Hali Przemysłowej „Termo-Tech"

**Rola:** Młodszy Inżynier Energetyk  
**Etap:** Klimatyzacja hali montażowej

---

## Dane Projektowe

| Parametr | Symbol | Wartość | Jednostka |
|----------|--------|---------|-----------|
| **Zima** | | | |
| Temp. zewnętrzna | $t_Z$ | **{tz_zima}** | °C |
| Wilgotność zewn. | $\varphi_Z$ | **{phi_zima}** | % |
| **Lato** | | | |
| Temp. zewnętrzna | $t_Z$ | **{tz_lato}** | °C |
| Wilgotność zewn. | $\varphi_Z$ | **{phi_lato}** | % |
| **Hala (wymagane)** | | | |
| Temp. wewnętrzna | $t_W$ | **{tw}** | °C |
| Wilgotność wewn. | $\varphi_W$ | **{phi_w}** | % |
| Strumień powietrza | $\dot{V}$ | **{V_dot}** | m³/h |
| Zyski ciepła jawnego | $Q_j$ | **{Qj}** | kW |
| Zyski wilgoci | $W$ | **{W}** | kg/h |

---

## Zadania do Wykonania

### Zadanie 8.1: Proces zimowy (grzanie)
Z wykresu h-X: odczytaj $h_Z, X_Z$ oraz $h_W, X_W$.  
$$\dot{Q}_{nagr} = \dot{m} \cdot (h_W - h_Z)$$
**Wynik:** $\dot{Q}_{nagr}$ = ______ kW

### Zadanie 8.2: Proces letni (chłodzenie + osuszanie)
$$\dot{Q}_{chłod} = \dot{m} \cdot (h_Z - h_{ch})$$
**Wynik:** $\dot{Q}_{chłod}$ = ______ kW

### Zadanie 8.3: Bilans centrali
Moc nagrzewnicy, chłodnicy, nawilżacza.  
**Wynik:** Zestawienie mocy [kW]

### Zadanie 8.4: Punkt rosy
Temp. ściany zewn. zimą: **{t_sciana}** °C. Czy dojdzie do kondensacji?  
$t_{rosy}$ (z wykresu h-X dla $X_W$) = ______ °C  
**Wynik:** Kondensacja: TAK / NIE

### Zadanie 8.5: Wymagany strumień powietrza
$$\dot{m} = \frac{Q_j}{c_p \cdot (t_W - t_N)}$$
Przyjmij $t_N$ = **{t_nawiew}** °C.  
**Wynik:** $\dot{m}$ = ______ kg/s, $\dot{V}$ = ______ m³/h

### Zadanie 8.6: Recyrkulacja powietrza
Proporcja: **{rec}**% recyrkulacja, reszta świeże.  
$$t_M = r \cdot t_W + (1-r) \cdot t_Z$$
$$X_M = r \cdot X_W + (1-r) \cdot X_Z$$
**Wynik:** $t_M$ = ______ °C, $X_M$ = ______ g/kg, Redukcja osuszania: ______ %

### Zadanie 8.7: Ilość skroplonej wody
$$\dot{m}_w = \dot{m} \cdot \Delta X$$
**Wynik:** $\dot{V}_w$ = ______ l/h

### Zadanie 8.8: Nagrzewnica zimowa
Podgrzanie od **{tz_zima}** °C do **{tw}** °C.  
**Wynik:** $\dot{Q}_{nagr}$ = ______ kW

---

## Zadanie Domowe (Raport 8)
Zaprojektuj rekuperator (sprawność 75%) i oblicz oszczędność mocy grzewczej.

---

### Parametry do randomizacji (Moodle Calculated)

| Zmienna | Min | Max | Krok |
|---------|-----|-----|------|
| `{tz_zima}` | -15 | -5 | 1 |
| `{phi_zima}` | 80 | 95 | 5 |
| `{tz_lato}` | 28 | 36 | 2 |
| `{phi_lato}` | 35 | 55 | 5 |
| `{tw}` | 20 | 24 | 1 |
| `{phi_w}` | 40 | 55 | 5 |
| `{V_dot}` | 15000 | 30000 | 5000 |
| `{Qj}` | 30 | 80 | 10 |
| `{W}` | 5 | 15 | 5 |
| `{t_sciana}` | 8 | 15 | 1 |
| `{t_nawiew}` | 14 | 18 | 1 |
| `{rec}` | 60 | 80 | 5 |
