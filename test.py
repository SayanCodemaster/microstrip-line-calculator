from wheeler_1965 import Wheeler_1965
from hammerstad_1975 import Hammerstad1975
from Wheeler_1977 import Wheeler_1977
from hammerstad import HammerstadJensen
from schneider import SchneiderMicrostrip
from IPC2141 import IPC2141Microstrip
from prettytable import PrettyTable

def test_all_formulas(er, h_mm, zo, elecLen, freq):
    h = h_mm / 1000.0  # convert mm → m

    formulas = {
        "Wheeler 1965": Wheeler_1965,
        "Wheeler 1977": Wheeler_1977,
        "Hammerstad 1975": Hammerstad1975,
        "Hammerstad and Jensen": HammerstadJensen,
        "Schneider": SchneiderMicrostrip,
        "IPC2141": IPC2141Microstrip
    }

    table = PrettyTable()
    table.field_names = ["Formula", "Width (mm)", "Length (mm)", "Z0 (Analyzed)", "Elec. Len (Analyzed)", "Error"]

    for name, cls in formulas.items():
        try:
            ob = cls(er, h, freq)
            # Use whichever method exists
            if hasattr(ob, "Synthesize"):
                w_m, l_m = ob.Synthesize(zo, elecLen)
            else:
                w_m, l_m = ob.synthesize(zo, elecLen)

            width_mm = w_m * 1000
            length_mm = l_m * 1000

            if hasattr(ob, "Analyze"):
                zo_calc, elec_calc = ob.Analyze(w_m, l_m)
            else:
                zo_calc, elec_calc = ob.analyze(w_m, l_m)

            table.add_row([
                name,
                round(width_mm, 4),
                round(length_mm, 4),
                round(zo_calc, 4),
                round(elec_calc, 4),
                "-"
            ])

        except Exception as e:
            table.add_row([name, "-", "-", "-", "-", str(e)])

    print(table)


if __name__ == "__main__":
    # Example input values
    er = 4.5        # dielectric constant
    h_mm = 1.6      # substrate height in mm
    zo = 50         # target impedance
    elecLen = 90    # electrical length in degrees
    freq = 1e9      # frequency in Hz

    test_all_formulas(er, h_mm, zo, elecLen, freq)
