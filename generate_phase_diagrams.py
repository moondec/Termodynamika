
import os
import numpy as np
import matplotlib.pyplot as plt
import CoolProp.CoolProp as CP

# Styl zgodny ze slajdami (theme/ggtheme.R): paleta, stonowana siatka, przezroczyste tło
INK, INK2, GRID, ACCENT = '#1d1d1b', '#5a5753', '#dedbd5', '#8b1e2d'
BLUE, ORANGE, AQUA, VIOLET = '#2a78d6', '#eb6834', '#1baf7a', '#6250d6'
plt.rcParams.update({
    'font.size': 14, 'axes.titlesize': 16, 'axes.titleweight': 'bold',
    'axes.labelsize': 14, 'legend.fontsize': 12,
    'text.color': INK, 'axes.labelcolor': INK2, 'xtick.color': INK2, 'ytick.color': INK2,
    'axes.edgecolor': GRID, 'axes.spines.top': False, 'axes.spines.right': False,
    'grid.color': GRID, 'grid.linewidth': 0.6,
    'figure.facecolor': 'none', 'axes.facecolor': 'none',
    'legend.frameon': False, 'savefig.transparent': True,
})

def plot_h2o():
    fluid = 'Water'
    
    # Critical Point
    Tc = CP.PropsSI('Tcrit', fluid)
    Pc = CP.PropsSI('Pcrit', fluid)
    
    # Triple Point (approximate for plotting range)
    Tt = 273.16
    Pt = 611.657
    
    # 1. Liquid-Vapor Saturation Line (Triple Point to Critical Point)
    T_sat = np.linspace(Tt, Tc, 500)
    P_sat = [CP.PropsSI('P', 'T', t, 'Q', 0, fluid) for t in T_sat]
    
    # 2. Solid-Liquid Melting Line (Approximate)
    # Water has negative slope, but for standard range it's steep.
    # CoolProp standard melting line might be tricky, let's use Simon equation or just Points.
    # For educational visualization, a steep line from Tt upwards is enough, slightly tilting left.
    P_melt = np.linspace(Pt, 100e6, 100) # Up to 100 MPa
    # Melting T is roughly constant ~273.15, actually decreases slightly.
    # T_melt approx: Tt * (P/Pt)^c ... 
    # Let's simple approximate: slightly retreating T
    T_melt = [Tt - (p - Pt)*7.4e-8 for p in P_melt] # Very slight negative slope specific to water

    # 3. Sublimation Line (Solid-Vapor) - Below Triple Point
    T_sub = np.linspace(200, Tt, 100)
    # Use Antoine or similar? Or CoolProp if supported (Ice)
    # CoolProp doesn't always support Ice states well in standard interface without Refprop.
    # We will use simple Clapeyron approx or just extrapolate log-linear.
    # Ln(P) ~ -A/T. Match at Triple Point.
    # L_sub/R ~ 6100K. 
    P_sub = [Pt * np.exp(6100 * (1/Tt - 1/t)) for t in T_sub]

    plt.figure(figsize=(8, 6))
    
    # Plotting
    plt.plot(T_sat, P_sat, color=BLUE, linewidth=2.2, label='Wrzenie (L-G)')
    plt.plot(T_melt, P_melt, color=INK, linewidth=2.2, label='Topnienie (S-L)')
    plt.plot(T_sub, P_sub, color=AQUA, linestyle='--', linewidth=2.2, label='Sublimacja (S-G)')

    # Critical Point
    plt.plot(Tc, Pc, 'o', color=ACCENT, markersize=9)
    plt.text(Tc+8, Pc, 'Punkt krytyczny', verticalalignment='center', color=ACCENT, fontweight='bold')

    # Triple Point
    plt.plot(Tt, Pt, 'o', color=INK, markersize=9)
    plt.text(Tt+8, Pt, 'Punkt potrójny', verticalalignment='top', fontweight='bold')

    # Labels
    plt.text(400, 3e4, 'GAZ (para)', fontsize=15, color=INK2)
    plt.text(320, 1e7, 'CIECZ', fontsize=15, color=INK2)
    plt.text(215, 1e5, 'CIAŁO STAŁE\n(lód)', fontsize=15, color=INK2)

    plt.yscale('log')
    plt.xlabel('Temperatura [K]')
    plt.ylabel('Ciśnienie [Pa]')
    plt.title('Diagram fazowy wody (p–T)')
    plt.grid(True, which="major", ls="-")
    plt.legend(loc='lower right')
    
    output_path = 'img/phase_diagram_h2o.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Generated {output_path}")
    plt.close()

def plot_he4():
    fluid = 'Helium'
    
    # Critical Point
    Tc = CP.PropsSI('Tcrit', fluid)
    Pc = CP.PropsSI('Pcrit', fluid)
    
    # Lambda Point
    T_lambda = 2.17
    P_lambda = 5040 # approx Pa
    
    # 1. Saturation Line
    T_sat = np.linspace(T_lambda, Tc, 200) # From Lambda to Crit (He I)
    P_sat = [CP.PropsSI('P', 'T', t, 'Q', 0, fluid) for t in T_sat]
    
    # Start from 1.5K to avoid low-T EOS issues
    T_sat_II = np.linspace(2.0, T_lambda, 50) 
    P_sat_II = []
    for t in T_sat_II:
        try:
             P_sat_II.append(CP.PropsSI('P', 'T', t, 'Q', 0, fluid))
        except:
             P_sat_II.append(None)
    
    # Filter Nones
    T_sat_II = [t for t, p in zip(T_sat_II, P_sat_II) if p is not None]
    P_sat_II = [p for p in P_sat_II if p is not None]

    # 2. Lambda Line (Transition He I - He II)
    # Approximately vertical or slight slope in p-T?
    # It goes from (2.17 K, 0.05 bar) up to melting curve (1.76 K, 30 bar)
    # Data points approx:
    P_lambda_line = np.linspace(P_lambda, 3e6, 100) # Up to 30 bar
    # He-4 Lambda line is roughly T = 2.17 - log(P)... 
    # Use approximate fit for viz: T = 2.1768 - (P/1e5)*0.013 roughly (very simplified)
    # Actually it slopes to LOWER T at HIGHER P.
    T_lambda_line = np.linspace(2.17, 1.76, 100) # T goes down
    P_lambda_line = np.linspace(5041, 30e5, 100) # P goes up

    # 3. Melting Curve (Solid - Liquid)
    # He4 melting is unique: requires pressure (~25 bar) even at 0K.
    T_melt = np.linspace(1.0, 5.0, 100)
    # P_melt approx: P [bar] = 25 + ...
    # Simplified P = 25e5 + 1e5*(T^1.5) approx
    P_melt = [25e5 + 1.5e5*(t**1.5) for t in T_melt]

    plt.figure(figsize=(8, 6))
    
    # Plotting
    plt.plot(T_sat, P_sat, color=BLUE, linewidth=2.2, label='Wrzenie He I')
    plt.plot(T_sat_II, P_sat_II, color=VIOLET, linestyle='-', linewidth=2.2, label='Wrzenie He II')
    plt.plot(T_melt, P_melt, color=INK, linewidth=2.2, label='Topnienie (S-L)')
    plt.plot(T_lambda_line, P_lambda_line, color=ORANGE, linestyle='--', linewidth=2.2, label='Linia λ')

    # Critical Point
    plt.plot(Tc, Pc, 'o', color=ACCENT, markersize=9)
    plt.text(Tc+0.1, Pc, 'Punkt krytyczny', verticalalignment='center', color=ACCENT, fontweight='bold')

    # Lambda Point
    plt.plot(2.17, 5040, 'o', color=ORANGE, markersize=9)
    plt.text(2.25, 4200, 'Punkt λ', verticalalignment='top', color=ORANGE, fontweight='bold')

    plt.text(4.2, 1e5, 'GAZ', fontsize=15, color=INK2)
    plt.text(2.6, 2e5, 'CIECZ He I\n(normalna)', fontsize=13, color=INK2)
    plt.text(1.05, 2e5, 'CIECZ He II\n(nadciekła)', fontsize=13, color=VIOLET)
    plt.text(3.2, 6e6, 'CIAŁO STAŁE', fontsize=15, color=INK2)

    plt.yscale('log')
    plt.xlabel('Temperatura [K]')
    plt.ylabel('Ciśnienie [Pa]')
    plt.title('Diagram fazowy helu-4 (p–T)')
    plt.ylim(2e3, 1.5e7)
    plt.grid(True, which="major", ls="-")
    plt.legend(loc='lower right')
    
    output_path = 'img/phase_diagram_he4.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Generated {output_path}")
    plt.close()

if __name__ == "__main__":
    if not os.path.exists('img'):
        os.makedirs('img')
    plot_h2o()
    plot_he4()
