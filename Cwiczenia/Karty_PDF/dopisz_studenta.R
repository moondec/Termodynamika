#!/usr/bin/env Rscript
# ============================================================================
# dopisz_studenta.R — card for a single late-enrolled student
#
# Renders the student card and key for ONE person and appends their parameters
# to an existing zestawienie.csv, without re-rendering the whole group
# (re-running generuj_imienne.R would overwrite the group's zestawienie).
# Seeds and parameters follow exactly the rules of generuj_imienne.R, whose
# definitions are loaded from that file; seeds already used in the group are
# skipped.
#
# Usage: cd Cwiczenia/Karty_PDF && Rscript dopisz_studenta.R "Nazwisko Imię" <katalog> ["grupy"] [album]
#        Rscript dopisz_studenta.R "Korbacz Maja" ~/Documents/dydaktyka/IŚ_S_2026_2027/output_2026_2027 "WYK1, LAB2"
# The album number is stored only if the group's zestawienie has an "album"
# column (lists generated before that column existed do not).
# ============================================================================

args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2) {
  stop('Użycie: Rscript dopisz_studenta.R "Nazwisko Imię" <katalog> ["grupy"] [album]')
}
osoba   <- gsub("\\s+", " ", trimws(enc2utf8(args[1])))
out_dir <- args[2]
grupy   <- if (length(args) > 2) args[3] else ""
album   <- if (length(args) > 3) args[4] else ""

csv_path <- file.path(out_dir, "zestawienie.csv")
if (!file.exists(csv_path)) {
  stop("Brak ", csv_path, " — najpierw wygeneruj grupę skryptem generuj_imienne.R.")
}
if (!file.exists("generuj_imienne.R")) {
  stop("Uruchom skrypt z katalogu Cwiczenia/Karty_PDF.")
}

# Load only the definitions (no main loop) so both scripts share one source of truth
keep <- "^(library|use_virtualenv|cp <-|W <-|generate_params|check_params|uzupelnij_params|tylko_csv|build_pflags|template_path)"
for (e in parse("generuj_imienne.R", encoding = "UTF-8")) {
  if (grepl(keep, deparse(e)[1], useBytes = TRUE)) eval(e, globalenv())
}

zest <- read.csv(csv_path, encoding = "UTF-8", check.names = FALSE)
if (osoba %in% zest$osoba) stop("Osoba już jest w zestawieniu: ", osoba)
i <- max(zest$nr) + 1

seed_val <- sum(utf8ToInt(osoba)) + 2025
repeat {
  if (!(seed_val %in% zest$seed)) {
    sys_params <- generate_params(seed_val)
    if (check_params(sys_params)) break
  }
  seed_val <- seed_val + 1000
}
sys_params <- uzupelnij_params(sys_params)

safe_name <- gsub("[^a-zA-Z0-9_ -]", "", iconv(osoba, from = "UTF-8", to = "ASCII//TRANSLIT"))
sys_params$student_name <- osoba
sys_params$zestaw_nr <- i
wiersz <- data.frame(nr = i, osoba = osoba, album = album, grupy = grupy, seed = seed_val,
                     sys_params[setdiff(names(sys_params), c("student_name", "zestaw_nr"))])
# Match the column layout of this group's zestawienie (with or without "album")
if (!"album" %in% names(zest)) {
  if (album != "") warning("Zestawienie nie ma kolumny album — numer albumu pominięty.")
  wiersz$album <- NULL
}
stopifnot(setequal(names(wiersz), names(zest)))
wiersz <- wiersz[names(zest)]

dir.create(file.path(out_dir, "Studenci"), showWarnings = FALSE)
dir.create(file.path(out_dir, "Klucze"), showWarnings = FALSE)

cat(sprintf("%s -> zestaw %d, seed %d\n", osoba, i, seed_val))
for (wersja in c("student", "klucz")) {
  sys_params$show_answers <- if (wersja == "klucz") "true" else "false"
  fname  <- sprintf(if (wersja == "klucz") "Klucz_%s.pdf" else "%s.pdf", safe_name)
  subdir <- if (wersja == "klucz") "Klucze" else "Studenci"
  qargs <- c("render", shQuote(template_path),
             build_pflags(sys_params[setdiff(names(sys_params), tylko_csv)]),
             "-o", shQuote(fname), "--quiet")
  res <- suppressWarnings(system2("quarto", qargs, stdout = TRUE, stderr = TRUE))
  if ((!is.null(attr(res, "status")) && attr(res, "status") != 0) || !file.exists(fname)) {
    print(tail(res, 20))
    stop("Błąd renderowania (", wersja, ") — zestawienie nie zostało zmienione.")
  }
  file.rename(fname, file.path(out_dir, subdir, fname))
  cat("  OK", file.path(subdir, fname), "\n")
}

# Append only after both PDFs exist, so a failed render leaves the CSV intact
write.csv(rbind(zest, wiersz), csv_path, row.names = FALSE, fileEncoding = "UTF-8")
cat("Dopisano do", csv_path, "\n")
