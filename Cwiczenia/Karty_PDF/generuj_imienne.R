#!/usr/bin/env Rscript
# ============================================================================
# generuj_imienne.R — Generowanie imiennych kart projektowych
# 
# Wejście: plik tekstowy z listą studentów (np. studenci.txt)
#          każda linia: Nazwisko Imie
#
# Wynik: output_imienne/Karta_[Nazwisko_Imie].pdf
#        output_imienne/Klucz_[Nazwisko_Imie].pdf (opcjonalnie)
#
# Użycie: cd Cwiczenia/Karty_PDF && Rscript generuj_imienne.R [plik_z_lista]
#         cd Cwiczenia/Karty_PDF && Rscript generuj_imienne.R studenci.txt
# ============================================================================

args <- commandArgs(trailingOnly = TRUE)
input_file <- if (length(args) > 0) args[1] else "studenci.txt"

if (!file.exists(input_file)) {
  stop("Nie znaleziono pliku wejściowego: ", input_file, 
       "\nUpewnij się, że plik istnieje w katalogu Cwiczenia/Karty_PDF.")
}

cat("=== Wczytywanie listy studentów z:", input_file, "===\n")
studenci <- readLines(input_file, warn = FALSE)
studenci <- studenci[studenci != ""] # usuń puste linie
N <- length(studenci)
cat("Znaleziono", N, "osób.\n\n")

dir.create("output_imienne", showWarnings = FALSE)
dir.create("output_imienne/Studenci", showWarnings = FALSE)
dir.create("output_imienne/Klucze", showWarnings = FALSE)

# Funkcja losująca parametry (deterministyczna po seedzie)
generate_params <- function(seed_val) {
  set.seed(seed_val)
  list(
    V = sample(seq(3, 8, 0.5), 1),
    p_man = sample(seq(6, 12, 0.5), 1),
    t = sample(15:35, 1),
    p_atm = sample(seq(740, 770, 5), 1),
    t_fire = sample(seq(200, 400, 50), 1),
    y_N2 = sample(seq(70, 85, 5), 1),
    p_mix = sample(3:8, 1),
    t_mix = sample(seq(15, 30, 5), 1),
    V_mix = sample(seq(1, 4, 0.5), 1),
    T_valve = sample(seq(200, 300, 10), 1),
    p2 = sample(seq(7, 12, 0.5), 1),
    t1_spr = sample(15:25, 1),
    n_poly = sample(seq(1.25, 1.38, 0.01), 1),
    Vn = sample(seq(60, 150, 10), 1),
    t_chlod = sample(seq(25, 40, 5), 1),
    p_kociol = sample(8:16, 1),
    t_para = sample(seq(200, 300, 25), 1),
    m_dot_kociol = sample(seq(1.5, 3.0, 0.5), 1),
    t_zas = sample(seq(40, 80, 10), 1),
    eta_k = sample(seq(0.85, 0.95, 0.05), 1),
    p_dlawienie = sample(1:4, 1),
    hm = sample(seq(2200, 2600, 50), 1),
    p1_turb = sample(8:14, 1),
    t1_turb = sample(seq(200, 300, 25), 1),
    p2_turb = sample(seq(0.5, 2.0, 0.5), 1),
    m_dot_turb = sample(seq(0.3, 0.8, 0.05), 1),
    eta_is = sample(seq(0.75, 0.85, 0.05), 1),
    m_spalin = sample(seq(0.5, 2.0, 0.25), 1),
    t_sp_in = sample(seq(250, 350, 25), 1),
    t_sp_out = sample(seq(120, 180, 10), 1),
    t_w_in = sample(seq(15, 25, 5), 1),
    t_w_out = sample(seq(60, 90, 10), 1),
    T0 = sample(seq(15, 25, 5), 1),
    Q_o = sample(seq(200, 500, 50), 1),
    t_o = sample(-5:5, 1),
    t_k = sample(seq(35, 45, 5), 1),
    d_rura = sample(seq(50, 100, 10), 1),
    t_zima = sample(-15:-5, 1),
    t_lato = sample(seq(28, 36, 2), 1),
    t_wewn = sample(20:24, 1),
    V_dot = sample(seq(15000, 30000, 5000), 1),
    Q_jawne = sample(seq(30, 80, 10), 1),
    rec = sample(seq(60, 80, 5), 1)
  )
}

# Funkcja budująca flagi -P dla quarto render
build_pflags <- function(params_list) {
  paste(sapply(names(params_list), function(nm) {
    v <- params_list[[nm]]
    if (is.character(v)) v <- sprintf('"%s"', v)
    sprintf("-P %s:%s", nm, v)
  }), collapse = " ")
}

# Główna pętla
cat("Start generowania...\n")

for (i in 1:N) {
  osoba <- studenci[i]
  # Hash z nazwiska jako seed (suma kodów znaków)
  seed_val <- sum(utf8ToInt(osoba)) + 2025 
  
  sys_params <- generate_params(seed_val)
  
  # Nazwa pliku dla studenta (prosta: Jan Kowalski.pdf)
  # Usuwamy dziwne znaki, ale zostawiamy spacje i myślniki dla Moodle
  safe_name <- iconv(osoba, to="ASCII//TRANSLIT")
  safe_name <- gsub("[^a-zA-Z0-9_ -]", "", safe_name) # allow spaces and dashes
  
  fname_student <- sprintf("%s.pdf", safe_name)      # np. Jan Kowalski.pdf
  fname_klucz   <- sprintf("Klucz_%s.pdf", safe_name) # np. Klucz_Jan Kowalski.pdf
  
  cat(sprintf("[%2d/%d] %-30s -> %s ", i, N, osoba, fname_student))
  
  # 1. Generuj wersję dla studenta
  sys_params$student_name <- osoba
  sys_params$show_answers <- "false"
  sys_params$zestaw_nr <- i
  
  # Użyj pełnej ścieżki do szablonu, aby działało z każdego katalogu
  # (zakładamy, że szablon jest w tym samym katalogu co skrypt)
  # Zostańmy przy CWD użytkownika. MUSISZ byc w katalogu Cwiczenia/Karty_PDF.
  # Zostańmy przy CWD użytkownika. MUSISZ byc w katalogu Cwiczenia/Karty_PDF.
  
  template_path <- "Karta_Projektowa_Szablon.qmd"
  if (!file.exists(template_path)) {
     cat("ERR(brak_szablonu)\n")
     next
  }

  cmd <- sprintf('quarto render "%s" %s -o "%s" --quiet 2>&1', 
                 template_path, build_pflags(sys_params), fname_student)
  
  res <- system(cmd, intern=TRUE) 
  # intern=TRUE łapie output. Jeśli status != 0, to output zawiera błąd.
  
  if (!is.null(attr(res, "status")) && attr(res, "status") != 0) {
    cat("ERR(render)\n")
    cat("Szczegóły błędu:\n")
    print(res)
  } else {
    # Przenieś do folderu Studenci
    if (file.exists(fname_student)) {
        file.rename(fname_student, file.path("output_imienne/Studenci", fname_student))
        cat("OK ")
    } else {
        cat("ERR(mv) ")
    }
  }
  
  # 2. Generuj klucz (dla prowadzącego)
  sys_params$show_answers <- "true"
  cmd_klucz <- sprintf('quarto render "%s" %s -o "%s" --quiet 2>/dev/null', 
                 template_path, build_pflags(sys_params), fname_klucz)
                 
  res_klucz <- system(cmd_klucz, intern=TRUE)
  
  if (!is.null(attr(res_klucz, "status")) && attr(res_klucz, "status") != 0) {
     cat("(Klucz ERR)\n")
  } else {
     if (file.exists(fname_klucz)) {
        file.rename(fname_klucz, file.path("output_imienne/Klucze", fname_klucz))
        cat("(+Klucz)\n")
     }
  }
}

cat("\n=== GOTOWE ===\n")
cat("Pliki znajdziesz w:\n")
cat("  - output_imienne/Studenci/ (te wyślij na Moodle)\n")
cat("  - output_imienne/Klucze/   (dla Ciebie)\n")
