import time
from flask import Flask, request, jsonify
from similarity import find_similar
from gemini_rca import analyze_with_gemini

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "rca-gemini-agent"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    incident = (data.get("description") or "").strip()

    if not incident:
        return jsonify({"error": "Missing incident description."}), 400

    similar_incidents = find_similar(incident)
    incident_number = f"INC-{int(time.time())}"
    rca_analysis = analyze_with_gemini(incident, similar_incidents)
    if isinstance(rca_analysis, dict):
        rca_analysis["incident_number"] = incident_number

    return jsonify({
        "incident_number": incident_number,
        "similar_incidents": similar_incidents,
        "rca_analysis": rca_analysis,
        "rca": rca_analysis
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
