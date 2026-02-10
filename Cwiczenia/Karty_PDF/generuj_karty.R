#!/usr/bin/env Rscript
# ============================================================================
# generuj_karty.R — Generowanie indywidualnych kart projektowych PDF
# 
# Użycie: cd Cwiczenia/Karty_PDF && Rscript generuj_karty.R [liczba_zestawów]
# Domyślnie: 30 zestawów
# ============================================================================

args <- commandArgs(trailingOnly = TRUE)
N <- if (length(args) > 0) as.integer(args[1]) else 30

cat("=== Generowanie", N, "zestawów kart projektowych ===\n\n")

set.seed(2025)
dir.create("output", showWarnings = FALSE)

sample_step <- function(min, max, step, n) {
  sample(seq(min, max, by = step), n, replace = TRUE)
}

zestawy <- data.frame(
  zestaw_nr = 1:N,
  V = sample_step(3,8,0.5,N), p_man = sample_step(6,12,0.5,N),
  t = sample_step(15,35,1,N), p_atm = sample_step(740,770,5,N),
  t_fire = sample_step(200,400,50,N), y_N2 = sample_step(70,85,5,N),
  p_mix = sample_step(3,8,1,N), t_mix = sample_step(15,30,5,N),
  V_mix = sample_step(1,4,0.5,N), T_valve = sample_step(200,300,10,N),
  p2 = sample_step(7,12,0.5,N), t1_spr = sample_step(15,25,1,N),
  n_poly = sample_step(1.25,1.38,0.01,N), Vn = sample_step(60,150,10,N),
  t_chlod = sample_step(25,40,5,N),
  p_kociol = sample_step(8,16,1,N), t_para = sample_step(200,300,25,N),
  m_dot_kociol = sample_step(1.5,3.0,0.5,N), t_zas = sample_step(40,80,10,N),
  eta_k = sample_step(0.85,0.95,0.05,N), p_dlawienie = sample_step(1,4,1,N),
  p1_turb = sample_step(8,14,1,N), t1_turb = sample_step(200,300,25,N),
  p2_turb = sample_step(0.5,2.0,0.5,N), m_dot_turb = sample_step(0.3,0.8,0.05,N),
  eta_is = sample_step(0.75,0.85,0.05,N),
  m_spalin = sample_step(0.5,2.0,0.25,N), t_sp_in = sample_step(250,350,25,N),
  t_sp_out = sample_step(120,180,10,N), t_w_in = sample_step(15,25,5,N),
  t_w_out = sample_step(60,90,10,N), T0 = sample_step(15,25,5,N),
  Q_o = sample_step(200,500,50,N), t_o = sample_step(-5,5,1,N),
  t_k = sample_step(35,45,5,N), d_rura = sample_step(50,100,10,N),
  t_zima = sample_step(-15,-5,1,N), t_lato = sample_step(28,36,2,N),
  t_wewn = sample_step(20,24,1,N), V_dot = sample_step(15000,30000,5000,N),
  Q_jawne = sample_step(30,80,10,N), rec = sample_step(60,80,5,N)
)

write.csv(zestawy, "output/zestawienie.csv", row.names = FALSE)
cat("Zapisano: output/zestawienie.csv\n\n")

# ---- Build -P flags string ----
build_pflags <- function(params_list) {
  paste(sapply(names(params_list), function(nm) {
    v <- params_list[[nm]]
    sprintf("-P %s:%s", nm, v)
  }), collapse = " ")
}

# ---- Render loop ----
for (i in 1:N) {
  z <- as.list(zestawy[i, ])
  nr <- sprintf("%02d", z$zestaw_nr)
  cat(sprintf("[%2d/%d] Zestaw %s ", i, N, nr))

  for (mode in c("student", "klucz")) {
    z$show_answers <- if (mode == "klucz") "true" else "false"
    fname <- sprintf("Karta_%s_%s.pdf", nr, mode)
    
    pflags <- build_pflags(z)
    cmd <- sprintf('quarto render Karta_Projektowa_Szablon.qmd %s -o "%s" --quiet 2>/dev/null', pflags, fname)
    system(cmd)
    
    if (file.exists(fname)) {
      file.rename(fname, file.path("output", fname))
      cat(sprintf("%s:OK ", mode))
    } else {
      cat(sprintf("%s:FAIL ", mode))
    }
  }
  cat("\n")
}

n_ok <- length(list.files("output", pattern = "\\.pdf$"))
cat(sprintf("\n=== GOTOWE: %d PDF-ów w output/ ===\n", n_ok))
