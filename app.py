from flask import Flask, render_template, request, jsonify
from formulas.wheeler_1965 import Wheeler_1965
from formulas.hammerstad_1975 import Hammerstad1975
from formulas.Wheeler_1977 import Wheeler_1977
from formulas.hammerstad import HammerstadJensen
from formulas.schneider import SchneiderMicrostrip
from formulas.IPC2141 import IPC2141Microstrip
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index2.html")

@app.route("/synthesize", methods=["POST"])
def synthesize():
    data = request.get_json()
    er = data.get("er")
    h_mm = data.get("h")           
    formula = data.get("formula")
    zo = data.get("zo")
    elecLen = data.get("elecLen")
    freq = data.get("freq")
    t_mm = data.get("t")

    h = h_mm / 1000.0  
    if t_mm is not None:
        t = t_mm / 1000.0  
    width_mm = None
    length_mm = None

    if formula == "Wheeler 1965":
        ob = Wheeler_1965(er, h, freq)
        w_m, l_m = ob.Synthesize(zo, elecLen)
        width_mm, length_mm = w_m * 1000, l_m * 1000
    elif formula == "Hammerstad and Jensen":
        ob = HammerstadJensen(er, h, freq)
        w_m, l_m = ob.synthesize(zo, elecLen)
        width_mm, length_mm = w_m * 1000, l_m * 1000
    elif formula == "Wheeler 1977":
        ob = Wheeler_1977(er, h, freq)
        w_m, l_m = ob.Synthesize(zo, elecLen)
        width_mm, length_mm = w_m * 1000, l_m * 1000
    elif formula == "Hammerstad 1975":
        ob = Hammerstad1975(er, h, freq)
        w_m, l_m = ob.synthesize(zo, elecLen)
        width_mm, length_mm = w_m * 1000, l_m * 1000
    elif formula == "Schneider":
        ob = SchneiderMicrostrip(er, h, freq)
        w_m, l_m = ob.synthesize(zo, elecLen)
        width_mm, length_mm = w_m * 1000, l_m * 1000
    elif formula == "IPC2141":
        # Check if t was provided, which IPC requires
        if t is None:
             return jsonify({"error": "IPC2141 formula requires a thickness (t)."}), 400
        print("IPC2141")
        ob = IPC2141Microstrip(er, h, t) # <<<--- 3. Now 't' is in meters
        width_mm = ob.synthesize(zo) * 1000
        
    if formula == "IPC2141":
        result = {
            "width_mm": width_mm
        }
    else:
        result = {
            "width_mm": width_mm,
            "length_mm": length_mm
        }
    return jsonify(result)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    er = data.get("er")
    h_mm = data.get("h")  # in mm from frontend
    formula = data.get("formula")
    width_mm = data.get("width_mm")
    length_mm = data.get("length_mm")
    t = None
    try:
        freq = data.get("freq")
    except:
        pass
    try:
        t_mm = data.get("t") # <<<--- 2. Get t in mm
        if t_mm is not None:
             t = t_mm / 1000.0 # <<<--- 3. Convert t from mm to METERS
    except:
        pass

    h = h_mm / 1000.0  # convert mm to meters

    # Convert width and length from mm to meters
    w = float(width_mm) / 1000.0
    if(formula != "IPC2141"):
        
        l = float(length_mm) / 1000.0

    if formula == "Wheeler 1965":
        ob = Wheeler_1965(er, h, freq)
        zo, elecLen = ob.Analyze(w, l)
    elif formula == "Wheeler 1977":
        ob = Wheeler_1977(er, h, freq)
        zo, elecLen = ob.Analyze(w, l)
    elif formula == "Hammerstad 1975":
        ob = Hammerstad1975(er, h, freq)
        zo, elecLen = ob.analyze(w, l)
    elif formula == "Hammerstad and Jensen":
        ob = HammerstadJensen(er, h, freq)
        zo, elecLen = ob.analyze(w, l)
    elif formula == "Schneider":
        ob = SchneiderMicrostrip(er, h, freq)
        zo, elecLen = ob.analyze(w, l)
    elif formula == "IPC2141":
        # Check if t was provided
        if t is None:
            return jsonify({"error": "IPC2141 formula requires a thickness (t)."}), 400
        ob = IPC2141Microstrip(er, h, t) # <<<--- 4. Now 't' is in meters
        zo = ob.analyze(w)

    
    if formula == "IPC2141":
        return jsonify({"zo": zo}) # <<<--- This was correct
        
    result = {
        "zo": zo,
        "elecLen": elecLen
    }
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
