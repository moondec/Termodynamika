library(ggplot2)
library(dplyr)
library(reticulate)

# Wykres T-s do Ćw. 4 (Cwiczenia/04_Obieg_Rankine.qmd):
# turbina przeciwprężna zamiast zaworu redukcyjnego (przykład z Ćw. 3 i 4):
# wlot = para z kotła 10 bar / 250 °C, wylot = 2 bar, η_is = 0.80,
# dla porównania dławienie na zaworze (h = const) do 2 bar.
# Uruchamiać z katalogu tools/:  Rscript generate_rankine_chart.R

# Setup środowiska
tryCatch({
  use_virtualenv("termo", required = TRUE)
}, error = function(e) {
  message("Warning: Venv issue, trying standard import")
})

CP <- import("CoolProp.CoolProp")
fluid <- "Water"
W <- function(out, in1, v1, in2, v2) CP$PropsSI(out, in1, v1, in2, v2, fluid)

# --- 1. TŁO (Krzywa nasycenia T-s) ---
T_crit <- CP$PropsSI("Tcrit", fluid)
T_trip <- 273.16

sat_data <- data.frame(T_K = seq(T_trip, T_crit - 0.1, length.out = 300)) %>%
  rowwise() %>%
  mutate(
    T_C = T_K - 273.15,
    s_liq = W("S", "T", T_K, "Q", 0) / 1e3,
    s_vap = W("S", "T", T_K, "Q", 1) / 1e3
  ) %>% ungroup()

# --- 2. TURBINA PRZECIWPRĘŻNA (Ćw. 4) ---
p1 <- 10e5            # wlot: para z kotła [Pa]
t1 <- 250             # [°C]
p2 <- 2e5             # wylot: ciśnienie po dławieniu [Pa]
eta_is <- 0.80

h1 <- W("H", "P", p1, "T", t1 + 273.15) / 1e3
s1 <- W("S", "P", p1, "T", t1 + 273.15) / 1e3
t_sat2 <- W("T", "P", p2, "Q", 0) - 273.15

# 2s: rozprężanie izentropowe
h2s <- W("H", "P", p2, "S", s1 * 1e3) / 1e3
# 2r: rozprężanie rzeczywiste
h2r <- h1 - eta_is * (h1 - h2s)
s2r <- W("S", "P", p2, "H", h2r * 1e3) / 1e3
# D: dławienie na zaworze (h = const) – stan po zaworze
tD <- W("T", "P", p2, "H", h1 * 1e3) - 273.15
sD <- W("S", "P", p2, "H", h1 * 1e3) / 1e3

# Izobary: 10 bar (kocioł) i 2 bar (wylot) – od cieczy nasyconej
isobar <- function(p, s_end, n = 120) {
  s_l <- W("S", "P", p, "Q", 0) / 1e3
  s_g <- W("S", "P", p, "Q", 1) / 1e3
  ts <- W("T", "P", p, "Q", 0) - 273.15
  s_sup <- seq(s_g, s_end, length.out = n)
  t_sup <- sapply(s_sup, function(s) W("T", "P", p, "S", s * 1e3) - 273.15)
  data.frame(s = c(s_l, s_sup), T = c(ts, t_sup))
}
iso_p1 <- isobar(p1, s1)
iso_p2 <- isobar(p2, sD)

# Izentalpa h = h1 (dławienie 10 -> 2 bar)
p_thr <- seq(p1, p2, length.out = 40)
thr <- data.frame(
  s = sapply(p_thr, function(p) W("S", "P", p, "H", h1 * 1e3) / 1e3),
  T = sapply(p_thr, function(p) W("T", "P", p, "H", h1 * 1e3) - 273.15)
)

pts <- data.frame(
  s = c(s1, s1, s2r, sD),
  T = c(t1, t_sat2, t_sat2, tD),
  lab = c(sprintf("1: %g bar, %g °C", p1 / 1e5, t1), "2s", "2r",
          sprintf("D: po zaworze, %.0f °C", tD)),
  hj = c(1.1, 1.5, -0.5, 0.75),
  vj = c(-0.6, 1.4, 1.4, -1.1)
)

t_sat1 <- W("T", "P", p1, "Q", 0) - 273.15

# Procesy (legenda zamiast podpisów na wykresie)
lab_iz <- "turbina idealna: 1 → 2s (s = const)"
lab_r  <- sprintf("turbina rzeczywista: 1 → 2r (η_is = %.2f)", eta_is)
lab_d  <- "zawór dławiący: 1 → D (h = const)"
proc <- rbind(
  data.frame(s = c(s1, s1),  T = c(t1, t_sat2), proces = lab_iz),
  data.frame(s = c(s1, s2r), T = c(t1, t_sat2), proces = lab_r),
  data.frame(s = thr$s, T = thr$T, proces = lab_d)
)
proc$proces <- factor(proc$proces, levels = c(lab_iz, lab_r, lab_d))
# etykiety legendy z indeksem dolnym η_is (plotmath)
leg_lab <- c(lab_iz,
             bquote("turbina rzeczywista: 1 → 2r (" * eta[is] == .(sprintf("%.2f", eta_is)) * ")"),
             lab_d)

# --- 3. RYSOWANIE (zbliżenie na obszar pracy turbiny) ---
p <- ggplot() +
  geom_path(data = sat_data, aes(x = s_vap, y = T_C), color = "red", linewidth = 1, alpha = 0.6) +
  # izobary
  geom_path(data = iso_p1, aes(s, T), color = "gray55", linewidth = 0.8, linetype = "dotted") +
  geom_path(data = iso_p2, aes(s, T), color = "gray55", linewidth = 0.8, linetype = "dotted") +
  annotate("text", x = 5.85, y = t_sat1 + 5, label = "p = 10 bar", color = "gray40", size = 4.5, hjust = 0) +
  annotate("text", x = 5.85, y = t_sat2 + 5, label = "p = 2 bar", color = "gray40", size = 4.5, hjust = 0) +
  annotate("text", x = 6.27, y = 238, label = "x = 1", color = "red", alpha = 0.8, size = 4.5, hjust = 0) +
  annotate("text", x = 6.05, y = 145, label = "para mokra\n(0 < x < 1)", color = "gray50", size = 4.5) +
  annotate("text", x = 7.75, y = 175, label = "para przegrzana", color = "gray50", size = 4.5) +
  # procesy
  geom_path(data = proc, aes(s, T, color = proces, linetype = proces, group = proces), linewidth = 1.3,
            arrow = arrow(ends = "last", type = "closed", length = unit(0.3, "cm"))) +
  scale_color_manual(values = c("black", "#d62728", "gray40"), labels = leg_lab, name = NULL) +
  scale_linetype_manual(values = c("solid", "solid", "dashed"), labels = leg_lab, name = NULL) +
  geom_point(data = pts, aes(s, T), size = 3.5) +
  geom_text(data = pts, aes(s, T, label = lab, hjust = hj, vjust = vj), fontface = "bold", size = 5) +
  coord_cartesian(xlim = c(5.8, 8.1), ylim = c(105, 265)) +
  scale_x_continuous(breaks = seq(5.8, 8.2, 0.2)) +
  labs(
    title = "Turbina przeciwprężna zamiast zaworu (wykres T-s)",
    subtitle = sprintf("Para z kotła %g bar / %g °C → %g bar;   2s: x = %.3f,   2r: x = %.3f",
                       p1 / 1e5, t1, p2 / 1e5,
                       W("Q", "P", p2, "S", s1 * 1e3), W("Q", "P", p2, "H", h2r * 1e3)),
    x = "Entropia właściwa s [kJ/(kg·K)]",
    y = "Temperatura t [°C]"
  ) +
  theme_bw(base_size = 15) +
  theme(legend.position = "bottom", legend.direction = "vertical",
        legend.key.width = unit(1.6, "cm"), legend.text = element_text(size = 13))

ggsave("../img/rankine_ts_przeciwprezna.png", plot = p, width = 9, height = 6.6, dpi = 150)
