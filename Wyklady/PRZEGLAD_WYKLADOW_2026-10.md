# Przegląd merytoryczny wykładów — październik 2026

Przegląd plików `Wyklady/01–15_*.qmd` (źródła prezentacji Quarto). Przykłady liczbowe przeliczone
w CoolProp (venv `termo`), wyrenderowane wykresy i HTML sprawdzone tam, gdzie to miało znaczenie.
Numery linii odnoszą się do plików `.qmd` w stanie z 2.10.2026. Pozycje oznaczone *(do weryfikacji)*
wymagają potwierdzenia u źródła (głównie przepisy i normy).

Legenda: **[W]** wysoka waga · **[Ś]** średnia · **[N]** niska.


## Stan realizacji (2.10.2026)

Wprowadzono wszystkie pozycje z sekcji A, B i C (zaznaczone [x]); wszystkie 15 wykładów wyrenderowano do HTML,
zmienione wykresy sprawdzono wizualnie. Nic nie zostało zatwierdzone w git.

- **Pozostawione do decyzji:** W15 — lista zagadnień egzaminacyjnych bez spalania i egzergii.
- **Zweryfikowane u źródła:** GWP w rozporządzeniu (UE) 2024/573 — HFC wg IPCC AR4 (1430/675/2088 bez zmian), HFO wg AR6
  (R1234yf: < 1 zamiast 4; dodano przypis); warunki EER wg PN-EN 14511 (35 °C zewn. / 27 °C wewn.), SEER wg PN-EN 14825.
  Udział siłowni parowych w W10 („ok. 55–60%”) — węgiel + atom + bioenergia ≈ 47% wg Ember (Global Electricity Review 2024),
  resztę (część parowa bloków gazowo-parowych) oszacowano.
- **Nie zmieniono (sprawdzone):** W9 — powtórzony rysunek turbina.png mieści się na slajdzie.
- **Separator dziesiętny (C.7):** przecinek w tekście i wzorach; w etykietach osi generowanych przez R zwykle pozostała kropka
  (w W5 i W8 ustawiono `options(OutDec = ",")`).
- **Poprawione dodatkowo (spoza listy):** W12 — rekuperacja podana jako przykład mieszania strumieni; nakładające się etykiety
  i niewidoczne etykiety „h = const” na wykresach h-X; W9 — ucinane numery punktów na 8 wykresach obiegów; W11 — nowe
  slajdy 6f (harmonogram F-gazów) i „Zagadnienia do egzaminu” (żeby nie skracać treści); W13 — zadanie domowe przeliczone
  (nawilżacz wodny, X_P = 7 g/kg: ṁ_w ≈ 6,0 kg/h, Q̇_n ≈ 12,6 kW).

---

## A. Najważniejsze (do poprawy przed semestrem)

- [x] **W3:113–315 — konwencja znaku pracy technicznej.** Bilans układu otwartego `Q̇ + L̇_t = ṁ[Δh + …]` (l. 240)
      odpowiada konwencji „praca doprowadzona > 0”, a kurs (W2: ΔU = Q − L; W3 l. 156–157, 300) przyjmuje „praca
      wykonana przez układ > 0”. Konsekwencje: wzór na l_t sprężarki (l. 315) daje wynik dodatni, choć z definicji
      đL_t = −V dp powinien być ujemny; pompa (l. 301) `l_t = vΔp` → `l_t = −vΔp`; „N < 0” i „P_d > 0” na jednym
      slajdzie (l. 300, 304). Proponowany bilans: `Q̇ − L̇_t = ṁ[(h₂−h₁) + (w₂²−w₁²)/2 + g(z₂−z₁)]`.
      *Karta projektowa (Zad. 2.1, 2.4) i ćwiczenie 2 stosują już tę konwencję.*
- [x] **W8:114, 120 — I zasada z odwrotnym znakiem.** `dU = đQ + đL` (praca „na układzie”) — sprzeczne z resztą W8
      (l. 128, 139, 172) i z W2. → `dU = đQ − đL`, đL — praca wykonana **przez** układ.
- [x] **W8:441, 586, 649 — znak pracy technicznej adiabaty.** `l_t = κ·l = Δh` → poprawnie `l_t = κ·l = −Δh = c_p(T₁−T₂)`
      (z q = Δh + l_t = 0). Tabela (l. 648): izoterma `l = −q` → `l = q`, `l_t = l = q`. Slajdy 350–351 (`l = −RT ln(v₂/v₁)`,
      `q = −l`) sprzeczne z l. 361 i 374–375 → `l = RT ln(v₂/v₁)`, `q = l`.
- [x] **W9:408–411 — stopień obciążenia (Diesel).** `φ = V₄/V₃ = T₄/T₃` jest błędne; poprawnie `φ = V₃/V₂ = T₃/T₂`
      (w l. 408 dodatkowo ρ zamiast φ).
- [x] **W10:149 — opis niewykonalności obiegu Carnota dla pary jest opisem Rankine'a.** Problemem Carnota jest sprężanie
      **pary mokrej** (niepełne skraplanie, pkt 3′→4′), a nie cieczy nasyconej. Sprzeczne z l. 1167–1171.
- [x] **W11:375, 607, 687 — daty F-gazowe** (trzy różne: 2030, 2032–35, 2035). Rozporządzenie (UE) 2024/573: wycofanie
      HFC z rynku do 2050 r.; zakazy dla małych klimatyzatorów/pomp ciepła od 2032 (monobloki) i 2035 (split).
      Także l. 515/482: R410A „zakaz od 2025” dotyczy tylko nowych single-split < 3 kg; R22 (l. 365, 397) jest w UE
      **zakazany** (od 2015), nie „wycofywany”.
- [x] **W11:278–283 — wykres „Rzeczywisty obieg Lindego”: h₂ = 435 kJ/kg** daje η_is = 1,34 (izentropowo h₂s = 445,3).
      → h₂ ≈ 455 kJ/kg.
- [x] **W12:1082 i 994 — punkty końcowe nawilżania adiabatycznego i suszarni leżą we mgle** (φ = 123% i 115%) i poza
      narysowaną izentalpą. → `p2 <- list(x = 14.8, t = 23)`, `pB <- list(x = 20.8, t = 28)`.
- [x] **W12:760 — tabela ε: „chłodzenie z osuszaniem: ε < 0 (−1000)”.** Przy Δh < 0 i ΔX < 0 jest ε > 0 (duże, rzędu
      5000–15 000 kJ/kg). Lód: ε ≈ −335 kJ/kg (nie −1000). Rozbić na dwa wiersze.
- [x] **W15:219–245 — „Prawo Gouy–Stodoli” zilustrowane bilansem ENERGII** (skraplacz 50%). W bilansie egzergii główna
      destrukcja zachodzi w kotle (~45–50%), skraplacz to kilka %. Zmienić tytuł na „Bilans energii elektrowni
      (I zasada)” albo dodać rozkład strat egzergii i poprawić wniosek o CHP.
- [x] **W14:121–125, 192–196 — listy renderują się jako blok kodu** (wcięcie 4 spacji; potwierdzone w HTML).

---

## B. Przegląd wykładów

### W1 — Wprowadzenie
- [x] [Ś] l. 458 — równowaga chemiczna `u1 = u2` → `μ1 = μ2` (potencjał chemiczny).
- [x] [Ś] l. 540–549 — proces kwazistatyczny ≠ odwracalny (np. powolne sprężanie z tarciem); obiegi podane jako „przykłady procesów”.
- [x] [Ś] l. 952 — podtytuł „Niestabilne stany równowagi” na slajdzie o stanach **metastabilnych** → „Metastabilne (nietrwałe)”.
- [x] [N] l. 818, 834 — `pV/RT`, van der Waals z R (stała uniwersalna) i V (molowa); w W2–W4 R to stała indywidualna → `pV_m = R_u T`.
- [x] [N] l. 655, 666 — v jako prędkość cząsteczek koliduje z v = objętość właściwa (l. 558) → np. `\overline{w^2}`.
- [x] [N] l. 681 — `p = dF/dA` → składowa normalna `dF_n/dA`.
- [x] [N] l. 767 — `Δp = ρ_{cieczy} g h`, na rysunku Δh; słowo w trybie math.
- [x] [N] l. 599 — `E_{u1} − E_{u2}` → `U_1 − U_2`.
- [x] [N] l. 625 — KMh nie jest jednostką legalną w UE → do „jednostek dawnych”.
- [x] [N] l. 840 — b = kowolumen (ok. 4× objętość własna cząsteczek), nie „objętość własna”.
- [x] [N] l. 162 — Ω bez definicji (liczba mikrostanów).
- [x] [N] l. 977 — „woda (posiadająca punkt potrójny)” — cechą szczególną jest ujemne nachylenie krzywej topnienia; lista sklejona z akapitem.
- [x] [N] l. 148, 157 — słowa w trybie math (`$fenomenologiczna$`) → kursywa markdown.
- [x] [N] l. 586 — widoczne „***” po obrazku.
- [x] [N] l. 222/262, 291–292, 407–408, 422–423 — podpis „(rozprężanie gazu)” przy izochorze; osie „[V]”, „[p]”; etykieta „Pole = Praca” nachodzi na krzywą.
- [x] [N] separator dziesiętny raz kropka, raz przecinek (l. 637, 994–996 vs 624, 641).

### W2 — I zasada, bilans
- [x] [Ś] l. 461 — tytuł „Entalpia (E) a Energia Wewnętrzna (U)” → H; slajd dotyczy izochory (Q = ΔU).
- [x] [Ś] l. 366 — `ΔU = m c_v (T₂−T₁)` bez zastrzeżenia (tylko gaz doskonały, c_v = const).
- [x] [Ś] l. 124 — `dS = đQ/T` → `dS = đQ_{odwr}/T`.
- [x] [N] l. 102 — U nie obejmuje makroskopowej energii kinetycznej/potencjalnej.
- [x] [N] l. 417 — praca przetłaczania: p to ciśnienie czynnika w przekroju, nie otoczenia.
- [x] [N] l. 120 — forma Pfaffa może być zupełna („różniczka niezupełna đ”).
- [x] [N] l. 456 — kocioł (układ otwarty) uzasadniony bilansem układu zamkniętego → odsyłacz do W3.
- [x] [N] l. 426 — „(większe v)” przy H = U + pV → V. l. 386 — tytuł książki w trybie math.
- [x] [N] literówki: l. 459 „obiętości”; l. 513 „Wzory … ma”.

### W3 — I zasada, układy otwarte
- [x] [W] konwencja znaków — patrz **A**.
- [x] [W] l. 376, 394–409 — wykres krzywej inwersji J-T: kolory odwrotne niż w tekście, `geom_line` sortuje po p → „plama”.
      → `geom_path(...)`, krzywa czerwona przerywana, izentalpy niebieskie.
- [x] [Ś] l. 318, 320 — „n = κ → adiabata”, „rzeczywista sprężarka 1 < n < κ” → n = κ to izentropa; sprężarka niechłodzona z tarciem ma n > κ.
- [x] [Ś] l. 319 — „n = 1 → izoterma” — wzór dzieli przez zero; dopisać `l_t = R T₁ ln(p₂/p₁)`.
- [x] [Ś] l. 267 — prędkość w „[J/kg]” → [m/s].
- [x] [Ś] l. 368 — samozapłon wodoru wskutek efektu J-T (CoolProp: z 700 bar ogrzanie o ok. 31 K; T_samozapłonu ≈ 858 K) → złagodzić.
- [x] [N] l. 156–157 — đL zamiast đL_t; l. 166 — L_n, L_w bez definicji; l. 204, 329 — „praca tłoczenia”/„L_tech” vs „przetłaczania”/L_t.
- [x] [N] l. 436 — definicja wartości opałowej z dopiskiem o korozji (to nie część definicji).
- [x] [N] l. 491 — strata egzergii: `δB = T_ot ΔS_iz` (Gouy–Stodola).
- [x] [N] l. 212–223 — diagram: widoczna kropka, strzałki przez blok energii potencjalnej, m1/m2.
- [x] [N] l. 140, 143 — etykieta nachodzi na krzywą; v vs V. l. 480 — `3-4` w trybie math (minus).

### W4 — Właściwości substancji I
- [x] [Ś] l. 224–228, 244–252, 385–387, 619 — ciepła właściwe na kg pisane wielką literą C, a tabela (l. 268–275) mówi, że C to wielkości całkowite → `c_v, c_p`.
- [x] [Ś] l. 290, 309–310 — `pV = (2/3)U` prawdziwe tylko dla gazu jednoatomowego → `(2/3)E_{k,post}`.
- [x] [Ś] l. 148 — „tracą energię przy zderzeniach nieidealnych” — fałsz (energia zachowana).
- [x] [Ś] l. 527–553 — rysunek Andrewsa: złe v_l, v_g dla T_r = 0,90 („ząb” izotermy), kopuła z `smooth.spline` ponad punktem krytycznym. Punkty binodalne (VdW, Maxwell) podane w raporcie: T_r = 0,85: p = 0,5045, v_l = 0,553, v_g = 3,128; T_r = 0,90: p = 0,647, v_l = 0,603, v_g = 2,349.
- [x] [Ś] l. 90 — w HTML widoczny tekst „{.fragment}”.
- [x] [N] l. 73 — agenda „wykładnik k” (slajd l. 368 zaleca κ). l. 286, 310 — „pV = potencjalna praca” → wymiar energii (praca przetłaczania).
- [x] [N] l. 370 — `k = R_u/N_A` przy R_u w J/(kmol·K) → N_A w kmol⁻¹.
- [x] [N] l. 385–387 — `Δu = c_v ΔT` „zawsze” → przy stałych/średnich ciepłach właściwych. l. 399 — brak wzoru na R_miesz.
- [x] [N] l. 582 — „błąd rzędu 100%” → setki procent, dla cieczy rzędy wielkości.
- [x] [N] l. 190 vs 271 — RM vs MR; l. 409, 446 — `p_{calk}` bez „ł”; obraz substancja_vs_mieszanina.png — angielska legenda zdublowana.
- [x] [N] literówki: l. 129 „Abstarakcja”; l. 170 „Wiązanie między”; l. 356, 362, 457; separator dziesiętny.

### W5 — Właściwości substancji II
- [x] [Ś] l. 743 — `h ≈ c_p T` dla pary z tablic (300 °C: 3075 vs ~1150 kJ/kg) → `Δh ≈ c_p ΔT`.
- [x] [Ś] l. 578 vs 680 — „x = 0,8 typowa para wylotowa” vs „x < 0,85 → erozja” → x = 0,9.
- [x] [Ś] l. 129 — łyżwy ślizgają się dzięki obniżeniu T_top pod naciskiem (mit; −2 K wymaga ok. 270 bar).
- [x] [Ś] l. 212–233 — slajd „4. Tablice pary wodnej” przed sekcjami 2 i 3; „Para przegrzana” bez numeru.
- [x] [N] l. 650, 654 — pionowa jest tylko adiabata **odwracalna**. l. 247 — „cała energia na rozerwanie wiązań” (ok. 7,5% to praca p·Δv).
- [x] [N] l. 106–113 — Q_r vs r; l. 109–110, 122 — v′/v″ dla topnienia; l. 121 — „unikalna cecha” wody (Bi, Ga, Si, Ge też); „ó” w math.
- [x] [N] l. 232 — `v ≈ v′(T)` (dla tej samej temperatury); ciecz sprężona vs dochłodzona. l. 613 — „1600 razy” → ok. 1620.
- [x] [N] l. 701 — „ln(p)” → skala logarytmiczna p. l. 160, 166 — krzywa topnienia ekstrapolowana do 1 GPa (lód Ih do ~210 MPa).
- [x] [N] l. 541 — „100 atm” → 100 bar *(izobara przegrzana przybliżona, do weryfikacji wizualnej)*. l. 197, 606, 675–682 — drobne techniczne.
- [x] [uwaga] l. 669: przykład 100 bar/500 °C → 0,1 bar daje x₂s = 0,79 < 0,85 (gałąź „erozja”) — warto to skomentować.

### W6 — II zasada I
- [x] [Ś] l. 524 — nieodwracalność ≠ „cofnięcie wymaga pracy”; trwałe zmiany w otoczeniu.
- [x] [Ś] l. 250, 273, 275 — W_net/W vs L w reszcie wykładu.
- [x] [N] l. 344 — chłodziarka nie musi „zużywać prądu” (absorpcyjna). l. 562, 571–572 — warunki odwracalności wewn./zewn.; P vs p.
- [x] [N] l. 109 — zdanie urwane. l. 352–359 — pokazano tylko jeden kierunek równoważności K-P ⇔ Clausius. l. 753 — 20 °C ≈ 293 K, nie 300 K.
- [x] [N] l. 614 — legenda oznaczeń do rysunku Szarguta (T_I, q_d…). l. 381, 617 — tekst w trybie math.
- [x] [N] literówki: l. 107, 359 „możnaby”, 553 „satałych”, 577 „idelizacja”, 678, 796 „Jednostka Kelvina”.

### W7 — II zasada II
- [x] [W] l. 381 — „stała w odwracalnych (izentropowych)” — odwracalny ≠ izentropowy; chodzi o układ izolowany / S_gen.
- [x] [Ś] l. 329–331 — na wykresie T-s pole wewnątrz obiegu opisane „Q_rev” → praca obiegu (Q_H − Q_L).
- [x] [N] l. 365–367, 385 — sformułowanie III zasady to Planck (na podstawie twierdzenia Nernsta).
- [x] [N] l. 213 — izolowany ≠ adiabatyczny. l. 115 — ∮ vs ∫₁². l. 233–237 — bilans entropii „dla dowolnego procesu” → dla układu zamkniętego; „ł” w math.
- [x] [N] l. 146–153, 189, 192 — zbiorniki T = const; `dS` → `ΔS`. l. 250–252 — C vs c.
- [x] [N] l. 95–98 (mermaid) — brak polskich znaków; l. 388 „Ubrojeni”.

### W8 — Przemiany gazowe
- [x] [W] znaki pracy — patrz **A**.
- [x] [Ś] l. 287 — `Q = n c_p ΔT` → `m c_p ΔT` (lub n·(Mc_p)).
- [x] [N] l. 148, 151 — R vs R_u. l. 389, 453 — zacieniowane „pole pracy” to prostokąt, nie pole pod krzywą.
- [x] [N] l. 131 — konwencję wprowadza W2, nie W3. l. 361 „wykonana w układzie”. l. 610 vs 637 — próg sprężu dla 2 stopni (4 vs 8). l. 636 — k jako liczba stopni.
- [x] [N] techniczne: l. 177 `title="**Wniosek:**"` na divie (tytuł niewidoczny); l. 198, 267 `.fade-rigth`; l. 627 `.callout-success` (nie istnieje w Quarto); l. 618, 621 `p_{pośr}`.
- [x] [N] l. 149–150, 344 „Boyle-Mariotte”, 409 `dq`.

### W9 — Obiegi gazowe
- [x] [W] stopień obciążenia — patrz **A**.
- [x] [Ś] l. 682 — „w Dieslu sprężanie to kilka %” (ok. 35% pracy rozprężania) → chodzi o pompę w siłowni parowej.
- [x] [Ś] l. 675 — „w przeciwieństwie do Diesla … nie ograniczeni stukiem” → w przeciwieństwie do Otto.
- [x] [Ś] l. 688–699 — tytuł „ciśnienie średnie indykowane (p_me)”, wartości to użyteczne (BMEP).
- [x] [Ś] l. 669 — „zależy od π, a nie ε” — wielkości równoważne (π^((κ−1)/κ) = ε^(κ−1)).
- [x] [N] l. 284 — stuk ≠ zapłon przed iskrą. l. 563 — „O − wtryskiwacz” (na rysunku W). l. 645 — zdublowany turbina.png *(do weryfikacji)*.
- [x] [N] zakresy w trybie math (l. 146–147, 675–676, 698–699); l. 680 `title=` na divie; l. 630 p-V vs p-v; l. 90 agenda.
- [x] [N] literówki: l. 104 „źrodła”, 514 „obiętości”, 566 „Odbiornik macy”, 564, 706.

### W10 — Obiegi parowe
- [x] [W] l. 149 — patrz **A**.
- [x] [Ś] l. 1106–1109 — rysunek regeneracji: punkt 4 w złym miejscu; odcinek 408→537 K to ekonomizer, nie regeneracja.
- [x] [Ś] l. 426, 428 — wykres „rzeczywisty” (η = 0,85), a lista mówi „izentropowe”.
- [x] [Ś] l. 637–673 — nagła zmiana numeracji stanów (1/2s zamiast 3/4s).
- [x] [Ś] l. 100 — „>70% elektryczności z siłowni parowych” — nieaktualne (ok. 55–60%, Ember 2023).
- [x] [Ś] l. 176 — „para wylotowa” → para świeża (wylot z kotła).
- [x] [N] l. 874, 784–794 — x₄ vs x₄′: 0,92 vs 0,81 (nie 0,94); punkty 3a, 3b, 4 na rysunku (CoolProp w raporcie).
- [x] [N] l. 893 — regeneracja: „sprawność rośnie drastycznie” → o kilka pkt proc.; l. 884 — 30 °C vs 0,1 bar (45,8 °C).
- [x] [N] l. 168 — Rankine to modyfikacja, nie realizacja Carnota. l. 111 — mała praca pompy wynika z małego v. l. 93 — IGCC nieomawiany.
- [x] [N] χ vs x; indeksy słowne w math (l. 434), zakres w math (l. 667), CSS (l. 1141, *do weryfikacji*).
- [x] [N] literówki/terminy: „Odzysknicowy”, „3-Kondensator” → skraplacz, angielskie etykiety (l. 841–848).

### W11 — Chłodnictwo
- [x] [W] F-gazy, wykres p-h — patrz **A**.
- [x] [Ś] l. 684 — „pole parowania to moc chłodnicza” → długość odcinka h₁−h₄ = q_L; Q̇_L = ṁ q_L.
- [x] [Ś] l. 673 — callout z całym zdaniem w tytule i pustą treścią (sprawdzone w HTML).
- [x] [Ś] l. 125 — „EER w warunkach t_o = 2 °C, t_k = 40 °C” → PN-EN 14511 (temperatury nośników) *(do weryfikacji)*.
- [x] [Ś] l. 564, 545 — R290 „COP o 10–15% wyższy”, „wymaga monobloku” → porównywalny / do ~10% vs R410A; zwykle monoblok *(obliczenia w raporcie)*.
- [x] [N] GWP wg AR4 (1430/675/2088) przy cytowaniu 2024/573 — dopisać „wg AR4” *(do weryfikacji, czy załącznik podaje AR6)*; l. 439 „>675” → „≥675”.
- [x] [N] l. 567 LPG ≠ propan; l. 218 „niska jakość” pary; l. 163 izentropowe; l. 206 element dławiący; l. 230 oś log p.
- [x] [N] agenda 6a–6c vs 6a–6e; `T_{otoczenia}`, `$CO_2$`.
- [x] [N] brak polskich znaków: l. 467/473, 488, 489, 590–597 (mermaid), „EU” → „UE”, „C.P.”, „(High Res)”.

### W12 — Powietrze wilgotne
- [x] [W] l. 1082, 994, 760 — patrz **A**.
- [x] [Ś] l. 762–763, 867 — h_w pary 100 °C ≈ 2676 kJ/kg (nie 2500); „para przegrzana np. 4500” (≈ 940 °C) → 2800–3000; próg kierunku ε > 2501 + 1,86t.
- [x] [Ś] l. 175 — `$varphi = 100%$` renderuje się jako „varphi = 100” → `$\varphi = 100\%$`.
- [x] [Ś] l. 143 — wzór na h z T (w l. 113 T = kelwiny) → t w °C.
- [x] [Ś] l. 178, 776 — „linie/skala Randa” → podziałka brzegowa (Randmaßstab).
- [x] [Ś] l. 1239–1241, 1234–1235 — listy sklejone z akapitem (HTML).
- [x] [Ś] l. 1250, 99 — X nazwane „wilgotnością bezwzględną” (w l. 111–113 to g); „dwóch definicji” → trzech wielkości.
- [x] [N] l. 755 — ε = h_w tylko bez dopływu ciepła. l. 520 vs 712 — „Suszenie (h = const)” vs nawilżanie adiabatyczne; dublująca się numeracja.
- [x] [N] l. 977 — „sprawność ~ (X_B − X_0)” → odparowana woda / jednostkowe zużycie powietrza. l. 651 — koniec strzałki za φ = 100%.
- [x] [N] l. 161 — oś pionowa vs ukośna h. l. 107 — punkt rosy to temperatura. l. 787/794/1215 — oznaczenia strumieni, brak bilansu powietrza suchego.
- [x] [N] literówki: „Assmana”, „obwiązują”, „Stopień zwilżenia”, „Bilansy”.

### W13 — Klimatyzacja
- [x] [Ś] l. 217 — nawilżanie parą prawie izotermiczne nie dlatego, że para gorąca, lecz bo h_p ≈ nachylenie izotermy (2501 + 1,86t).
- [x] [Ś] l. 473–478 — listy w zadaniu domowym sklejone z akapitem (HTML).
- [x] [Ś] l. 469–479 — zadanie domowe niedookreślone (typ nawilżacza: 15,2 kW wodny vs 8,4 kW parowy); x_P = 10 g/kg → φ = 68% (poza komfortem).
- [x] [Ś] l. 463 vs 447, 451 — punkt S vs P.
- [x] [N] l. 381–385 — regenerator ≠ rekuperator. l. 431 — `ε = ΔH/Δx` → Δh/Δx. l. 125 vs 133 — oś rzędnych to entalpia; podpis bitmapy „i-X”.
- [x] [N] l. 140 — „wilgotność bezwzględna” → stopień zawilżenia x. l. 183 — przebieg teoretyczny. l. 254 — powietrze świeże wynika z CO₂, nie z tlenu. l. 461.
- [x] [N] niespójności oznaczeń W12/W13: t_w/t_m, t_R/t_r, x/X, ṁ_{s.p.}/ṁ_g, izoentalpa/izentalpa, g.
- [x] [N] l. 139–141, 239–241 — dwie linie zlewają się w jedną; literówki l. 86, 205, 127.

### W14 — Wymiana ciepła
- [x] [W] listy jako blok kodu — patrz **A**.
- [x] [Ś] l. 140 vs 153, 359 — R = δ/(λA) [K/W] vs R = δ/λ [m²K/W].
- [x] [Ś/N] l. 299–300 — profile temperatur przeciwprądu bilansowo niemożliwe (różna krzywizna); wygenerować z ε-NTU.
- [x] [N] l. 220 — „każde ciało emituje światło” → promieniowanie cieplne (T > 0 K). l. 234 — warunek „małe ciało w dużym otoczeniu”; σ bez jednostki.
- [x] [N] l. 333 — radiator intensyfikuje konwekcję. l. 204, 171 — indeksy z polskimi literami. l. 349–352 — „Dane” sklejone. l. 61–67 agenda.

### W15 — Spalanie i egzergia
- [x] [W] l. 219–245 — patrz **A**.
- [x] [Ś] l. 152, 181 — trzy symbole wartości opałowej (W_d, W_o, LHV) i dwa ciepła spalania (C_s, HHV); r, m_H₂O niezdefiniowane → `W_d = W_g − r(9h + w)`.
- [x] [N] l. 197–198 — definicja egzergii. l. 214 — δB vs ΔS. l. 106–108 — brak SO₂, O₂ w spalinach; L₀ bez definicji.
- [x] [N] l. 269–271 — „60 MJ straty (do rzeki)” vs komin + skraplacz. l. 90–93 — trójkąt Gibbsa ≠ trójkąt spalania.
- [x] [N] l. 145–147, 185 — λ = 1 to spalanie teoretyczne; nadmiar powietrza (nie tlenu); kocioł kondensacyjny vs HHV.
- [x] [N] l. 392, 421 — numeracja „6. Podsumowanie” (agenda: 8).
- [ ] [N] l. 428–437 — lista zagadnień egzaminacyjnych bez spalania/egzergii — **do decyzji prowadzącego** (nie zmieniano).
- [x] [N] l. 432 „Sabathe” → „Sabathé”; l. 181 `m_{H2O}`.

---

## C. Problemy przekrojowe (warto ujednolicić w całym kursie)

1. **Konwencja znaku pracy** — W2 (ΔU = Q − L) ✔, W3 (bilans otwarty) ✘, W8 (dU = đQ + đL, adiabata, izoterma) ✘. Jedna konwencja: praca wykonana przez układ > 0, `đL_t = −V dp`.
2. **Ciepła właściwe** — małe c na kg, wielkie C całkowite (W4, W7 mieszają).
3. **Stała gazowa** — R (indywidualna) vs R_u (uniwersalna) — W1, W8.
4. **Polskie litery i słowa w indeksach w trybie matematycznym** (np. `p_{calk}`, `T_{otoczenia}`, `\Delta S_{ukladu}`) — znikają lub składają się kursywą. → `\text{…}`.
5. **Listy bez pustej linii przed nimi** — sklejają się z akapitem (W1, W12, W13, W14, także karta projektowa — już poprawiona).
6. **Zakresy liczb w trybie math** (`3-4`, `0.75 - 0.90`) renderują się jako odejmowanie → `3\text{–}4`.
7. **Separator dziesiętny** — kropka/przecinek mieszane w obrębie wykładów.
8. **Konstrukcje Quarto niedziałające**: `title="…"` na zwykłym divie, `.callout-success`, `.fade-rigth`, `{.fragment}` jako tekst.
