#!/usr/bin/env Rscript
# ============================================================================
# generuj_imienne.R — Generowanie imiennych kart projektowych
#
# Wejście: lista studentów jako
#          - plik tekstowy (każda linia: Nazwisko Imie), albo
#          - PDF z USOS ("Studenci uprawnieni do zaliczania przedmiotu")
#
# Wynik: <katalog>/Studenci/Nazwisko Imie.pdf        (dla studentów / Moodle)
#        <katalog>/Klucze/Klucz_Nazwisko Imie.pdf    (dla prowadzącego)
#        <katalog>/zestawienie.csv                   (parametry każdego zestawu)
#
# Użycie: cd Cwiczenia/Karty_PDF && Rscript generuj_imienne.R [lista] [katalog]
#         Rscript generuj_imienne.R studenci.txt                    # -> output_imienne/
#         Rscript generuj_imienne.R ~/Downloads/lista.pdf output_2026_2027
# ============================================================================

args <- commandArgs(trailingOnly = TRUE)
input_file <- if (length(args) > 0) args[1] else "studenci.txt"
out_dir    <- if (length(args) > 1) args[2] else "output_imienne"

if (!file.exists(input_file)) {
  stop("Nie znaleziono pliku wejściowego: ", input_file,
       "\nUpewnij się, że plik istnieje w katalogu Cwiczenia/Karty_PDF.")
}

# Lista z USOS (PDF): wiersze "  1 Nazwisko Imię      WYK1, LAB1"
read_usos_pdf <- function(path) {
  txt <- system2("pdftotext", c("-layout", shQuote(path), "-"), stdout = TRUE)
  m <- regmatches(txt, regexec("^\\s*\\d+\\s+(\\S.*?)(?:\\s{2,}(\\S.*?))?\\s*$", txt, perl = TRUE))
  m <- Filter(function(r) length(r) == 3, m)
  data.frame(osoba = sapply(m, `[`, 2), grupy = sapply(m, `[`, 3))
}

cat("=== Wczytywanie listy studentów z:", input_file, "===\n")
if (grepl("\\.pdf$", input_file, ignore.case = TRUE)) {
  lista <- read_usos_pdf(input_file)
} else {
  osoby <- readLines(input_file, warn = FALSE, encoding = "UTF-8")
  lista <- data.frame(osoba = osoby, grupy = "")
}
Encoding(lista$osoba) <- "UTF-8"
lista$osoba <- gsub("\\s+", " ", trimws(lista$osoba)) # spacje na końcu psuły nazwy plików
lista <- lista[lista$osoba != "", ]
studenci <- lista$osoba
N <- length(studenci)
cat("Znaleziono", N, "osób.\n\n")

dir.create(file.path(out_dir, "Studenci"), recursive = TRUE, showWarnings = FALSE)
dir.create(file.path(out_dir, "Klucze"), recursive = TRUE, showWarnings = FALSE)

# Funkcja losująca parametry (deterministyczna po seedzie)
generate_params <- function(seed_val) {
  set.seed(seed_val)
  list(
    V = sample(seq(3, 8, 0.1), 1),
    p_man = sample(seq(6, 12, 0.1), 1),
    t = sample(15:35, 1),
    p_atm = sample(seq(740, 770, 5), 1),
    t_fire = sample(seq(200, 400, 10), 1),
    y_N2 = sample(seq(70, 85, 5), 1),
    p_mix = sample(3:8, 1),
    t_mix = sample(seq(15, 30, 5), 1),
    V_mix = sample(seq(1, 4, 0.5), 1),
    T_valve = sample(seq(200, 300, 10), 1),
    p2 = sample(seq(7, 12, 0.5), 1),
    n_poly = sample(seq(1.25, 1.38, 0.01), 1),
    Vn = sample(seq(60, 150, 10), 1),
    t_chlod = sample(seq(25, 40, 5), 1),
    # Ćw. 3: stany w siatce tablic pary przegrzanej (B2/B3: 10–16 bar; 200/250/300 °C),
    # jak w przykładzie z ćwiczeń (10 bar, 250 °C) — bez podwójnej interpolacji
    p_kociol = sample(10:16, 1),
    t_para = sample(c(200, 250, 300), 1),
    m_dot_kociol = sample(seq(1.5, 3.0, 0.5), 1),
    t_zas = sample(seq(40, 80, 10), 1),
    eta_k = sample(seq(0.85, 0.95, 0.05), 1),
    p_dlawienie = sample(c(1, 2, 5), 1),  # kolumny tablicy B1 (przykład: 2 bar)
    hm = sample(seq(2200, 2600, 50), 1),
    # Ćw. 4: turbina zastępuje zawór dławiący (wlot = kocioł, wylot = p_dlawienie),
    # parametry wlotu/wylotu/strumienia wylicza szablon
    eta_is = sample(seq(0.75, 0.85, 0.05), 1),
    m_spalin = sample(seq(0.5, 2.0, 0.25), 1),
    t_sp_in = sample(seq(250, 350, 25), 1),
    t_sp_out = sample(seq(120, 180, 10), 1),
    t_w_in = sample(seq(15, 25, 5), 1),
    t_w_out = sample(seq(60, 90, 10), 1),
    Q_o = sample(seq(200, 500, 50), 1),
    t_o = sample(-5:5, 1),
    t_k = sample(seq(35, 45, 5), 1),
    # Zad. 6.7: średnica rury jako ułamek średnicy wymaganej dla 12 m/s
    # (0.6–0.8: rura za mała jak w przykładzie z ćwiczeń, 0.9–1.1: w normie)
    f_rura = sample(c(0.6, 0.7, 0.8, 0.9, 1.0, 1.1), 1),
    t_zima = sample(-15:-5, 1),
    t_lato = sample(seq(28, 36, 2), 1),
    t_wewn = sample(20:24, 1),
    V_dot = sample(seq(15000, 30000, 5000), 1),
    Q_jawne = sample(seq(30, 80, 10), 1),
    rec = sample(seq(60, 80, 5), 1),
    # Zad. 1.2e: butla na azot (przykład z ćwiczeń: 50 kg, 15 °C, 200 bar)
    m_N2_tank = sample(seq(20, 80, 5), 1),
    p_N2_tank = sample(c(150, 200, 300), 1),
    t_N2_tank = sample(5:25, 1),
    # Zad. 2.8: pomiar serwisanta (przykład z ćwiczeń: 22 °C/1 bar -> 215 °C/8 bar, n = 1.32)
    p2_pom = sample(6:10, 1),
    n_pom = sample(seq(1.22, 1.40, 0.01), 1)
  )
}

# Kontrola fizyczna zestawu (CoolProp, ten sam venv co szablon).
# Odrzucamy zestawy, w których:
#  - para z kotła jest ledwo przegrzana (Zad. 3.1 byłoby niejednoznaczne, a przy
#    16 bar / 200 °C to w ogóle woda, nie para),
#  - rozprężanie izentropowe w turbinie (kocioł -> p_dlawienie), także w wariancie
#    z Zad. 4.5, kończy się poza obszarem pary mokrej (Zad. 4.1–4.5 zakładają 0 < x2 < 1).
library(reticulate)
use_virtualenv("termo", required = TRUE)
cp <- import("CoolProp.CoolProp")
W <- function(out, in1, v1, in2, v2) cp$PropsSI(out, in1, v1, in2, v2, "Water")

check_params <- function(p) {
  tsat_k <- W("T", "P", p$p_kociol * 1e5, "Q", 0) - 273.15
  sf2 <- W("S", "P", p$p_dlawienie * 1e5, "Q", 0)
  sg2 <- W("S", "P", p$p_dlawienie * 1e5, "Q", 1)
  x2 <- function(p1, t1) (W("S", "P", p1 * 1e5, "T", t1 + 273.15) - sf2) / (sg2 - sf2)
  x_baza <- x2(p$p_kociol, p$t_para)
  x_var  <- x2(p$p_kociol + 4, p$t_para + 50)  # Zad. 4.5: wariant +4 bar / +50 K
  p$t_para - tsat_k >= 20 && x_baza > 0 && x_baza < 0.99 && x_var > 0 && x_var < 0.99
}

# Parametry wyliczane z wylosowanych (wywołać po check_params)
uzupelnij_params <- function(p) {
  # Zad. 2.8: ssanie z hali przy 1 bar; t2 wynika z "prawdziwego" wykładnika n_pom
  p$t1_pom <- p$t
  p$p1_pom <- 1.0
  p$t2_pom <- round((p$t1_pom + 273.15) * (p$p2_pom / p$p1_pom)^((p$n_pom - 1) / p$n_pom) - 273.15)
  # Zad. 6.7: jak w przykładzie z ćwiczeń (300 kW, d = 80 mm -> 26.8 m/s, potrzeba ~120 mm)
  # rura jest za mała albo mieści się w normie 8-15 m/s
  R <- function(out, in1, v1, in2, v2) cp$PropsSI(out, in1, v1, in2, v2, "R134a")
  To <- p$t_o + 273.15
  m_dot <- p$Q_o / ((R("H", "T", To, "Q", 1) - R("H", "T", p$t_k + 273.15, "Q", 0)) / 1000)
  V_dot <- m_dot / R("D", "T", To, "Q", 1)
  p$d_rura <- round(1000 * sqrt(4 * V_dot / (pi * 12)) * p$f_rura / 10) * 10
  p
}

# Wartości pomocnicze — trafiają do zestawienia, ale nie do szablonu
tylko_csv <- c("f_rura", "n_pom")

# Funkcja budująca flagi -P dla quarto render
build_pflags <- function(params_list) {
  paste(sapply(names(params_list), function(nm) {
    v <- params_list[[nm]]
    if (is.character(v)) v <- shQuote(v)
    sprintf("-P %s:%s", nm, v)
  }), collapse = " ")
}

template_path <- "Karta_Projektowa_Szablon.qmd"
if (!file.exists(template_path)) {
  stop("Brak szablonu ", template_path, " — uruchom skrypt z katalogu Cwiczenia/Karty_PDF.")
}

# Główna pętla
cat("Start generowania...\n")

uzyte_seedy <- c()
zestawienie <- list()

for (i in 1:N) {
  osoba <- studenci[i]
  # Hash z nazwiska jako seed (suma kodów znaków); kolizje i zestawy
  # niespełniające kontroli fizycznej przesuwają seed o 1000
  seed_val <- sum(utf8ToInt(osoba)) + 2025
  repeat {
    if (!(seed_val %in% uzyte_seedy)) {
      sys_params <- generate_params(seed_val)
      if (check_params(sys_params)) break
    }
    seed_val <- seed_val + 1000
  }
  uzyte_seedy <- c(uzyte_seedy, seed_val)
  sys_params <- uzupelnij_params(sys_params)

  # Nazwa pliku dla studenta (prosta: Jan Kowalski.pdf)
  # Usuwamy dziwne znaki, ale zostawiamy spacje i myślniki dla Moodle
  safe_name <- iconv(osoba, from = "UTF-8", to = "ASCII//TRANSLIT")
  safe_name <- gsub("[^a-zA-Z0-9_ -]", "", safe_name) # allow spaces and dashes

  fname_student <- sprintf("%s.pdf", safe_name)      # np. Jan Kowalski.pdf
  fname_klucz   <- sprintf("Klucz_%s.pdf", safe_name) # np. Klucz_Jan Kowalski.pdf

  cat(sprintf("[%2d/%d] %-30s -> %s ", i, N, osoba, fname_student))

  sys_params$student_name <- osoba
  sys_params$zestaw_nr <- i
  zestawienie[[i]] <- data.frame(nr = i, osoba = osoba, grupy = lista$grupy[i],
                                 seed = seed_val, sys_params[setdiff(names(sys_params), c("student_name", "zestaw_nr"))])

  # 1. Wersja dla studenta, 2. klucz (dla prowadzącego)
  for (wersja in c("student", "klucz")) {
    sys_params$show_answers <- if (wersja == "klucz") "true" else "false"
    fname  <- if (wersja == "klucz") fname_klucz else fname_student
    subdir <- if (wersja == "klucz") "Klucze" else "Studenci"

    cmd <- sprintf('quarto render "%s" %s -o "%s" --quiet 2>&1',
                   template_path, build_pflags(sys_params[setdiff(names(sys_params), tylko_csv)]), fname)
    res <- system(cmd, intern = TRUE)

    if (!is.null(attr(res, "status")) && attr(res, "status") != 0) {
      cat(sprintf("ERR(%s)\n", wersja))
      cat("Szczegóły błędu:\n")
      print(tail(res, 20))
    } else if (file.exists(fname)) {
      file.rename(fname, file.path(out_dir, subdir, fname))
      cat(if (wersja == "klucz") "(+Klucz)\n" else "OK ")
    } else {
      cat(sprintf("ERR(mv %s) ", wersja))
    }
  }
}

write.csv(do.call(rbind, zestawienie), file.path(out_dir, "zestawienie.csv"),
          row.names = FALSE, fileEncoding = "UTF-8")

cat("\n=== GOTOWE ===\n")
cat("Pliki znajdziesz w:\n")
cat(sprintf("  - %s/Studenci/ (te wyślij na Moodle)\n", out_dir))
cat(sprintf("  - %s/Klucze/   (dla Ciebie)\n", out_dir))
cat(sprintf("  - %s/zestawienie.csv (parametry zestawów)\n", out_dir))
