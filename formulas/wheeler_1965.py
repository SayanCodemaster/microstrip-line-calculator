import math
import sympy as sp

class Wheeler_1965:
    def __init__(self, er, h, freq):
        self.er = er             # relative permittivity
        self.h = h               # substrate height (meters)
        self.freq = freq         # frequency in GHz

    def Analyze(self, w, l):
        # w, l expected in meters
        Z0 = self._calculate_Z0(w)
        elec_length = self._calculate_elec_length(w, l)
        return float(Z0), float(elec_length)

    def Synthesize(self, Z0_target, elec_length_target):
        # Solve nonlinear equations symbolically/numerically for Wheeler 1965
        w, l = sp.symbols("w l", positive=True, real=True)
        Eeff = ((self.er + 1) / 2) + ((self.er - 1) / 2) * (1 + 12 * (self.h / w))**(-0.5)
        U = w / self.h
        Z0_expr = sp.Piecewise(
            ((60 / sp.sqrt(Eeff)) * sp.log((8 / U) + (U / 4)), U <= 3.3),
            ((120 * sp.pi) / (sp.sqrt(Eeff) * (U + 1.393 + 0.667 * sp.log(U + 1.444))), True)
        )

        c = 2.99792458e8
        f_hz = self.freq * 1e9
        lambda_g = c / (f_hz * sp.sqrt(Eeff))
        theta_expr = (360 * l) / lambda_g

        try:
            solutions = sp.nsolve(
                [Z0_expr - Z0_target, theta_expr - elec_length_target],
                [w, l],
                [self.h, 0.03]
            )
            w_val = float(solutions[0])
            l_val = float(solutions[1])
            return w_val, l_val
        except Exception as e:
            raise RuntimeError(f"Synthesize failed: {e}")

    def _calculate_Z0(self, w):
        U = w / self.h
        Eeff = self._calculate_eff(w)
        if U <= 3.3:
            return (60 / math.sqrt(Eeff)) * math.log((8 / U) + (U / 4))
        else:
            return (120 * math.pi) / (math.sqrt(Eeff) * (U + 1.393 + 0.667 * math.log(U + 1.444)))

    def _calculate_elec_length(self, w, L):
        c = 2.99792458e8
        f_hz = self.freq * 1e9
        Eeff = self._calculate_eff(w)
        lambda_g = c / (f_hz * math.sqrt(Eeff))
        theta_deg = (360 * L) / lambda_g
        return theta_deg

    def _calculate_eff(self, w):
        return ((self.er + 1) / 2) + ((self.er - 1) / 2) * (1 + 12 * (self.h / w))**-0.5

    # Optional: Round-trip test to verify correctness
    def round_trip_test(self, Z0_in, elecLen_in):
        w, l = self.Synthesize(Z0_in, elecLen_in)
        Z0_out, elecLen_out = self.Analyze(w, l)
        print(f"Input to Synthesize: Z0={Z0_in}, ElecLen={elecLen_in}")
        print(f"Synthesize outputs: w={w:.6f} m, l={l:.6f} m")
        print(f"Analyze outputs: Z0={Z0_out:.6f}, ElecLen={elecLen_out:.6f}")
        return (Z0_out, elecLen_out), (w, l)

