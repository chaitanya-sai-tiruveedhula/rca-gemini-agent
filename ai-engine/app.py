from flask import Flask, request, jsonify
from similarity import find_similar
from gemini_rca import analyze_with_gemini

app = Flask(__name__)

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    incident = data["description"]

    similar_incidents = find_similar(incident)
    rca_analysis = analyze_with_gemini(incident, similar_incidents)

    return jsonify({
        "similar_incidents": similar_incidents,
        "rca": rca_analysis
    })

if __name__ == "__main__":
    app.run(port=5000)