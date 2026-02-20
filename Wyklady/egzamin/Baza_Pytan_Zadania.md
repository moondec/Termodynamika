# Baza Zadań Obliczeniowych (Egzamin Moodle)

Kategoria: `egzamin/zadania`. Punktacja: 3–5 pkt/zadanie.
Zmienne w `{nawiasach}` — pod przyszłą randomizację.

---

## Zadanie 1 — Ogrzewanie gazu przy stałej objętości
W zamkniętym zbiorniku o stałej objętości znajduje się **{m} kg** powietrza o temperaturze **{T1} °C**. Gaz ogrzano do temperatury **{T2} °C**. Ciepło właściwe powietrza przy stałej objętości wynosi $c_v$ = 0,718 kJ/(kg·K). Obliczyć ilość ciepła doprowadzonego do gazu.

*(Wskazówka: I Zasada dla układu zamkniętego przy V = const.)*

**Podaj $Q$ [kJ]:** `{ans_Q}`

---

## Zadanie 1b — Ogrzewanie metanu przy stałej objętości
W zamkniętym zbiorniku o stałej objętości znajduje się **{m} kg** metanu ($CH_4$, $c_v$ = 1,708 kJ/(kg·K)) o temperaturze **{T1} °C**. Gaz ogrzano do temperatury **{T2} °C**. Obliczyć ilość ciepła doprowadzonego do gazu.

*(Wskazówka: I Zasada dla układu zamkniętego przy V = const.)*

**Podaj $Q$ [kJ]:** `{ans_Q}`

---

## Zadanie 2 — Moc turbiny parowej
Przez turbinę przepływa para wodna ze strumieniem masy **{m_dot} kg/s**. Entalpia właściwa na wlocie wynosi **{h1} kJ/kg**, na wylocie **{h2} kJ/kg**. Prędkość pary na wlocie to **{c1} m/s**, na wylocie **{c2} m/s**. Turbina jest adiabatyczna. Obliczyć moc mechaniczną na wale turbiny.

[tu wstaw grafikę ilustrującą przekrój turbiny z oznaczonymi przekrojami 1 i 2]

*(Wskazówka: Równanie bilansu energii dla przepływu ustalonego z uwzględnieniem energii kinetycznej.)*

**Podaj $P$ [kW]:** `{ans_P}`

---

## Zadanie 2b — Moc sprężarki
Sprężarka adiabatyczna sprężą powietrze ze strumieniem masy **{m_dot} kg/s**. Entalpia właściwa na wlocie wynosi **{h1} kJ/kg**, na wylocie **{h2} kJ/kg**. Różnice energii kinetycznej pominąć. Obliczyć moc napędową sprężarki.

*(Wskazówka: Bilans energii przepływu ustalonego. Moc napędowa jest pobierana z zewnątrz.)*

**Podaj $P$ [kW]:** `{ans_P}`

---

## Zadanie 3 — Sprawność obiegu i straty ciepła
Siłownia parowa pracuje między temperaturą pary **{TH} °C** (kocioł) a temperaturą wody chłodzącej **{TL} °C** (skraplacz). Moc elektryczna bloku wynosi **{P_el} MW**, a jego sprawność rzeczywista stanowi **{eta_frac}** sprawności Carnota.

a) Obliczyć sprawność obiegu Carnota.
b) Obliczyć ilość ciepła odprowadzonego w skraplaczu w ciągu **{t_h} godzin** pracy.

[tu wstaw grafikę ilustrującą schemat obiegu siłowni parowej]

*(Wskazówka: Temperatury przeliczyć na kelwiny. Moc cieplna doprowadzona: $\dot{Q}_{dop} = P_{el}/\eta$.)*

**Podaj $Q_{odpr}$ [GJ]:** `{ans_Q_odpr}`

---

## Zadanie 3b — Sprawność elektrowni gazowej
Turbina gazowa pracuje w obiegu Braytona między temperaturą spalin **{TH} °C** a temperaturą powietrza na wlocie **{TL} °C**. Moc elektryczna wynosi **{P_el} MW**, a sprawność rzeczywista stanowi **{eta_frac}** sprawności Carnota.

a) Obliczyć sprawność Carnota.
b) Obliczyć strumień ciepła doprowadzonego w komorze spalania [MW].

*(Wskazówka: $\dot{Q}_{dop} = P_{el}/\eta_{rzecz}$.)*

**Podaj $\dot{Q}_{dop}$ [MW]:** `{ans_Q_dop}`

---

## Zadanie 4 — Przenikanie ciepła przez ścianę dwuwarstwową
Ściana składa się z dwóch warstw:
- beton o grubości **{d1} cm** i $\lambda_1$ = 1,30 W/(m·K),
- wełna mineralna o grubości **{d2} cm** i $\lambda_2$ = 0,035 W/(m·K).

Pominąć opory przejmowania ciepła na powierzchniach ($R_{si} = R_{se} = 0$). Obliczyć współczynnik przenikania ciepła $U$ przegrody.

[tu wstaw grafikę ilustrującą przekrój ściany z zaznaczonymi warstwami i analogią oporową]

*(Wskazówka: $U = 1 / \sum(\delta_i / \lambda_i)$.)*

**Podaj $U$ [W/(m²·K)]:** `{ans_U}`

---

## Zadanie 4b — Ściana trójwarstwowa
Ściana składa się z trzech warstw:
- tynk wewnętrzny o grubości **{d1} cm** i $\lambda_1$ = 0,70 W/(m·K),
- cegła o grubości **{d2} cm** i $\lambda_2$ = 0,77 W/(m·K),
- styropian o grubości **{d3} cm** i $\lambda_3$ = 0,040 W/(m·K).

Pominąć opory przejmowania. Obliczyć współczynnik przenikania ciepła $U$.

*(Wskazówka: Opory warstw dodaje się szeregowo.)*

**Podaj $U$ [W/(m²·K)]:** `{ans_U}`

---

## Zadanie 5 — Nawilżanie adiabatyczne powietrza
Powietrze o temperaturze **{t1} °C** i zawartości wilgoci **{X1} g/kg** wpływa do komory zraszania, gdzie jest nawilżane rozpyloną wodą. W wyniku odparowania wody temperatura powietrza spada o **{dt} K**. Obliczyć przyrost zawilżenia $\Delta X$.

[tu wstaw grafikę ilustrującą proces na wykresie h-X (Molliera)]

*(Wskazówka: Nawilżanie adiabatyczne przebiega przy $h$ = const. Zapisać $h_1 = h_2$ i wyznaczyć $X_2$.)*

**Podaj $\Delta X$ [g/kg]:** `{ans_dX}`

---

## Zadanie 5b — Ogrzewanie powietrza w nagrzewnicy
Powietrze wilgotne o temperaturze **{t1} °C**, wilgotności względnej **{phi1} %** i ciśnieniu barometrycznym 1013 hPa przepływa przez nagrzewnicę elektryczną, która podnosi jego temperaturę do **{t2} °C**. Obliczyć wilgotność względną powietrza na wylocie z nagrzewnicy.

*(Wskazówka: Ogrzewanie bez dodawania wody — zawartość wilgoci $X$ nie zmienia się. Zmienia się tylko $\varphi$, bo rośnie ciśnienie nasycenia $p_s(T)$.)*

**Podaj $\varphi_2$ [%]:** `{ans_phi2}`

---

## Zadanie 6 — Izentropowe sprężanie powietrza
**{m} kg** powietrza o temperaturze **{T1} °C** i ciśnieniu **{p1} bar** sprężono izentropowo do ciśnienia **{p2} bar**. Obliczyć temperaturę końcową gazu po sprężeniu. Przyjąć $\kappa$ = 1,40.

*(Wskazówka: Związek izentropa: $T_2/T_1 = (p_2/p_1)^{(\kappa-1)/\kappa}$. Temperatury w kelwinach.)*

**Podaj $T_2$ [°C]:** `{ans_T2}`

---

## Zadanie 7 — Chłodziarka (obieg lewobieżny)
Chłodziarka pracuje między temperaturą wnętrza **{TL} °C** a temperaturą otoczenia **{TH} °C**. Moc sprężarki wynosi **{P} kW**. Obliczyć maksymalny (Carnota) współczynnik wydajności chłodniczej COP oraz maksymalny strumień ciepła odbieranego z wnętrza.

*(Wskazówka: $COP_C = T_L / (T_H - T_L)$, temperatury w K. $\dot{Q}_L = COP \cdot P$.)*

**Podaj $\dot{Q}_L$ [kW]:** `{ans_QL}`

---

## Zadanie 8 — Rozprężanie izotermiczne gazu
W cylindrze z tłokiem znajduje się **{m} kg** powietrza o temperaturze **{T1} °C** i ciśnieniu **{p1} bar**. Gaz rozprężono izotermicznie do ciśnienia **{p2} bar**. Obliczyć pracę objętościową wykonaną przez gaz. Przyjąć $R$ = 287 J/(kg·K).

*(Wskazówka: $L = mRT \ln(p_1/p_2)$. Temperatura w kelwinach.)*

**Podaj $L$ [kJ]:** `{ans_L}`

---

## Zadanie 9 — Kocioł parowy (bilans energii)
W kotle parowym wytwarzane jest izobarycznie **{m_dot} t/h** pary wodnej przegrzanej o entalpii **{h2} kJ/kg**. Woda zasilająca kocioł ma temperaturę **{t_w} °C** (entalpia wody: $h_1 \approx c_w \cdot t_w$, gdzie $c_w$ = 4,19 kJ/(kg·K)). Obliczyć strumień ciepła, jaki powinien być doprowadzony do kotła.

*(Wskazówka: $\dot{Q} = \dot{m}(h_2 - h_1)$. Przelicz t/h na kg/s.)*

**Podaj $\dot{Q}$ [kW]:** `{ans_Q}`

---

## Zadanie 10 — Wymiennik ciepła (strumień ciepła)
W wymienniku przeciwprądowym woda jest ogrzewana od **{t1_z} °C** do **{t2_z} °C** strumieniem gorącej wody, która wchodzi z temperaturą **{t1_g} °C** i wychodzi z temperaturą **{t2_g} °C**. Współczynnik przenikania ciepła wymiennika wynosi $U$ = **{U_wym}** W/(m²·K), a powierzchnia wymiany **{A} m²**. Obliczyć strumień ciepła wymienianego w wymienniku.

[tu wstaw grafikę ilustrującą schemat wymiennika przeciwprądowego z oznaczonymi temperaturami]

*(Wskazówka: $\dot{Q} = U \cdot A \cdot \Delta T_{lm}$. Średnia logarytmiczna: $\Delta T_{lm} = (\Delta T_1 - \Delta T_2) / \ln(\Delta T_1 / \Delta T_2)$.)*

**Podaj $\dot{Q}$ [kW]:** `{ans_Q_wym}`

---

## Zadanie 10b — Wymiennik współprądowy
W wymienniku współprądowym olej jest chłodzony od **{t1_g} °C** do **{t2_g} °C** wodą wchodzącą z temperaturą **{t1_z} °C** i wychodzącą z temperaturą **{t2_z} °C**. Współczynnik przenikania ciepła wynosi $U$ = **{U_wym}** W/(m²·K), powierzchnia wymiany **{A} m²**. Obliczyć strumień ciepła wymienianego w wymienniku.

[tu wstaw grafikę ilustrującą schemat wymiennika współprądowego z oznaczonymi temperaturami]

*(Wskazówka: Dla wymiennika współprądowego $\Delta T_1 = T_{g,we} - T_{z,we}$, $\Delta T_2 = T_{g,wy} - T_{z,wy}$. Dalej: $\dot{Q} = U A \Delta T_{lm}$.)*

**Podaj $\dot{Q}$ [kW]:** `{ans_Q_wym}`

---

## Zadanie 11 — Sprawność klimatyzatora (pompa ciepła)
Klimatyzator pracujący w trybie grzania pobiera ciepło z powietrza zewnętrznego o temperaturze **{TL} °C** i oddaje je do pomieszczenia o temperaturze **{TH} °C**. Moc elektryczna sprężarki wynosi **{P} kW**, a rzeczywisty współczynnik COP urządzenia stanowi **{eta_frac}** wartości COP Carnota. Obliczyć strumień ciepła dostarczanego do pomieszczenia.

*(Wskazówka: $COP_{C,PC} = T_H / (T_H - T_L)$, temperatury w K. $\dot{Q}_H = COP_{rzecz} \cdot P$.)*

**Podaj $\dot{Q}_H$ [kW]:** `{ans_QH}`

---

## Zadanie 12 — Rekuperator powietrza (sprawność temperaturowa)
W rekuperatorze krzyżowym powietrze nawiewane (świeże) o temperaturze **{t_zew} °C** jest podgrzewane powietrzem wywiewanym (zużytym) o temperaturze **{t_wew} °C**. Sprawność temperaturowa rekuperatora wynosi **{eta_rek} %**. Obliczyć temperaturę powietrza nawiewanego po przejściu przez rekuperator.

*(Wskazówka: Sprawność temperaturowa: $\eta_t = (t_{naw,wy} - t_{naw,we}) / (t_{wyw,we} - t_{naw,we})$.)*

**Podaj $t_{naw,wy}$ [°C]:** `{ans_t_naw}`

---

## Zadanie 13 — Mieszanie strumieni powietrza wilgotnego
W centrali wentylacyjnej miesza się dwa strumienie powietrza:
- Strumień 1 (zewnętrzny): **{m1} kg/s**, temperatura **{t1} °C**, zawilżenie **{X1} g/kg**.
- Strumień 2 (obiegowy): **{m2} kg/s**, temperatura **{t2} °C**, zawilżenie **{X2} g/kg**.

Obliczyć temperaturę i zawilżenie powietrza po zmieszaniu.

[tu wstaw grafikę ilustrującą proces mieszania na wykresie h-X z regułą dźwigni]

*(Wskazówka: Reguła dźwigni: $t_M = (m_1 t_1 + m_2 t_2)/(m_1 + m_2)$, analogicznie dla $X_M$.)*

**Podaj $t_M$ [°C]:** `{ans_tM}`
**Podaj $X_M$ [g/kg]:** `{ans_XM}`
