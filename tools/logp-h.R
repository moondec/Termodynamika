#| label: fig-ph-r134a
#| fig-cap: "Wykres p-h dla czynnika R134a (log p - h)"
#| warning: false
#| message: false

# install.packages("reticulate")
# library(reticulate)
# py_install("CoolProp") # To zainstaluje bibliotekę termodynamiczną w środowisku R

library(ggplot2)
library(dplyr)
library(reticulate)

# Wskazujemy, że chcemy używać KONKRETNIE tego środowiska
use_virtualenv("termo", required = TRUE)
# Wskazujemy środowisko CONDA o nazwie termo
# use_condaenv("termo", required = TRUE)

# 1. Importowanie biblioteki CoolProp (przez Pythona)
CP <- import("CoolProp.CoolProp")

# Nazwa czynnika (możesz zmienić na "Water", "Ammonia", "CO2")
fluid <- "R134a"

# --- KROK 1: Obliczenie Krzywej Nasycenia (Kopuła) ---
# Generujemy sekwencję temperatur od T_min do T_krytycznej
T_crit <- CP$PropsSI("Tcrit", fluid)
T_min <- 200 # Kelvin (ok -73 C)
T_seq <- seq(T_min, T_crit - 0.5, length.out = 200)

# Ramka danych dla nasycenia
saturation_data <- data.frame(T = T_seq) %>%
  rowwise() %>%
  mutate(
    # Ciśnienie nasycenia [Pa] -> zamiana na [bar]
    p_bar = CP$PropsSI("P", "T", T, "Q", 0, fluid) / 1e5,
    
    # Entalpia cieczy nasyconej (x=0) [J/kg] -> [kJ/kg]
    h_liq = CP$PropsSI("H", "T", T, "Q", 0, fluid) / 1e3,
    
    # Entalpia pary nasyconej (x=1) [J/kg] -> [kJ/kg]
    h_vap = CP$PropsSI("H", "T", T, "Q", 1, fluid) / 1e3
  )

# Przekształcenie danych do formatu długiego (dla ggplot)
dome_data <- data.frame(
  h = c(saturation_data$h_liq, rev(saturation_data$h_vap)),
  p = c(saturation_data$p_bar, rev(saturation_data$p_bar)),
  type = "Krzywa nasycenia"
)

# --- KROK 2: Obliczenie Izoterm (Linii stałej temperatury) ---
# Wybieramy temperatury w Celsjuszach
iso_T_C <- c(-20, 0, 20, 40, 60, 80, 100)
isotherms_data <- data.frame()

for (tc in iso_T_C) {
  Tk <- tc + 273.15
  # Zakres ciśnień dla danej izotermy (od 0.5 bara do 50 barów)
  p_range <- 10^seq(log10(0.5), log10(50), length.out = 50)
  
  # Obliczamy entalpię dla każdego ciśnienia przy stałym T
  # Obsługa błędów (CoolProp może protestować w obszarze dwufazowym przy podawaniu T i P, 
  # ale dla gazu/cieczy jest OK. Tutaj upraszczamy pętlę).
  
  h_vals <- sapply(p_range, function(p_bar) {
    tryCatch({
      CP$PropsSI("H", "T", Tk, "P", p_bar * 1e5, fluid) / 1e3
    }, error = function(e) NA)
  })
  
  temp_df <- data.frame(
    p = p_range,
    h = h_vals,
    T_label = paste0(tc, "°C"),
    group = tc
  )
  isotherms_data <- rbind(isotherms_data, temp_df)
}

# Usuwamy błędne punkty (jeśli CoolProp nie zbiegł)
isotherms_data <- na.omit(isotherms_data)

# --- KROK 3: Rysowanie Wykresu ---

ggplot() +
  # 1. Izotermy (Cienkie szare linie)
  geom_path(data = isotherms_data, aes(x = h, y = p, group = group), 
            color = "gray60", size = 0.5, alpha = 0.7) +
  # Podpisy izoterm (na końcu linii)
  geom_text(data = isotherms_data %>% group_by(group) %>% filter(p == max(p)),
            aes(x = h, y = p, label = T_label), 
            hjust = 0, vjust = 0, color = "gray40", size = 3) +
  
  # 2. Krzywa Nasycenia (Gruba niebieska/czerwona linia)
  # Rysujemy jako jedną zamkniętą ścieżkę lub dwie linie
  geom_path(data = saturation_data, aes(x = h_liq, y = p_bar), 
            color = "blue", size = 1.2) + # Ciecz
  geom_path(data = saturation_data, aes(x = h_vap, y = p_bar), 
            color = "red", size = 1.2) +  # Para
  
  # 3. Punkt Krytyczny
  annotate("point", x = CP$PropsSI("H", "T", T_crit, "Q", 1, fluid)/1e3, 
           y = CP$PropsSI("P", "T", T_crit, "Q", 1, fluid)/1e5, 
           color = "black", size = 3) +
  annotate("text", x = CP$PropsSI("H", "T", T_crit, "Q", 1, fluid)/1e3, 
           y = CP$PropsSI("P", "T", T_crit, "Q", 1, fluid)/1e5 * 1.2, 
           label = "Punkt\nKrytyczny", size = 3, fontface = "bold") +
  
  # 4. Estetyka (Skala Logarytmiczna Y!)
  scale_y_log10(breaks = c(0.5, 1, 2, 5, 10, 20, 40),
                labels = c("0.5", "1", "2", "5", "10", "20", "40")) +
  scale_x_continuous(breaks = seq(100, 500, 50)) +
  
  theme_bw() +
  labs(
    title = paste("Wykres p-h dla czynnika", fluid),
    subtitle = "Niebieska: Ciecz nasycona (x=0) | Czerwona: Para nasycona (x=1)",
    x = "Entalpia właściwa h [kJ/kg]",
    y = "Ciśnienie p [bar] (skala log)"
  ) +
  theme(
    panel.grid.minor = element_blank(),
    plot.title = element_text(face = "bold")
  )