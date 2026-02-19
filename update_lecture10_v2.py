
import os

file_path = "Wyklady/10_Obiegi_Parowe.qmd"
with open(file_path, "r") as f:
    lines = f.readlines()

# TARGET: Python block for "Sawtooth Regeneration V2"
target_comment = "# Sawtooth Regeneration V2 (Double Sawtooth)"
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if target_comment in line:
        start_idx = i
    if start_idx != -1 and "```" in line and i > start_idx:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Find start of chunk
    chunk_start = -1
    for k in range(start_idx, -1, -1):
        if "```{python}" in lines[k]:
            chunk_start = k
            break
            
    if chunk_start != -1:
        # Construct NEW Python Content
        # Arrows:
        # Water (Left): "unieś o 25". Original: y=mid_T+40, yend=mid_T.
        # Interpretation: Move AWAY from line. yend=mid_T+25. y=mid_T+65.
        # Steam (Right): "opuść o 10". Original: y=T_lev, yend=T_lev-40.
        # Interpretation: Move AWAY from line. y=T_lev-10. yend=T_lev-50.
        
        # Labels:
        # Old 1 (Main) -> 3
        # Old 2 (Turbine End) -> 4
        # Old 3 (Cond Out) -> 1
        # Old 4 (Boiler In) -> 2
        
        new_content = """```{python}
#| echo: false
#| warning: false
#| message: false

# Sawtooth Regeneration V2 (Double Sawtooth)
# Concept: Feedwater (left, liq) is heated (Staircase) by Steam (Staircase)
# Green Arrows point DOWN from Steam Steps to Water Steps.

p_cond = 0.1 * 1e5    # 0.1 bar
p_boiler = 50 * 1e5   # 50 bar
T_max = 500 + 273.15  # 500C

# 1. Main Expansion Line (1 -> 2)
# 1: Superheated Steam
h1 = CP.PropsSI('H', 'P', p_boiler, 'T', T_max, fluid)
s1 = CP.PropsSI('S', 'P', p_boiler, 'T', T_max, fluid) / 1000
T1 = T_max

# 2. Bleed logic (3 bleeds)
def find_T_sat_vap(s_target, T_high, T_low):
    for i in range(50):
        T_mid = (T_high + T_low) / 2
        try:
            s_mid = CP.PropsSI('S', 'T', T_mid, 'Q', 1, fluid)/1000
            if abs(s_mid - s_target) < 0.001:
                return T_mid
            elif s_mid > s_target:
                T_low = T_mid
            else:
                T_high = T_mid
        except:
            return T_high
    return (T_high + T_low) / 2

T_crit = CP.PropsSI('Tcrit', fluid)
T_tri = CP.PropsSI('Tmin', fluid)
T_bleed1 = find_T_sat_vap(s1, T_crit-1, T_tri+1)

T_cond = CP.PropsSI('T', 'P', p_cond, 'Q', 0, fluid)

# Bleed Temperatures
T_steps = np.linspace(T_bleed1, T_cond, 4) 
Ts = T_steps[0:3]

# ---- STEAM PATH (ORANGE) ----
steam_path = []
steam_arrows = [] 

curr_s = s1
curr_T = T1

# Expansion to first bleed
steam_path.append({'x': curr_s, 'y': curr_T, 'xend': curr_s, 'yend': Ts[0], 'color': 'orange', 'type': 'exp'})
curr_T = Ts[0]

for i, T_lev in enumerate(Ts):
    dS = 0.5
    next_s = curr_s - dS
    
    # Horizontal
    steam_path.append({'x': curr_s, 'y': T_lev, 'xend': next_s, 'yend': T_lev, 'color': 'orange', 'type': 'extr'})
    
    # Arrow: Pointing DOWN, shifted DOWN by 10 (gap)
    mid_s = (curr_s + next_s)/2
    # Start at T_lev - 10, End at T_lev - 50 (Length 40)
    steam_arrows.append({'x': mid_s, 'y': T_lev - 10, 'xend': mid_s, 'yend': T_lev - 50, 'label': "q[r]"})
    
    curr_s = next_s
    
    # Vertical
    if i < 2:
        next_T_lev = Ts[i+1]
        steam_path.append({'x': curr_s, 'y': T_lev, 'xend': curr_s, 'yend': next_T_lev, 'color': 'orange', 'type': 'exp'})
        curr_T = next_T_lev
    else:
        steam_path.append({'x': curr_s, 'y': T_lev, 'xend': curr_s, 'yend': T_cond, 'color': 'orange', 'type': 'exp'})
        curr_T = T_cond

# Condenser Line
s3_liq = CP.PropsSI('S', 'P', p_cond, 'Q', 0, fluid) / 1000
steam_path.append({'x': curr_s, 'y': T_cond, 'xend': s3_liq, 'yend': T_cond, 'color': 'cyan3', 'type': 'cond'})

# ---- WATER PATH (RED) ----
water_path = []
water_arrows = [] 

T_w_levels = [T_cond, Ts[2], Ts[1], Ts[0], CP.PropsSI('T', 'P', p_boiler, 'Q', 0, fluid)] 

for i in range(len(T_w_levels)-1):
    T_curr = T_w_levels[i]
    T_next = T_w_levels[i+1]
    
    s_curr = CP.PropsSI('S', 'T', T_curr, 'Q', 0, fluid)/1000
    s_next = CP.PropsSI('S', 'T', T_next, 'Q', 0, fluid)/1000
    
    water_path.append({'x': s_curr, 'y': T_curr, 'xend': s_next, 'yend': T_next, 'color': 'red', 'type': 'heat'})
    
    mid_s = (s_curr + s_next)/2
    mid_T = (T_curr + T_next)/2
    
    if i < 3: 
        # Arrow: Pointing DOWN, shifted UP by 25 (gap from line)
        # End at mid_T + 25. Start at mid_T + 65. (Length 40)
        water_arrows.append({'x': mid_s, 'y': mid_T + 65, 'xend': mid_s, 'yend': mid_T + 25, 'label': "q[r]"})

# Boiler Path
s_sat_boil = CP.PropsSI('S', 'P', p_boiler, 'Q', 0, fluid)/1000
s_sat_vap = CP.PropsSI('S', 'P', p_boiler, 'Q', 1, fluid)/1000
water_path.append({'x': s_sat_boil, 'y': T_w_levels[-1], 'xend': s_sat_vap, 'yend': T_w_levels[-1], 'color': 'red', 'type': 'evap'})
water_path.append({'x': s_sat_vap, 'y': T_w_levels[-1], 'xend': s1, 'yend': T1, 'color': 'red', 'type': 'sup'})

df_steam = pd.DataFrame(steam_path)
df_s_arr = pd.DataFrame(steam_arrows)
df_water = pd.DataFrame(water_path)
df_w_arr = pd.DataFrame(water_arrows)

# Points Renumbered
# s1 (Main Steam) -> 3
# curr_s (Turbine End) -> 4
# s3_liq (Cond Out) -> 1
# s_sat_boil (Boiler In) -> 2
pts = pd.DataFrame({
    'label': ['3', '4', '1', '2'],
    's': [s1, curr_s, s3_liq, s_sat_boil],
    'T': [T1, T_cond, T_cond, T_w_levels[-1]]
})
```
"""
        new_lines = new_content.split('\n')
        new_lines = [l + '\n' for l in new_lines]
        
        final_lines = lines[:chunk_start] + new_lines + lines[end_idx+1:]
        
        with open(file_path, "w") as f:
            f.writelines(final_lines)
        print("Updated successfully.")

    else:
        print("Could not find start of chunk.")
else:
    print("Could not find block identifier constraint.")
