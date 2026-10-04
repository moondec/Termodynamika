# Wykresy p-h (R134a) do Ćwiczenia 6 (Cwiczenia/06_Projekt_Chlodniczy.qmd):
#  - img/cw6_obieg_r134a.png   — Zad. 6.1: obieg bazowy (t_o = 2 °C, t_k = 40 °C)
#                                 z kierunkami przemian i ciśnieniami p_o, p_k
#  - img/cycles_comparison.png — Zad. 6.5: obieg bazowy vs t_k = 55 °C (+15 K,
#                                 zabrudzony skraplacz — jak w karcie projektowej)
# Uruchamiać z katalogu tools/:  Rscript generate_cycles_chart.R

library(ggplot2)
library(dplyr)
library(reticulate)

tryCatch({
  use_virtualenv("termo", required = TRUE)
}, error = function(e) {
  message("Nie udało się załadować venv 'termo', próbuję standardowy import...")
})

CP <- import("CoolProp.CoolProp")
fluid <- "R134a"

# --- 1. Krzywe nasycenia ---
T_crit <- CP$PropsSI("Tcrit", fluid)
T_seq <- seq(225, T_crit - 0.5, length.out = 300)
sat_data <- data.frame(T = T_seq) %>%
  rowwise() %>%
  mutate(
    p_bar = CP$PropsSI("P", "T", T, "Q", 0, fluid) / 1e5,
    h_liq = CP$PropsSI("H", "T", T, "Q", 0, fluid) / 1e3,
    h_vap = CP$PropsSI("H", "T", T, "Q", 1, fluid) / 1e3
  ) %>% ungroup()

# --- 2. Obieg teoretyczny: 1 para nasycona, 1-2 s = const, 3 ciecz nasycona, 3-4 h = const ---
calc_cycle <- function(To_C, Tk_C) {
  To <- To_C + 273.15
  Tk <- Tk_C + 273.15
  p1 <- CP$PropsSI("P", "T", To, "Q", 1, fluid)
  h1 <- CP$PropsSI("H", "T", To, "Q", 1, fluid)
  s1 <- CP$PropsSI("S", "T", To, "Q", 1, fluid)
  p2 <- CP$PropsSI("P", "T", Tk, "Q", 0, fluid)
  h2 <- CP$PropsSI("H", "P", p2, "S", s1, fluid)
  t2 <- CP$PropsSI("T", "P", p2, "S", s1, fluid) - 273.15
  h3 <- CP$PropsSI("H", "P", p2, "Q", 0, fluid)
  # izentropa 1-2 jako krzywa (nie odcinek)
  p_is <- exp(seq(log(p1), log(p2), length.out = 30))
  h_is <- sapply(p_is, function(pp) CP$PropsSI("H", "P", pp, "S", s1, fluid))
  path <- data.frame(
    h = c(h_is, h3, h3, h1) / 1e3,
    p = c(p_is, p2, p1, p1) / 1e5
  )
  pts <- data.frame(
    point = c("1", "2", "3", "4"),
    h = c(h1, h2, h3, h3) / 1e3,
    p = c(p1, p2, p2, p1) / 1e5
  )
  list(path = path, pts = pts, t2 = t2, s1 = s1 / 1e3,
       p1 = p1 / 1e5, p2 = p2 / 1e5, h_is = h_is / 1e3, p_is = p_is / 1e5)
}

base <- calc_cycle(2, 40)   # Zad. 6.1–6.3
high <- calc_cycle(2, 55)   # Zad. 6.5 (t_k + 15 K)

col_base <- "#2ca02c"
col_high <- "#d62728"

sat_layers <- list(
  geom_path(data = sat_data, aes(x = h_liq, y = p_bar), color = "blue", linewidth = 1),
  geom_path(data = sat_data, aes(x = h_vap, y = p_bar), color = "red", linewidth = 1)
)

# Strzałka w połowie odcinka (a -> b), współrzędne w jednostkach danych
mid_arrow <- function(h_a, p_a, h_b, p_b, frac = 0.06, color = col_base) {
  hm <- (h_a + h_b) / 2
  pm <- exp((log(p_a) + log(p_b)) / 2)
  dh <- (h_b - h_a) * frac
  dlp <- (log(p_b) - log(p_a)) * frac
  annotate("segment",
           x = hm - dh, y = exp(log(pm) - dlp), xend = hm + dh, yend = exp(log(pm) + dlp),
           color = color, linewidth = 1.5,
           arrow = arrow(length = unit(0.45, "cm"), type = "closed"))
}

# --- 3a. Wykres do Zad. 6.1: obieg bazowy z kierunkami przemian ---
b <- base$pts
n_is <- length(base$h_is)
k <- floor(n_is / 2)

p1_plot <- ggplot() +
  sat_layers +
  annotate("text", x = 222, y = 5.6, label = "x = 0", color = "blue", size = 7, hjust = 1) +
  annotate("text", x = 386, y = 1.75, label = "x = 1", color = "red", size = 7, hjust = 1) +
  geom_path(data = base$path, aes(x = h, y = p), color = col_base, linewidth = 1.5) +
  geom_point(data = b, aes(x = h, y = p), size = 4, color = col_base) +
  # kierunki przemian
  annotate("segment",
           x = base$h_is[k - 1], y = base$p_is[k - 1], xend = base$h_is[k + 2], yend = base$p_is[k + 2],
           color = col_base, linewidth = 1.5,
           arrow = arrow(length = unit(0.45, "cm"), type = "closed")) +
  mid_arrow(b$h[2], b$p[2], b$h[3], b$p[3]) +
  mid_arrow(b$h[3], b$p[3], b$h[4], b$p[4], frac = 0.08) +
  mid_arrow(b$h[4], b$p[4], b$h[1], b$p[1]) +
  # numery punktów
  annotate("text", x = b$h[1] + 4, y = b$p[1] * 0.90, label = "1", color = col_base,
           size = 11, fontface = "bold", hjust = 0) +
  annotate("text", x = b$h[2] + 4, y = b$p[2] * 1.09, label = "2", color = col_base,
           size = 11, fontface = "bold", hjust = 0) +
  annotate("text", x = b$h[3] - 5, y = b$p[3] * 1.09, label = "3", color = col_base,
           size = 11, fontface = "bold", hjust = 1) +
  annotate("text", x = b$h[4] - 5, y = b$p[4] * 0.90, label = "4", color = col_base,
           size = 11, fontface = "bold", hjust = 1) +
  # przemiany i ciśnienia
  annotate("text", x = (b$h[2] + b$h[3]) / 2, y = b$p[2] * 1.18, size = 7, parse = TRUE,
           label = "'2→3 skraplanie: '*p[k]*' = 10.17 bar'") +
  annotate("text", x = (b$h[1] + b$h[4]) / 2, y = b$p[1] * 0.84, size = 7, parse = TRUE,
           label = "'4→1 parowanie: '*p[o]*' = 3.15 bar'") +
  annotate("text", x = b$h[3] + 4, y = 5.6, size = 7, hjust = 0,
           label = "3→4 dławienie\n(h = const)") +
  annotate("text", x = 404, y = 6.0, size = 7, hjust = 1,
           label = "1→2 sprężanie\n(s = const)") +
  annotate("text", x = b$h[2] + 3, y = b$p[2] * 1.40, size = 7, hjust = 0, parse = TRUE,
           label = "t[2] %~~% '44 °C'") +
  # odczyt entalpii na osi h
  annotate("segment", x = b$h[c(1, 2, 3)], xend = b$h[c(1, 2, 3)],
           y = b$p[c(1, 2, 3)], yend = 1.25, linetype = "dotted", color = "grey30") +
  annotate("label", x = b$h[3], y = 1.18, label = "h[3]==h[4] %~~% 256", parse = TRUE, size = 7,
           fill = "white", label.size = 0) +
  annotate("label", x = b$h[1] - 2, y = 1.18, label = "h[1] %~~% 400", parse = TRUE, size = 7,
           hjust = 1, fill = "white", label.size = 0) +
  annotate("label", x = b$h[2] + 2, y = 1.18, label = "h[2] %~~% 425", parse = TRUE, size = 7,
           hjust = 0, fill = "white", label.size = 0) +
  scale_y_log10(breaks = c(1, 2, 3, 5, 10, 15, 20, 30)) +
  scale_x_continuous(breaks = seq(180, 460, 20)) +
  coord_cartesian(xlim = c(185, 470), ylim = c(1.1, 30)) +
  labs(
    title = "Obieg teoretyczny R134a (Zad. 6.1)",
    x = "Entalpia h [kJ/kg]",
    y = "Ciśnienie p [bar]"
  ) +
  theme_bw(base_size = 18) +
  theme(
    plot.title = element_text(size = 28, face = "bold"),
    axis.title = element_text(size = 24),
    axis.text = element_text(size = 19),
    panel.grid.minor = element_blank()
  )

ggsave("../img/cw6_obieg_r134a.png", plot = p1_plot, width = 11, height = 8, dpi = 150)
message("Wykres zapisano w: ../img/cw6_obieg_r134a.png")

# --- 3b. Wykres do Zad. 6.5: obieg bazowy vs t_k = 55 °C ---
hp <- high$pts
lab_base <- data.frame(
  label = c("1", "2", "3", "4"),
  x = c(b$h[1] + 4, b$h[2] + 5, b$h[3] - 5, b$h[4] - 5),
  y = c(b$p[1] * 0.90, b$p[2] * 0.93, b$p[3] * 1.07, b$p[4] * 0.90),
  hjust = c(0, 0, 1, 1)
)
lab_high <- data.frame(
  label = c("2'", "3'", "4'"),
  x = c(hp$h[2] + 5, hp$h[3] - 5, hp$h[4] + 4),
  y = c(hp$p[2] * 1.07, hp$p[3] * 1.07, hp$p[4] * 0.90),
  hjust = c(0, 1, 0)
)

p2_plot <- ggplot() +
  sat_layers +
  geom_path(data = base$path, aes(x = h, y = p), color = col_base, linewidth = 1.5) +
  geom_point(data = b, aes(x = h, y = p), size = 4, color = col_base) +
  mid_arrow(b$h[4], b$p[4], b$h[1], b$p[1]) +
  geom_path(data = high$path, aes(x = h, y = p), color = col_high, linewidth = 1.2,
            linetype = "dashed") +
  geom_point(data = hp[2:4, ], aes(x = h, y = p), size = 4, color = col_high) +
  geom_text(data = lab_base, aes(x = x, y = y, label = label, hjust = hjust),
            size = 9, fontface = "bold", color = col_base) +
  geom_text(data = lab_high, aes(x = x, y = y, label = label, hjust = hjust),
            size = 9, fontface = "bold", color = col_high) +
  # przesunięcie punktu 4 -> 4' (mniejsze q_o)
  annotate("segment", x = b$h[4] + 2, xend = hp$h[4] - 2, y = 2.35, yend = 2.35,
           color = col_high, linewidth = 1,
           arrow = arrow(length = unit(0.3, "cm"), type = "closed")) +
  annotate("text", x = (b$h[4] + hp$h[4]) / 2, y = 2.1, size = 5.5, color = col_high,
           label = "'mniejsze '*q[o]", parse = TRUE) +
  scale_y_log10(breaks = c(1, 2, 3, 5, 10, 15, 20, 30)) +
  scale_x_continuous(breaks = seq(180, 460, 20)) +
  coord_cartesian(xlim = c(185, 470), ylim = c(1.5, 30)) +
  labs(
    title = "Porównanie obiegów chłodniczych (R134a)",
    subtitle = expression("Zielony: obieg bazowy ("*t[k]*" = 40 °C)   |   Czerwony: Zad. 6.5 ("*t[k]*" = 55 °C, zabrudzony skraplacz)"),
    x = "Entalpia h [kJ/kg]",
    y = "Ciśnienie p [bar]"
  ) +
  theme_bw(base_size = 18) +
  theme(
    plot.title = element_text(size = 22, face = "bold"),
    axis.title = element_text(size = 18),
    axis.text = element_text(size = 14),
    panel.grid.minor = element_blank()
  )

ggsave("../img/cycles_comparison.png", plot = p2_plot, width = 12, height = 7.5, dpi = 150)
message("Wykres zapisano w: ../img/cycles_comparison.png")
