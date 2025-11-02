import sympy as sp
import numpy as np

class SchneiderMicrostrip:
    def __init__(self, er, h, freq):
        """
        er   : relative permittivity εᵣ of substrate
        h    : substrate height (m)
        freq : frequency in GHz (for electrical length, if needed)
        """
        self.er   = er
        self.h    = h
        self.freq = freq * 1e9  # convert GHz to Hz

    def analyze(self, w, l):
        """
        Given width w (m) and physical length l (m), returns
        (Z0, electrical_length_deg) using Schneider formulas (low‑freq approx).
        """
        Z0 = self._calc_Z0(w)
        theta_deg = self._calc_elec_length(w, l)
        return float(Z0), float(theta_deg)

    def synthesize(self, Z0_target, elec_length_deg_target):
        """
        Solve for w and l given target Z0 and target electrical length (in degrees).
        Uses sympy nsolve.
        """
        w_sym, l_sym = sp.symbols('w_sym l_sym', positive=True, real=True)
        Z0_expr = self._Z0_expr_symbolic(w_sym)
        theta_expr = self._theta_expr_symbolic(w_sym, l_sym)

        sol = sp.nsolve([
            Z0_expr - Z0_target,
            theta_expr - elec_length_deg_target
        ], [w_sym, l_sym], [self.h, (self.freq > 0) and (sp.sqrt(1/self.er) * (3e8/self.freq) * elec_length_deg_target/360) or self.h])

        w_calc = float(sol[0])
        l_calc = float(sol[1])
        return w_calc, l_calc

    def _calc_Z0(self, w):
        """Numeric Z0 using Schneider’s approximation (quasi‑static)"""
        # Using the same functional form as Wheeler/Hammerstad but with Schneider's ε_eff
        Eeff = self._calc_eff(w)
        U = w / self.h
        if U <= 1:
            z0 = (60.0 / np.sqrt(Eeff)) * np.log( (8.0 / U) + (U / 4.0) )
        else:
            z0 = (120.0*np.pi) / ( np.sqrt(Eeff) * ( U + 1.393 + 0.667*np.log(U + 1.444) ) )
        return z0

    def _calc_eff(self, w):
        """Numeric effective permittivity ε_eff using Schneider’s static‑TEM approx."""
        # Schneider’s static formula (very similar to √(1+12h/w) form) 
        U = w / self.h
        return (self.er + 1)/2 + (self.er - 1)/2 * (1.0 / np.sqrt(1.0 + 12.0*(self.h/w)))

    def _calc_elec_length(self, w, l):
        """Compute electrical length (in degrees) for length l (m) at freq self.freq."""
        Eeff = self._calc_eff(w)
        lambda_g = 3e8 / ( self.freq * np.sqrt(Eeff) )
        theta_deg = (360.0 * l) / lambda_g
        return theta_deg

    def _Z0_expr_symbolic(self, w_sym):
        """Symbolic Z0 expression for use in synthesis."""
        Eeff_sym = ( (self.er + 1)/2 ) + ( (self.er - 1)/2 ) * (1/sp.sqrt(1 + 12*(self.h/w_sym)) )
        U_sym    = w_sym / self.h
        expr = sp.Piecewise(
            ( (60/sp.sqrt(Eeff_sym)) * sp.log( (8/U_sym) + (U_sym/4) ), U_sym <= 1 ),
            ( (120*sp.pi) / ( sp.sqrt(Eeff_sym) * ( U_sym + 1.393 + 0.667*sp.log( U_sym + 1.444 ) ) ), True )
        )
        return expr

    def _theta_expr_symbolic(self, w_sym, l_sym):
        """Symbolic expression for electrical length (degrees) in synthesis."""
        Eeff_sym = ( (self.er + 1)/2 ) + ( (self.er - 1)/2 ) * (1/sp.sqrt(1 + 12*(self.h/w_sym)) )
        lambda_g_sym = 3e8 / ( self.freq * sp.sqrt(Eeff_sym) )
        theta_sym = 360 * l_sym / lambda_g_sym
        return theta_sym


if __name__ == "__main__":
    # Example usage
    substrate = SchneiderMicrostrip(er=4.4, h=1.6e-3, freq=2.4)  # FR‑4, 2.4 GHz
    w = 3e-3  # 3 mm
    l = 30e-3 # 30 mm
    Z0, theta = substrate.analyze(w=w, l=l)
    print("Analyze:")
    print("Z0 = {:.2f} Ω".format(Z0))
    print("Electrical length = {:.2f}°".format(theta))

    # Now attempt synthesize: use the same Z0 and θ as targets
    w_calc, l_calc = substrate.synthesize(Z0_target=Z0, elec_length_deg_target=theta)
    print("\nSynthesize:")
    print("Width = {:.6f} m".format(w_calc))
    print("Length = {:.6f} m".format(l_calc))
