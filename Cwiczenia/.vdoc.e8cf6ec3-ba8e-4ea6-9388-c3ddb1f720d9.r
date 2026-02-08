#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#| echo: true
#| fig-height: 5
library(ggplot2)

V <- 5       # m3
T_C <- 25    # st. C
T_K <- T_C + 273.15
R <- 287     # J/kgK

# Zakres ciśnień manometrycznych [bar]
p_man_bar <- seq(6, 10, by=0.1)
p_abs_Pa <- (p_man_bar * 100000) + 100000

# Masa gazu [kg]
m_gas <- (p_abs_Pa * V) / (R * T_K)

df <- data.frame(p_man = p_man_bar, m = m_gas)

ggplot(df, aes(x=p_man, y=m)) +
  geom_line(color="blue", size=2) +
  geom_point(aes(x=8.5, y=55.5), color="red", size=5) +
  ggtitle("Masa powietrza w zbiorniku 5m3 (25 st. C)") +
  xlab("Ciśnienie manometryczne [bar]") +
  ylab("Masa powietrza [kg]") +
  theme_minimal(base_size=18)
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
