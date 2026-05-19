import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-pro")

def analyze_with_gemini(current_incident, similar_incidents):
    context = "\n".join([
        f"Incident: {i['description']}, Cause: {i['root_cause']}, Fix: {i['resolution']}"
        for i in similar_incidents
    ])

    prompt = f"""
You are an IT Problem Management expert.

Current Incident:
{current_incident}

Similar Incidents:
{context}

Tasks:
1. Identify 3 likely root causes
2. Explain reasoning
3. Suggest resolution steps based on past incidents
4. Highlight risk level

Provide structured output.
"""

    response = model.generate_content(prompt)
    return response.text