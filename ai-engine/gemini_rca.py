import google.generativeai as genai
import os

class GeminiRCAAgent:
    def __init__(self, api_key=None, model_name="gemini-flash-latest"):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    def analyze(self, current_incident, similar_incidents):
        context = "\n".join([
            f"Incident: {i['description']}, Cause: {i['root_cause']}, Fix: {i['resolution']}"
            for i in similar_incidents
        ]) if similar_incidents else "No similar incidents found."

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

        response = self.model.generate_content(prompt)
        return getattr(response, "text", str(response))


def analyze_with_gemini(current_incident, similar_incidents):
    agent = GeminiRCAAgent()
    return agent.analyze(current_incident, similar_incidents)