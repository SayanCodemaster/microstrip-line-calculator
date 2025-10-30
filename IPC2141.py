# IPC2141.py

import sympy as sp  # <-- **FIX 5: Add this missing import**
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