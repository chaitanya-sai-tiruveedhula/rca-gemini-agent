import time
from flask import Flask, request, jsonify
from similarity import find_similar, get_incident_by_id
from gemini_rca import analyze_with_gemini

app = Flask(__name__)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "service": "rca-gemini-agent"})

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json or {}
    incident_id = (data.get("incident_id") or "").strip()
    description = (data.get("description") or "").strip()

    # If incident_id is provided, look it up in the database
    if incident_id:
        incident_record = get_incident_by_id(incident_id)
        if incident_record:
            description = incident_record.get("description", "")
            incident_number = str(incident_record.get("incident_id", incident_id))
        else:
            return jsonify({"error": f"Incident with ID {incident_id} not found in database."}), 404
    elif not description:
        return jsonify({"error": "Missing incident description or incident ID."}), 400
    else:
        incident_number = f"INC-{int(time.time())}"

    similar_incidents = find_similar(description)
    rca_analysis = analyze_with_gemini(description, similar_incidents, incident_number)
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
