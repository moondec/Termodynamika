# install.packages("mcr")
library(mcr)
library(deming)

current <- c(0.15,
           0.25,
           0.35,
           0.55,
           0.7,
           0.8,
           0.92,
           0.95,
           1.05,
           1.1)
voltage <- c(3.8,
           3.4,
           3.15,
           2.8,
           2.3,
           2.1,
           1.75,
           1.55,
           1.35,
           1.2)
# Measurement uncertainties (given by user)
sd_i <- 0.05  # Standard deviation for Current
sd_u <- 0.15  # Standard deviation for Voltage

df <- data.frame(I = current, U = voltage)

# ---------------------------------------------------------
# 2. Regression Analysis (Deming Method)
# ---------------------------------------------------------

# xstd and ystd can be single values or vectors of the same length as data
fit <- deming(U ~ I, data = df, xstd = rep(sd_i, nrow(df)), ystd = rep(sd_u, nrow(df)))

# Extract results
fit_summary <- summary(fit)
r_value <- fit$coefficients[2]        # Slope (Resistance R)
r_error <- fit$se[2]                  # Standard error of slope
intercept <- fit$coefficients[1]      # Intercept (b)
intercept_error <- fit$se[1]          # Standard error of intercept

# Print results in a clean format
cat(sprintf("Estimated Resistance (R): %.4f ± %.4f Ohm\n", r_value, r_error))
cat(sprintf("Intercept (b): %.4f ± %.4f V\n", intercept, intercept_error))

# ---------------------------------------------------------
# 3. Visualization
# ---------------------------------------------------------

plot <- ggplot(df, aes(x = I, y = U)) +
  # Add error bars for both axes
  geom_errorbar(aes(ymin = U - sd_u, ymax = U + sd_u), width = 0.01, color = "gray40") +
  geom_errorbarh(aes(xmin = I - sd_i, xmax = I + sd_i), height = 0.05, color = "gray40") +
  # Add data points
  geom_point(color = "red", size = 2) +
  # Add regression line
  geom_abline(intercept = intercept, slope = r_value, color = "blue", linewidth = 1) +
  # Formatting
  labs(
    title = "Charakterystyka prądowo-napięciowa",
    subtitle = sprintf("R = %.3f ± %.3f Ω", r_value, r_error),
    x = "Natężenie prądu I [A]",
    y = "Napięcie U [V]"
  ) +
  theme_minimal()

print(plot)

# Uproszczone podejście
ggplot(df) + theme_bw() + geom_point(aes(x=I,y=U)) + 
  geom_smooth(aes(x=I,y=U),method = 'lm') +
  geom_errorbar(aes(x=I,y=U,ymin=U-sd_u,ymax=U+sd_u,xmin=I-sd_i,xmax=I+sd_i)) +
  geom_errorbarh(aes(x=I,y=U,ymin=U-sd_u,ymax=U+sd_u,xmin=I-sd_i,xmax=I+sd_i)) +
  # geom_smooth(aes(x=I-sd_i,y=U),method = 'lm',se = FALSE,col="red") + 
  # geom_smooth(aes(x=I+sd_i,y=U),method = 'lm',se = FALSE,col = 'green') +
  # geom_smooth(aes(x=I,y=U-sd_u),method = 'lm',se = FALSE,col="yellow") + 
  # geom_smooth(aes(x=I,y=U+sd_u),method = 'lm',se = FALSE,col = 'brown') +
  geom_smooth(aes(x=I-sd_i,y=U-sd_u),method = 'lm',se = FALSE,col="orange") +
  geom_smooth(aes(x=I+sd_i,y=U+sd_u),method = 'lm',se = FALSE,col = 'magenta') +
  # geom_smooth(aes(x=I-sd_i,y=U+sd_u),method = 'lm',se = FALSE,col="forestgreen") + 
  # geom_smooth(aes(x=I+sd_i,y=U-sd_u),method = 'lm',se = FALSE,col = 'navy') +
  geom_smooth(aes(x=I+sd_i,y=U+sd_u),method = 'lm',se = FALSE,col="#912") + 
  geom_smooth(aes(x=I-sd_i,y=U-sd_u),method = 'lm',se = FALSE,col = '#409')
