
library(ggplot2)
library(dplyr)
library(reticulate)

# Setup środowiska (zgodnie z tools/logp-h.R)
tryCatch({
  use_virtualenv("termo", required = TRUE)
}, error = function(e) {
  message("Nie udało się załadować venv 'termo', próbuję standardowy import...")
})

CP <- import("CoolProp.CoolProp")
fluid <- "R134a"

# --- 1. TŁO (Krzywa nasycenia i Izotermy) ---
# (Uproszczona wersja z logp-h.R)

T_crit <- CP$PropsSI("Tcrit", fluid)
T_seq <- seq(180, T_crit - 0.5, length.out = 300) # szerszy zakres dla R134a

# Ramka danych dla nasycenia
sat_data <- data.frame(T = T_seq) %>%
  rowwise() %>%
  mutate(
    p_bar = CP$PropsSI("P", "T", T, "Q", 0, fluid) / 1e5,
    h_liq = CP$PropsSI("H", "T", T, "Q", 0, fluid) / 1e3,
    h_vap = CP$PropsSI("H", "T", T, "Q", 1, fluid) / 1e3
  ) %>% ungroup()

# --- 2. DANE DO OBIEGÓW ---

calc_cycle <- function(To_C, Tk_C, label_suffix="") {
  # Parametry
  To <- To_C + 273.15
  Tk <- Tk_C + 273.15
  
  # 1. Punkt 1: Para nasycona suche na ssaniu
  p1 <- CP$PropsSI("P", "T", To, "Q", 1, fluid)
  h1 <- CP$PropsSI("H", "T", To, "Q", 1, fluid)
  s1 <- CP$PropsSI("S", "T", To, "Q", 1, fluid)
  
  # 2. Punkt 2: Sprężanie izentropowe
  p2 <- CP$PropsSI("P", "T", Tk, "Q", 0, fluid) # Ciśnienie skraplania
  s2 <- s1
  h2 <- CP$PropsSI("H", "P", p2, "S", s2, fluid)
  t2 <- CP$PropsSI("T", "P", p2, "S", s2, fluid) - 273.15
  
  # 3. Punkt 3: Rozprężanie (Skraplanie do cieczy nasyconej)
  p3 <- p2
  h3 <- CP$PropsSI("H", "P", p3, "Q", 0, fluid)
  # t3 = Tk_C
  
  # 4. Punkt 4: Dławienie izentalpowe
  h4 <- h3
  p4 <- p1
  
  # Tworzenie ramki dla linii (zamknięty obieg 1-2-3-4-1)
  df <- data.frame(
    point = c("1", "2", "3", "4", "1"),
    h = c(h1, h2, h3, h4, h1) / 1e3,
    p = c(p1, p2, p3, p4, p1) / 1e5,
    label = paste0(c("1", "2", "3", "4", ""), label_suffix)
  )
  return(df)
}

cycle1 <- calc_cycle(2, 40, "")      # Zad 6.1 (Standard)
cycle2 <- calc_cycle(2, 50, "'")     # Zad 6.5 (Zły skraplacz)

# --- 3. RYSOWANIE ---

p <- ggplot() +
  # Krzywa nasycenia
  geom_path(data = sat_data, aes(x = h_liq, y = p_bar), color = "blue", linewidth = 1) +
  geom_path(data = sat_data, aes(x = h_vap, y = p_bar), color = "red", linewidth = 1) +
  
  # Obieg 1 (Standard - Zielony)
  geom_path(data = cycle1, aes(x = h, y = p), color = "#2ca02c", linewidth = 1.5,
            arrow = arrow(length = unit(0.4, "cm"), ends = "last", type = "closed")) +
  geom_point(data = cycle1[1:4,], aes(x = h, y = p), size = 4, color = "#2ca02c") +
  geom_text(data = cycle1[1:4,], aes(x = h, y = p, label = label), 
            vjust = -1, hjust = -0.5, size = 8, fontface = "bold", color = "#2ca02c") +
  
  # Obieg 2 (Zły - Czerwony/Pomarańczowy przerywany)
  geom_path(data = cycle2, aes(x = h, y = p), color = "#d62728", linewidth = 1.2, linetype = "dashed") +
  # Punkty zmienione (2' i 3' i 4')
  geom_point(data = cycle2[2:4,], aes(x = h, y = p), size = 4, color = "#d62728") +
  geom_text(data = cycle2[2:4,], aes(x = h, y = p, label = label), 
            vjust = 1.5, hjust = 1, size = 8, fontface = "bold", color = "#d62728") +

  # Estetyka
  scale_y_log10(breaks = c(1, 2, 5, 10, 20, 30, 40), limits = c(1, 40)) +
  scale_x_continuous(limits = c(150, 500)) +
  labs(
    title = "Porównanie Obiegów Chłodniczych (R134a)",
    subtitle = "Zielony: Standard (tk=40°C) | Czerwony: Zad 6.5 (tk=50°C)",
    x = "Entalpia h [kJ/kg]",
    y = "Ciśnienie p [bar]"
  ) +
  theme_bw(base_size = 18) + # Powiększona czcionka
  theme(
    plot.title = element_text(size = 24, face = "bold"),
    axis.title = element_text(size = 20),
    axis.text = element_text(size = 16)
  )

# Zapis do pliku
output_path <- "../img/cycles_comparison.png"
ggsave(output_path, plot = p, width = 12, height = 8, dpi = 150)
message("Wykres zapisano w: ", output_path)
