# Wspólny styl wykresów ggplot2 dla slajdów (wykłady i ćwiczenia).
# Użycie w chunku setup:  source("../theme/ggtheme.R"); theme_set(theme_slides())
#
# Paleta kategoryczna (kolejność ma znaczenie – sąsiednie kolory są rozróżnialne
# także przy zaburzeniach widzenia barw): niebieski, pomarańczowy, morski, żółty,
# różowy, zielony, fioletowy, czerwony.
pal_slides <- c("#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                "#e87ba4", "#008300", "#6250d6", "#e34948")

col_ink    <- "#1d1d1b"   # tekst główny
col_ink2   <- "#5a5753"   # tekst pomocniczy (osie, adnotacje)
col_grid   <- "#dedbd5"   # siatka (cienka, stonowana)
col_accent <- "#8b1e2d"   # akcent prezentacji (bordo)

theme_slides <- function(base_size = 16) {
  ggplot2::theme_minimal(base_size = base_size) +
    ggplot2::theme(
      text              = ggplot2::element_text(colour = col_ink),
      plot.background   = ggplot2::element_rect(fill = "transparent", colour = NA),
      panel.background  = ggplot2::element_rect(fill = "transparent", colour = NA),
      panel.grid.minor  = ggplot2::element_blank(),
      panel.grid.major  = ggplot2::element_line(colour = col_grid, linewidth = 0.4),
      axis.title        = ggplot2::element_text(colour = col_ink2),
      axis.text         = ggplot2::element_text(colour = col_ink2),
      plot.title        = ggplot2::element_text(face = "bold", hjust = 0),
      plot.subtitle     = ggplot2::element_text(colour = col_ink2),
      legend.position   = "bottom",
      legend.background = ggplot2::element_rect(fill = "transparent", colour = NA),
      legend.key        = ggplot2::element_rect(fill = "transparent", colour = NA),
      legend.text       = ggplot2::element_text(colour = col_ink2),
      plot.margin       = ggplot2::margin(6, 10, 6, 6)
    )
}
