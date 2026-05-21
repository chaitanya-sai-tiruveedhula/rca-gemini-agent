import json
import os
import re
import google.generativeai as genai

class GeminiRCAAgent:
    def __init__(self, api_key=None, model_name="gemini-flash-latest"):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        self.model_name = model_name

    def _build_prompt(self, current_incident, similar_incidents):
        context = "\n".join([
            f"- Description: {i['description']}\n  Root cause: {i.get('root_cause', 'unknown')}\n  Resolution: {i.get('resolution', 'unknown')}"
            for i in similar_incidents
        ]) if similar_incidents else "No similar incidents found."

        return f"""
You are an IT problem management expert and RCA analyst.

Current incident:
{current_incident}

Similar incidents:
{context}

Analyze the incident and return only valid JSON with these keys:
- summary: short overview of the root cause and impact
- root_causes: array of likely root causes
- recommended_actions: array of remediation or next steps
- risk_level: one of low, medium, high, or critical
- confidence: brief confidence indicator
- analysis_text: optional expanded analysis or notes

If you cannot determine a structured answer, still return a JSON object. Do not include any markdown or code fences.
""".strip()

    def _parse_response(self, response_text):
        if not response_text:
            return {"analysis_text": "No answer returned from the LLM."}

        try:
            candidate = re.search(r"\{.*\}", response_text, re.S).group(0)
            parsed = json.loads(candidate)
            return parsed if isinstance(parsed, dict) else {"analysis_text": response_text.strip()}
        except Exception:
            return {"analysis_text": response_text.strip()}

    def analyze(self, current_incident, similar_incidents):
        prompt = self._build_prompt(current_incident, similar_incidents)
        if hasattr(genai, 'generate_text'):
            response = genai.generate_text(model=self.model_name, prompt=prompt)
        else:
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)

        text = getattr(response, "text", None) or getattr(response, "content", None) or str(response)
        result = self._parse_response(text)
        if "analysis_text" not in result:
            result["analysis_text"] = text.strip()
        return result


def analyze_with_gemini(current_incident, similar_incidents):
    agent = GeminiRCAAgent()
    return agent.analyze(current_incident, similar_incidents)
