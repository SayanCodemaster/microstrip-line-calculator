import sympy as sp

class Wheeler_1977:
    def __init__(self, er, h, freq):
        self.er = er
        self.h = h
        self.freq = freq
        self.c = 2.99792458e8 

    def Analyze(self, w, l):
        Z0 = self.__calculate_Z0(w)
        elec_length = self.__calculate_elec_length(w, l)
        return float(Z0), float(elec_length)

    def Synthesize(self, Z0_target, elec_length_target):
        w, l = sp.symbols("w l", positive=True, real=True)
        A_sym = ((14 + 8 / self.er) / 11) * (4 * self.h / w)
        Z0_expr = (42.4 / sp.sqrt(self.er + 1)) * sp.ln(
            1 + (4 * self.h / w) * (A_sym + sp.sqrt(A_sym**2 + ((sp.pi**2 / 2) * (1 + 1 / self.er))))
        )
        e_eff_sym = ((self.er + 1) / 2) + ((self.er - 1) / 2) * (1 + 12 * (self.h / w))**-0.5
        f_hz = self.freq * 1e9
        lambda_g_sym = self.c / (f_hz * sp.sqrt(e_eff_sym))
        theta_expr = (360 * l) / lambda_g_sym
        solutions = sp.nsolve(
            (Z0_expr - Z0_target, theta_expr - elec_length_target),
            (w, l),
            (self.h, 0.03),  
            dict=True
        )
        return float(solutions[0][w]), float(solutions[0][l])

    def __calculate_Z0(self, w):
        A = ((14 + 8 / self.er) / 11) * (4 * self.h / w)
        Z0 = (42.4 / sp.sqrt(self.er + 1)) * sp.log(
            1 + (4 * self.h / w) * (A + sp.sqrt(A**2 + ((sp.pi**2 / 2) * (1 + 1 / self.er))))
        )
        return Z0

    def __calculate_elec_length(self, w, l):
        e_eff = self.__calculate_eff(w)
        f_hz = self.freq * 1e9
        lambda_g = self.c / (f_hz * sp.sqrt(e_eff))
        theta_deg = (360 * l) / lambda_g
        return theta_deg

    def __calculate_eff(self, w):
        return ((self.er + 1) / 2) + ((self.er - 1) / 2) * (1 + 12 * (self.h / w))**-0.5
        
if __name__ == "__main__":
    calculator = Wheeler_1977(er=4.2, h=1.6e-3, freq=2.4)
    width_m = 3.0e-3
    length_m = 18.2e-3
    
    Z0_result, ElecLen_result = calculator.Analyze(w=width_m, l=length_m)
    print("--- Analysis (Wheeler 1977) ---")
    print(f"For a trace of {width_m*1000:.1f}mm width and {length_m*1000:.1f}mm length:")
    print(f"  - Calculated Impedance (Z₀) = {Z0_result:.2f} Ω")
    print(f"  - Electrical Length = {ElecLen_result:.2f}°")
    Z0_target = Z0_result
    ElecLen_target = ElecLen_result
    w_calc, l_calc = calculator.Synthesize(Z0_target, ElecLen_target)
    print(f"\n--- Synthesis (Wheeler 1977) ---")
    print(f"For a target of {Z0_target:.2f} Ω and {ElecLen_target:.2f}°:")
    print(f"  - Required Width = {w_calc * 1000:.3f} mm")
    print(f"  - Required Length = {l_calc * 1000:.2f} mm")