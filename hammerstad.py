import math

class HammerstadJensen:
    def __init__(self, er: float, h: float, freq: float):
        self.er = float(er)
        self.h = float(h)
        self.freq = float(freq)  # GHz

    def _num_er_eff(self, w: float) -> float:
        U = w / self.h
        # Hammerstad/Jensen effective permittivity
        return (self.er + 1) / 2 + (self.er - 1) / 2 * (1 / math.sqrt(1 + 12 * self.h / w))
    def _num_Z0(self, w: float) -> float:
        er_eff = self._num_er_eff(w)
        U = w / self.h
        if U <= 1:
            return 60 / math.sqrt(er_eff) * math.log(8 * self.h / w + 0.25 * U)
        else:
            return 120 * math.pi / (math.sqrt(er_eff) * (U + 1.393 + 0.667 * math.log(U + 1.444)))


    def _num_theta(self, w: float, l: float) -> float:
        """Numeric electrical length (degrees)."""
        er_eff = self._num_er_eff(w)
        c = 2.99792458e8
        freq_hz = self.freq * 1e9
        lambda_g = c / (freq_hz * math.sqrt(er_eff))
        theta = 360 * l / lambda_g
        return float(theta)

    def analyze(self, w: float, l: float):
        """
        Given physical width w (m) and length l (m), return:
          (Z0 (ohm), electrical_length (degrees))
        """
        if w <= 0 or l < 0:
            raise ValueError("w must be > 0, l must be >= 0 (meters).")

        Z0 = self._num_Z0(w)
        theta = self._num_theta(w, l)
        return float(Z0), float(theta)
    
    # FIX: Removed the duplicate definition line for 'synthesize' that was here.
    def synthesize(self, Z0_target: float, elec_length_target: float):
        """
        Returns width (m), length (m) that match given Z0 and electrical length (deg)
        using an approximate analytical approach.
        """
        # Rough inversion using trial method
        w = self.h  # initial guess
        for _ in range(100):
            Z0 = self._num_Z0(w)
            if abs(Z0 - Z0_target) < 1e-3:
                break
            # adjust width slightly based on difference
            if Z0 > Z0_target:
                w *= 1.01
            else:
                w *= 0.99

        # compute electrical length to get physical length
        er_eff = self._num_er_eff(w)
        c = 2.99792458e8
        freq_hz = self.freq * 1e9
        lambda_g = c / (freq_hz * math.sqrt(er_eff))
        l = lambda_g * (elec_length_target / 360.0)
        return float(w), float(l)

# Example run (optional)
if __name__ == "__main__":
    model = HammerstadJensen(er=4.4, h=1.6e-3, freq=2.4)
    w, l = 3.0e-3, 30.0e-3
    Z0, theta = model.analyze(w, l)
    w_syn, l_syn = model.synthesize(Z0, theta)
    Z0_syn, theta_syn = model.analyze(w_syn, l_syn)
    print(f"Synthesized w = {w_syn:.6f} m, l = {l_syn:.6f} m")
    print(f"Verified Z0 = {Z0_syn:.3f} Ω, θ = {theta_syn:.3f}°")
    print(f"Z0 = {Z0:.3f} Ω, θ = {theta:.3f}°")
# FIX: Removed the non-Python comment '// fix' from the end of the file.