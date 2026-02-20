---
output:
  pdf_document:
    latex_engine: xelatex
---

# Karta Wzorów — Termodynamika Techniczna

------------------------------------------------------------------------

## Tabela stałych

| Substancja | $\mu$ \[kg/kmol\] | $R$ \[J/(kg·K)\] | $c_p$ \[kJ/(kg·K)\] | $c_v$ \[kJ/(kg·K)\] | $\kappa$ |
|:-----------|:----------:|:----------:|:----------:|:----------:|:----------:|
| Powietrze | 28,96 | 287,0 | 1,005 | 0,718 | 1,40 |
| Para wodna | 18,01 | 461,5 | 1,860 | 1,399 | 1,33 |
| Azot $N_2$ | 28,01 | 296,8 | 1,039 | 0,743 | 1,40 |
| Tlen $O_2$ | 32,00 | 259,8 | 0,918 | 0,658 | 1,40 |
| $CO_2$ | 44,01 | 188,9 | 0,844 | 0,655 | 1,29 |
| Metan $CH_4$ | 16,04 | 518,3 | 2,226 | 1,708 | 1,30 |
| Woda (ciecz) | 18,01 | — | 4,19 | — | — |

Stała uniwersalna: $MR$ = 8314 J/(kmol·K). Stała Stefana-Boltzmanna: $\sigma$ = 5,67·10⁻⁸ W/(m²·K⁴).

------------------------------------------------------------------------

## Równanie stanu gazu doskonałego

$$pV = mRT, \quad R = \frac{MR}{\mu}, \quad c_p - c_v = R, \quad \kappa = \frac{c_p}{c_v}$$

## I Zasada Termodynamiki

-   Układ zamknięty: $Q_{1-2} = \Delta U + L_{1-2}$
-   Układ otwarty (przepływ ustalony): $Q_{1-2} = \Delta H + L_t$
-   Praca objętościowa: $L = \int p \, dV$, praca techniczna: $L_t = -\int V \, dp$
-   Bilans turbiny/sprężarki (adiabat., przepływ ustalony): $P = \dot{m}\left[(h_1 - h_2) + \frac{\omega_1^2 - \omega_2^2}{2}\right]$
-   Bilans kotła/wymiennika: $\dot{Q} = \dot{m}(h_{wy} - h_{we})$

## Przemiany gazu doskonałego ($pv^n = \text{const}$)

| Przemiana |   $n$    | Warunek            | Ciepło                    |
|:----------|:--------:|:-------------------|:--------------------------|
| Izobara   |    0     | $p = \text{const}$ | $Q = mc_p \Delta T$       |
| Izoterma  |    1     | $T = \text{const}$ | $Q = L = mRT\ln(V_2/V_1)$ |
| Izentropa | $\kappa$ | $S = \text{const}$ | $Q = 0$                   |
| Izochora  | $\infty$ | $V = \text{const}$ | $Q = mc_v \Delta T$       |

Związek izentropa: $\frac{T_2}{T_1} = \left(\frac{p_2}{p_1}\right)^{(\kappa-1)/\kappa}$

## Sprawności obiegów

-   Sprawność termiczna: $\eta = 1 - \frac{|Q_{odpr}|}{Q_{dop}}$
-   Obieg Carnota: $\eta_C = 1 - \frac{T_L}{T_H}$ (temperatury w K)
-   COP chłodziarki: $COP_{ch} = \frac{T_L}{T_H - T_L}$, COP pompy ciepła: $COP_{PC} = \frac{T_H}{T_H - T_L} = COP_{ch} + 1$
-   Związek moc — ciepło: $\dot{Q}_{dop} = P/\eta$, $\dot{Q}_{odpr} = \dot{Q}_{dop} - P$

## Para wodna

-   Stopień suchości: $x = m''/(m'+m'')$
-   Entalpia pary mokrej: $h_x = h' + x \cdot r$, gdzie $r = h'' - h'$

### Tablica entalpii pary wodnej nasyconej

| $p$ [bar] | $t_s$ [°C] | $h'$ [kJ/kg] | $h''$ [kJ/kg] | $r$ [kJ/kg] |
|:---:|:---:|:---:|:---:|:---:|
| 1 | 99,6 | 417 | 2675 | 2258 |
| 2 | 120,2 | 505 | 2707 | 2202 |
| 4 | 143,6 | 605 | 2738 | 2133 |
| 6 | 158,8 | 670 | 2757 | 2087 |
| 8 | 170,4 | 721 | 2769 | 2048 |
| 10 | 179,9 | 763 | 2778 | 2015 |
| 15 | 198,3 | 845 | 2792 | 1947 |
| 20 | 212,4 | 909 | 2799 | 1890 |
| 30 | 233,8 | 1008 | 2803 | 1795 |
| 40 | 250,3 | 1087 | 2801 | 1714 |

### Entalpia pary przegrzanej [kJ/kg]

| $p$ [bar] | 200 °C | 250 °C | 300 °C | 350 °C | 400 °C | 500 °C |
|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 1 | 2875 | 2974 | 3074 | 3175 | 3278 | 3488 |
| 4 | 2861 | 2964 | 3067 | 3170 | 3273 | 3484 |
| 8 | 2839 | 2950 | 3057 | 3162 | 3268 | 3481 |
| 15 | — | 2924 | 3038 | 3148 | 3257 | 3474 |
| 20 | — | 2903 | 3024 | 3138 | 3248 | 3468 |
| 30 | — | — | 2994 | 3116 | 3231 | 3457 |
| 40 | — | — | 2961 | 3093 | 3214 | 3446 |

*„—" oznacza, że para nie istnieje przy tych parametrach (poniżej temperatury nasycenia).*

## Wymiana ciepła

-   Przewodzenie (Fourier): $\dot{Q} = \lambda A \, \Delta T / \delta$
-   Konwekcja (Newton): $\dot{Q} = \alpha A (T_s - T_\infty)$
-   Współczynnik przenikania: $U = \frac{1}{\frac{1}{\alpha_w} + \sum\frac{\delta_i}{\lambda_i} + \frac{1}{\alpha_z}}$
-   Wymiennik ciepła: $\dot{Q} = U \cdot A \cdot \Delta T_{lm}$, gdzie $\Delta T_{lm} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1 / \Delta T_2)}$
-   Promieniowanie: $\dot{Q} = \varepsilon \sigma A T^4$

## Powietrze wilgotne

-   Zawilżenie: $X = 622 \cdot \frac{p_w}{p_B - p_w}$ \[g/kg\]
-   Wilgotność względna: $\varphi = p_w / p_s(T)$
-   Entalpia: $h \approx 1{,}005\,t + X(2{,}5 + 0{,}00186\,t)$ \[kJ/kg\]
-   Mieszanie: $X_M = (m_1 X_1 + m_2 X_2)/(m_1 + m_2)$, analogicznie $t_M$
-   Sprawność rekuperatora: $\eta_t = (t_{naw,wy} - t_{naw,we}) / (t_{wyw,we} - t_{naw,we})$
