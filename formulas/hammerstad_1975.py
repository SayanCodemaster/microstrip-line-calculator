import sympy as sp

class Hammerstad1975:
    def __init__(self, er, h, freq):
        self.er = er               # Relative permittivity
        self.h = h                 # Substrate height (meters)
        self.freq = freq           # Frequency (GHz)

    def analyze(self, w, l):
        Z0 = self.calculate_Z0(w)
        L = self.calculate_electrical_length(w, l)
        return Z0,L

    def synthesize(self, Z0_target, elec_length_target):
        w, l = sp.symbols('w l', positive=True, real=True)
        Z0_expr = self.characteristic_impedance_expr(w)
        theta_expr = self.electrical_length_expr(w, l)
        # Initial guesses: width same as height, length 3cm
        solutions = sp.nsolve(
            [Z0_expr - Z0_target, theta_expr - elec_length_target],
            [w, l],
            [self.h, 0.03]
        )
        
        return float(solutions[0]),float(solutions[1])

    def effective_eps(self, w):
        return (self.er + 1) / 2 + (self.er - 1) / 2 * 1 / sp.sqrt(1 + 12 * self.h / w)

    def characteristic_impedance_expr(self, w):
        U = w / self.h
        eps_eff = self.effective_eps(w)
        Z0 = sp.Piecewise(
            (60 / sp.sqrt(eps_eff) * sp.log(8 / U + 0.25 * U), U <= 1),
            (120 * sp.pi / (sp.sqrt(eps_eff) * (U + 1.393 + 0.667 * sp.log(U + 1.444))), True)
        )
        return Z0

    def calculate_Z0(self, w):
        U = w / self.h
        eps_eff = float(self.effective_eps(w))
        if U <= 1:
            return float(60 / eps_eff ** 0.5 * sp.log(8 / U + 0.25 * U))
        else:
            return float(120 * sp.pi / (eps_eff ** 0.5 * (U + 1.393 + 0.667 * sp.log(U + 1.444))))

    def electrical_length_expr(self, w, l):
        c = 2.99792458e8      # m/s
        freq_hz = self.freq * 1e9
        eps_eff = self.effective_eps(w)
        lambdag = c / (freq_hz * sp.sqrt(eps_eff))
        theta = 360 * l / lambdag
        return theta

    def calculate_electrical_length(self, w, l):
        c = 2.99792458e8      # m/s
        freq_hz = self.freq * 1e9
        eps_eff = float(self.effective_eps(w))
        lambdag = c / (freq_hz * eps_eff ** 0.5)
        return float(360 * l / lambdag)

if __name__ == '__main__':
    # Example parameters for demonstration
    er = 4.4          # Relative permittivity
    h = 1.6e-3        # Height (meters)
    freq = 2.4        # GHz
    w = 3.0e-3        # Width (meters)
    l = 30.0e-3       # Length (meters)
    
    model = Hammerstad1975(er, h, freq)
    print(model.analyze(w, l))
    model.synthesize(51.17, 157.65)
