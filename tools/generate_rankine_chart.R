
library(ggplot2)
library(dplyr)
library(reticulate)

# Setup środowiska
tryCatch({
  use_virtualenv("termo", required = TRUE)
}, error = function(e) {
  message("Warning: Venv issue, trying standard import")
})

CP <- import("CoolProp.CoolProp")
fluid <- "Water"

# --- 1. TŁO (Krzywa nasycenia T-s) ---
T_crit <- CP$PropsSI("Tcrit", fluid)
T_trip <- 273.16
s_crit <- CP$PropsSI("S", "T", T_crit, "Q", 0, fluid) / 1e3

# Generujemy punkty nasycenia
sat_data <- data.frame(T_K = seq(T_trip, T_crit-0.1, length.out = 300)) %>%
  rowwise() %>%
  mutate(
    T_C = T_K - 273.15,
    s_liq = CP$PropsSI("S", "T", T_K, "Q", 0, fluid) / 1e3,
    s_vap = CP$PropsSI("S", "T", T_K, "Q", 1, fluid) / 1e3
  ) %>% ungroup()

# --- 2. OBIEG RANKINE'A (Ćw 4) ---
# Założenia z zadania
p_high <- 14 * 1e5  # 14 bar
p_low <- 0.5 * 1e5  # 0.5 bar
t_steam <- 225 + 273.15 # Przegrzew

# Punkt 1: Para przegrzana przed turbiną
s1 <- CP$PropsSI("S", "T", t_steam, "P", p_high, fluid) / 1e3
h1 <- CP$PropsSI("H", "T", t_steam, "P", p_high, fluid) / 1e3
t1 <- t_steam - 273.15

# Punkt 2s: Ekspansja izentropowa w turbinie
s2s <- s1
t2s <- CP$PropsSI("T", "P", p_low, "S", s2s * 1e3, fluid) - 273.15
h2s <- CP$PropsSI("H", "P", p_low, "S", s2s * 1e3, fluid) / 1e3

# Punkt 3: Skropliny (Ciecz nasycona)
t3 <- CP$PropsSI("T", "P", p_low, "Q", 0, fluid) - 273.15
s3 <- CP$PropsSI("S", "P", p_low, "Q", 0, fluid) / 1e3
h3 <- CP$PropsSI("H", "P", p_low, "Q", 0, fluid) / 1e3

# Punkt 4: Za pompą (Woda zasilająca) - izentropowe sprężanie
# (W skali T-s punkt 3 i 4 są b. blisko siebie)
s4 <- s3
t4 <- CP$PropsSI("T", "P", p_high, "S", s4 * 1e3, fluid) - 273.15
h4 <- CP$PropsSI("H", "P", p_high, "S", s4 * 1e3, fluid) / 1e3

# Punkt nasycenia cieczy przy wysokim ciśnieniu (5) i pary (6) - do rysowania izobary
t5 <- CP$PropsSI("T", "P", p_high, "Q", 0, fluid) - 273.15
s5 <- CP$PropsSI("S", "P", p_high, "Q", 0, fluid) / 1e3
s6 <- CP$PropsSI("S", "P", p_high, "Q", 1, fluid) / 1e3

# Tworzenie ścieżki cyklu (1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 1)
cycle_path <- data.frame(
  s = c(s1, s2s, s3, s4, s5, s6, s1),
  T = c(t1, t2s, t3, t4, t5, t5, t1),
  label = c("1", "2", "3", "4", "", "", "")
)

# --- 3. RYSOWANIE ---
p <- ggplot() +
  # Krzywa nasycenia
  geom_path(data = sat_data, aes(x = s_liq, y = T_C), color = "blue", linewidth = 1, alpha=0.6) +
  geom_path(data = sat_data, aes(x = s_vap, y = T_C), color = "red", linewidth = 1, alpha=0.6) +
  
  # Cykl
  geom_path(data = cycle_path, aes(x = s, y = T), color = "black", linewidth = 1.2,
            arrow = arrow(ends = "last", type = "closed", length = unit(0.3, "cm"))) +
  geom_point(data = cycle_path[1:4,], aes(x = s, y = T), size = 4, color = "black") +
  # Etykiety punktów
  geom_text(data = cycle_path[1:4,], aes(x = s, y = T, label = label), 
            vjust = -1, hjust = -0.5, fontface = "bold", size = 6) +
  
  # Obszar mokrej pary
  annotate("text", x = 4, y = 100, label = "Obszar Pary Mokrej\n(x < 1)", color = "gray50") +
  
  # Opis procesu
  annotate("text", x = s1+0.5, y = t1, label = "Ekspansja w Turbinie\n(Praca)", hjust = 0, color = "#d62728") +
  annotate("segment", x = s1+0.4, xend = s1+0.1, y = t1, yend = (t1+t2s)/2, 
           arrow = arrow(length = unit(0.2, "cm")), color = "#d62728") +

  scale_x_continuous(limits = c(0, 9)) +
  labs(
    title = "Obieg Rankine'a (T-s)",
    subtitle = "Woda: 14 bar / 225°C -> 0.5 bar",
    x = "Entropia właściwa s [kJ/(kg·K)]",
    y = "Temperatura T [°C]"
  ) +
  theme_bw(base_size = 14)

ggsave("../img/rankine_ts_chart.png", plot = p, width = 8, height = 6, dpi = 150)
