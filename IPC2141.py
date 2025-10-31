# IPC2141.py

import sympy as sp  #
import numpy as np
import math

class IPC2141Microstrip:
    def __init__(self, er, h, t):
        """
        er : relative permittivity (εr)
        h  : dielectric height (m)
        t  : trace thickness (m)
        """
        self.er = float(er)
        self.h = float(h)
        self.t = float(t)

    def analyze(self, w):
        """
        Given trace width w (m), returns Z0 (Ω) using IPC-2141 formula.
        """
        if w <= 0:
            raise ValueError("Width must be > 0")
        Z0 = (87.0 / math.sqrt(self.er + 1.41)) * math.log((5.98 * self.h) / (0.8 * w + self.t))
        print("-------------------------------IPC2141 Analyze-----------------------------")
        return float(Z0)

    def synthesize(self, Z0_target, initial_guess_w=None):
        """
        Returns the trace width w (m) for a given target impedance (Ω).
        Uses both analytical estimation and fallback to sympy.nsolve if needed.
        """

        if Z0_target <= 0:
            raise ValueError("Target impedance must be > 0")

        # --- Analytical first guess (approx inverse of IPC2141 equation) ---
        try:
            w_est = ((5.98 * self.h) / math.exp(Z0_target * math.sqrt(self.er + 1.41) / 87.0)) - (self.t / 0.8)
            if w_est <= 0:
                w_est = self.h * 0.5  # fallback to reasonable value
        except Exception:
            w_est = self.h * 0.5

        # --- Use nsolve for refinement ---
        w_sym = sp.symbols('w', positive=True, real=True)
        expr = (87 / sp.sqrt(self.er + 1.41)) * sp.log((5.98 * self.h) / (0.8 * w_sym + self.t)) - Z0_target

        try:
            sol = sp.nsolve(expr, w_sym, w_est)
            w_val = float(sol)
        except Exception:
            # fallback to iterative refinement
            w_val = w_est
            for _ in range(50):
                try:
                    z = self.analyze(w_val)
                    if abs(z - Z0_target) < 1e-3:
                        break
                    # simple gradient step
                    if z > Z0_target:
                        w_val *= 1.02
                    else:
                        w_val *= 0.98
                except Exception:
                    break

        if w_val <= 0:
            raise RuntimeError("Failed to find valid width for target Z0.")

        return float(w_val)
if __name__ == "__main__":
    # --- Start of Test Case (Analyze -> Synthesize) ---

    # 1. Define realistic PCB parameters
    # Common FR-4 dielectric constant
    er_val = 4.4
    # Dielectric height: 6.0 mils (0.006 inches)
    h_mils = 6.0
    h_val = h_mils * 0.001 * 0.0254  # convert mils to meters
    # Trace thickness: 1 oz copper (approx 35 um)
    t_um = 35.0
    t_val = t_um * 1e-6               # convert micrometers to meters

    # 2. Create an instance of the class
    print("==================================================")
    print("      IPC2141 Microstrip Test Case (A -> S)")
    print("==================================================")
    print("Initializing calculator with parameters:")
    print(f"  Relative Permittivity (er): {er_val}")
    print(f"  Dielectric Height (h):   {h_val * 1e3:.4f} mm ({h_mils:.1f} mils)")
    print(f"  Trace Thickness (t):     {t_val * 1e6:.2f} um ({t_um / 35.0:.1f} oz Cu)")
    
    ms = IPC2141Microstrip(er=er_val, h=h_val, t=t_val)

    # 3. Test Analyze: Start with a known width
    # Let's use an initial width of 11.5 mils
    w_initial_mils = 11.5
    w_initial = w_initial_mils * 0.001 * 0.0254 # convert mils to meters
    
    print("\n--- Test 1: Analyze ---")
    print(f"Analyzing impedance for a known initial width w = {w_initial * 1e3:.4f} mm ({w_initial_mils:.2f} mils)...")
    
    try:
        # Note: The analyze() method prints its own "---IPC2141 Analyze---" line
        Z0_calculated = ms.analyze(w_initial)
        print(f"  > Calculated Z0: {Z0_calculated:.4f} Ohms")

        # 4. Test Synthesize: Use the analyzed Z0 as the target
        print("\n--- Test 2: Synthesize (Self-Consistency Check) ---")
        print(f"Synthesizing width for target Z0 = {Z0_calculated:.4f} Ohms...")
        
        w_synthesized = ms.synthesize(Z0_calculated)
        w_synthesized_mils = (w_synthesized / 0.0254) * 1000.0
        
        print(f"  > Synthesized Width (w): {w_synthesized * 1e3:.4f} mm ({w_synthesized_mils:.2f} mils)")

        # 5. Verification
        print("\n--- Verification ---")
        error_w = abs(w_synthesized - w_initial)
        error_w_percent = (error_w / w_initial) * 100.0
        
        print(f"  Initial Width:    {w_initial * 1e3:.6f} mm")
        print(f"  Synthesized Width: {w_synthesized * 1e3:.6f} mm")
        print(f"  Absolute Error (width): {error_w:.2e} m")
        print(f"  Percentage Error:       {error_w_percent:.4f} %")

        if error_w < 1e-9: # Expecting very high precision
            print("  > \u2705 PASS: Synthesize recovered the initial width.")
        else:
            print("  > \u274C FAIL: Synthesize did NOT recover the initial width.")
    
    except Exception as e:
        print(f"\nAn error occurred during the test: {e}")

    print("==================================================")
    # --- End of Test Case ---