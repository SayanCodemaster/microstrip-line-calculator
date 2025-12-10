# ===============================
# Microstrip Test Runner (Fixed)
# ===============================

from formulas.wheeler_1965 import Wheeler_1965
from formulas.hammerstad_1975 import Hammerstad1975
from formulas.Wheeler_1977 import Wheeler_1977
from formulas.hammerstad import HammerstadJensen
from formulas.schneider import SchneiderMicrostrip
from formulas.IPC2141 import IPC2141Microstrip


def synthesize_test(er, h, freq, z0, elec_len, t):
    h = h / 1000.0
    t = t / 1000.0

    Wheeler_1965_ob = Wheeler_1965(er=er, h=h, freq=freq)
    Hammerstad1975_ob = Hammerstad1975(er=er, h=h, freq=freq)
    Wheeler_1977_ob = Wheeler_1977(er=er, h=h, freq=freq)
    HammerstadJensen_ob = HammerstadJensen(er=er, h=h, freq=freq)
    SchneiderMicrostrip_ob = SchneiderMicrostrip(er=er, h=h, freq=freq)
    IPC2141Microstrip_ob = IPC2141Microstrip(er=er, h=h, t=t)

    def print_result(name, result):
        """Helper to print result uniformly"""
        if isinstance(result, tuple):
            try:
                w, l = result
                print(f"{name:20s} -> W = {w*1000:.4f} mm, L = {l*1000:.4f} mm")
            except Exception:
                print(f"{name:20s} -> Invalid result format: {result}")
        else:
            try:
                w = float(result)
                print(f"{name:20s} -> W = {w*1000:.4f} mm")
            except Exception:
                print(f"{name:20s} -> Error: {result}")

    print(f"\n===== Synthesize Test | Z0={z0} Ω | θ={elec_len}° =====")

    # Each formula safely wrapped
    try:
        print_result("Wheeler 1965", Wheeler_1965_ob.Synthesize(z0, elec_len))
    except Exception as e:
        print(f"Wheeler 1965 ERROR: {e}")

    try:
        print_result("Hammerstad 1975", Hammerstad1975_ob.synthesize(z0, elec_len))
    except Exception as e:
        print(f"Hammerstad 1975 ERROR: {e}")

    try:
        print_result("Wheeler 1977", Wheeler_1977_ob.Synthesize(z0, elec_len))
    except Exception as e:
        print(f"Wheeler 1977 ERROR: {e}")

    try:
        print_result("Hammerstad Jensen", HammerstadJensen_ob.synthesize(z0, elec_len))
    except Exception as e:
        print(f"Hammerstad Jensen ERROR: {e}")

    try:
        print_result("Schneider Microstrip", SchneiderMicrostrip_ob.synthesize(z0, elec_len))
    except Exception as e:
        print(f"Schneider Microstrip ERROR: {e}")

    # IPC2141 special handling (it only returns width)
    try:
        w_val = IPC2141Microstrip_ob.synthesize(z0)
        print_result("IPC2141 Microstrip", w_val)
    except Exception as e:
        print(f"IPC2141 Microstrip ERROR: {e}")


def analyze_test(er, h, freq, w, l, t):
    h = h / 1000.0
    t = t / 1000.0
    w = float(w) / 1000.0
    l = float(l) / 1000.0

    Wheeler_1965_ob = Wheeler_1965(er=er, h=h, freq=freq)
    Hammerstad1975_ob = Hammerstad1975(er=er, h=h, freq=freq)
    Wheeler_1977_ob = Wheeler_1977(er=er, h=h, freq=freq)
    HammerstadJensen_ob = HammerstadJensen(er=er, h=h, freq=freq)
    SchneiderMicrostrip_ob = SchneiderMicrostrip(er=er, h=h, freq=freq)
    IPC2141Microstrip_ob = IPC2141Microstrip(er=er, h=h, t=t)

    print(f"\n===== Analyze Test | W={w*1000:.3f} mm | L={l*1000:.3f} mm =====")

    def safe_analyze(name, func):
        try:
            result = func()
            print(f"{name:20s}: {result}")
        except Exception as e:
            print(f"{name:20s} ERROR: {e}")

    safe_analyze("Wheeler 1965", lambda: Wheeler_1965_ob.Analyze(w, l))
    safe_analyze("Hammerstad 1975", lambda: Hammerstad1975_ob.analyze(w, l))
    safe_analyze("Wheeler 1977", lambda: Wheeler_1977_ob.Analyze(w, l))
    safe_analyze("Hammerstad Jensen", lambda: HammerstadJensen_ob.analyze(w, l))
    safe_analyze("Schneider Microstrip", lambda: SchneiderMicrostrip_ob.analyze(w, l))
    safe_analyze("IPC2141 Microstrip", lambda: IPC2141Microstrip_ob.analyze(w))


def main():
    # =========================
    # Common Parameters
    # =========================
    Er = 4.4
    Tand = 0.007
    h = 1.58  # mm
    t = 0.05  # mm
    fo = 2.4  # GHz (keep in GHz for consistency with class inputs)
    cond = 5.2e7

    # -------------------------
    # Synthesize Test Data
    # -------------------------
    synth_data = [
        (20, 90),
        (30, 90),
        (40, 90),
        (50, 90),
        (60, 90),
        (70, 90),
        (80, 90),
        (90, 90),
        (100, 90),
        (110, 90),
    ]

    print("\n==============================")
    print("   SYNTHESIZE TESTS START")
    print("==============================")

    for z0, theta in synth_data:
        synthesize_test(Er, h, fo, z0, theta, t)

    # -------------------------
    # Analyze Test Data
    # -------------------------
    analyze_data = [
        (0.4, 17),
        (0.8, 17),
        (1.2, 17),
        (1.6, 17),
        (2.0, 17),
        (2.4, 17),
        (2.8, 17),
        (3.2, 17),
        (3.6, 17),
        (4.0, 17),
    ]

    print("\n==============================")
    print("   ANALYZE TESTS START")
    print("==============================")

    for w, l in analyze_data:
        analyze_test(Er, h, fo, w, l, t)


if __name__ == "__main__":
    main()
