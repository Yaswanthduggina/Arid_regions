# Why the Current ETo Calculation is Scientificaly Incorrect

Based on the FAO-56 Penman-Monteith standard, there are four major reasons why the calculations in `scripts/calc_ETo_all_cities.py` are producing wrong results for your hourly data.

---

### 1. Wrong Aerodynamic Constant ($C_d$)
**The Error**: You are using a fixed value of **0.34**.
- **The Science**: 0.34 is only for **daily** (24-hour) calculations. 
- **For Hourly**: The atmosphere behaves differently when the sun is up versus when it is down.
  - **Daytime**: Should be **0.24**.
  - **Nighttime**: Should be **0.96**.
- **Impact**: Using 0.34 at night underestimates the resistance, and using it in the day overestimates it.

### 2. Incorrect Soil Heat Flux ($G$)
**The Error**: You have set `G = 0`.
- **The Science**: While $G$ is approximately 0 over a full 24-hour day (heat goes in, heat comes out), it is **very large** during individual hours.
  - **Daytime**: $G$ should be about $0.1 \times R_n$ (soil absorbing heat).
  - **Nighttime**: $G$ should be about $0.5 \times R_n$ (soil releasing heat).
- **Impact**: Ignoring $G$ leads to a massive energy balance error in your hourly ETo values.

### 3. Extraterrestrial Radiation ($R_a$) Math Error
**The Error**: The manual code uses the midpoint solar angle (`omega`) in a term that should represent the 1-hour duration ($\pi/12$).
- **Impact**: This causes the "maximum possible solar radiation" calculation to be mathematically skewed, which effectively makes your $R_{nl}$ (net longwave radiation) calculation wrong.

### 4. Unit Conversion Danger (Documentation Mismatch)
**The Fact**: Your project notes say the units are $W/m^2$, but the data you downloaded from NASA is actually $MJ/m^2/hr$.
- **Impact**: Even though the current script "got lucky" by using the raw value, any future script (like the draft `process_data.py` in your notes) that tries to convert $W/m^2 \to MJ$ will divide by ~277, making your radiation effectively zero and your ETo results 100% wrong.

---

## Conclusion
To fix this, you must:
1.  **Stop** fixed constants (0.34).
2.  **Start** using `if Rs > 0` logic to switch constants for day and night.
3.  **Correct** the $R_a$ formula to follow FAO-56 Equation 28 exactly.
