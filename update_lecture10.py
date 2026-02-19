
import os

file_path = "Wyklady/10_Obiegi_Parowe.qmd"
with open(file_path, "r") as f:
    lines = f.readlines()

# Identify start and end of the Python chunk to replace
# We look for the comment "# Sawtooth Regeneration (Specific User Constraints)"
# And the closing backticks.

target_comment = "# Sawtooth Regeneration (Specific User Constraints)"
start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if target_comment in line:
        start_idx = i
    # Find closing ticks after the start_idx
    if start_idx != -1 and "```" in line and i > start_idx:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    # Found the block constraints.
    # Find the opening ```{python} above the start_idx
    chunk_start = -1
    for k in range(start_idx, -1, -1):
        if "```{python}" in lines[k]:
            chunk_start = k
            break
            
    if chunk_start != -1:
        # New Content
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
# Intersection: s_vap(T_start) = s1
# Custom T_start
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

# Bleed Temperatures (Equal Steps)
T_steps = np.linspace(T_bleed1, T_cond, 4) # T_b1, T_b2, T_b3, T_cond
# Just pick T_b1, T_b2, T_b3
Ts = T_steps[0:3]

# ---- STEAM PATH (ORANGE) ----
steam_path = []
steam_arrows = [] # Green horizontal arrows (representing q_r leaving)

curr_s = s1
curr_T = T1

# Expansion to first bleed
steam_path.append({'x': curr_s, 'y': curr_T, 'xend': curr_s, 'yend': Ts[0], 'color': 'orange', 'type': 'exp'})
curr_T = Ts[0]

for i, T_lev in enumerate(Ts):
    # Determine Extraction Delta S
    dS = 0.5
    next_s = curr_s - dS
    
    # Horizontal Orange Segment (Extraction/State Change)
    steam_path.append({'x': curr_s, 'y': T_lev, 'xend': next_s, 'yend': T_lev, 'color': 'orange', 'type': 'extr'})
    
    # Green Arrow Head pointing DOWN from Middle
    mid_s = (curr_s + next_s)/2
    steam_arrows.append({'x': mid_s, 'y': T_lev, 'xend': mid_s, 'yend': T_lev - 40, 'label': "q[r]"})
    
    curr_s = next_s
    
    # Vertical Expansion to Next Level
    if i < 2:
        next_T_lev = Ts[i+1]
        steam_path.append({'x': curr_s, 'y': T_lev, 'xend': curr_s, 'yend': next_T_lev, 'color': 'orange', 'type': 'exp'})
        curr_T = next_T_lev
    else:
        # Final Expansion to Condenser
        steam_path.append({'x': curr_s, 'y': T_lev, 'xend': curr_s, 'yend': T_cond, 'color': 'orange', 'type': 'exp'})
        curr_T = T_cond

# Condenser Line
s3_liq = CP.PropsSI('S', 'P', p_cond, 'Q', 0, fluid) / 1000
steam_path.append({'x': curr_s, 'y': T_cond, 'xend': s3_liq, 'yend': T_cond, 'color': 'cyan3', 'type': 'cond'})

# ---- WATER PATH (RED) ----
# Staircase along Sat Line corresponding to T steps
water_path = []
water_arrows = [] # Green arrow incoming

# T levels (Low to High): T_cond -> Ts[2] -> Ts[1] -> Ts[0] -> T_boiler
# Ts is T_b1 (High), T_b2, T_b3 (Low).
T_w_levels = [T_cond, Ts[2], Ts[1], Ts[0], CP.PropsSI('T', 'P', p_boiler, 'Q', 0, fluid)] 

for i in range(len(T_w_levels)-1):
    T_curr = T_w_levels[i]
    T_next = T_w_levels[i+1]
    
    # Saturation entropy at these T
    s_curr = CP.PropsSI('S', 'T', T_curr, 'Q', 0, fluid)/1000
    s_next = CP.PropsSI('S', 'T', T_next, 'Q', 0, fluid)/1000
    
    # Segment: Curve along Saturation Line represents heating
    water_path.append({'x': s_curr, 'y': T_curr, 'xend': s_next, 'yend': T_next, 'color': 'red', 'type': 'heat'})
    
    # Arrow: Pointing DOWN onto this segment midpoint
    mid_s = (s_curr + s_next)/2
    mid_T = (T_curr + T_next)/2
    
    if i < 3: # correspond to 3 bleeds
        water_arrows.append({'x': mid_s, 'y': mid_T + 40, 'xend': mid_s, 'yend': mid_T, 'label': "q[r]"})

# Boiler Path
s_sat_boil = CP.PropsSI('S', 'P', p_boiler, 'Q', 0, fluid)/1000
s_sat_vap = CP.PropsSI('S', 'P', p_boiler, 'Q', 1, fluid)/1000
water_path.append({'x': s_sat_boil, 'y': T_w_levels[-1], 'xend': s_sat_vap, 'yend': T_w_levels[-1], 'color': 'red', 'type': 'evap'})
water_path.append({'x': s_sat_vap, 'y': T_w_levels[-1], 'xend': s1, 'yend': T1, 'color': 'red', 'type': 'sup'})

df_steam = pd.DataFrame(steam_path)
df_s_arr = pd.DataFrame(steam_arrows)
df_water = pd.DataFrame(water_path)
df_w_arr = pd.DataFrame(water_arrows)

pts = pd.DataFrame({
    'label': ['1', '2', '3', '4'],
    's': [s1, curr_s, s3_liq, s_sat_boil],
    'T': [T1, T_cond, T_cond, T_w_levels[-1]]
})
```
"""
        new_lines = new_content.split('\n')
        new_lines = [l + '\n' for l in new_lines]
        
        # Replace the chunk
        # end_idx is the line with ```. We want to replace it too (it is in NEW content as last line).
        # Actually in new_content above, I included ``` at the end.
        final_lines = lines[:chunk_start] + new_lines + lines[end_idx+1:]
        
        with open(file_path, "w") as f:
            f.writelines(final_lines)
        print("Updated successfully.")

    else:
        print("Could not find start of chunk.")
else:
    print("Could not find block identifier comment.")
