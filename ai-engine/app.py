import time
import json
import logging
from flask import Flask, request, jsonify
from similarity import find_similar, get_incident_by_id
from gemini_rca import analyze_with_gemini
import google.generativeai as genai
import os
from config import DATA_SOURCES, CACHE_TTL
from functools import lru_cache
import hashlib

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configure Gemini for conversational responses
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

@app.route("/", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "rca-gemini-agent",
        "features": ["local_analysis", "internet_sources", "chatbot"],
        "data_sources": list(DATA_SOURCES.keys())
    })

@app.route("/data-sources", methods=["GET"])
def get_data_sources():
    """Return information about available data sources"""
    sources_info = {}
    for source_name, config in DATA_SOURCES.items():
        sources_info[source_name] = {
            "enabled": config.get("enabled", False),
            "description": config.get("description", ""),
            "max_results": config.get("max_results", 0)
        }
    
    return jsonify({
        "sources": sources_info,
        "note": "Combine local CSV with internet sources (GitHub, Stack Overflow, CISA, Status Pages)"
    })

@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Analyze incident with RCA using both local and internet sources.
    """
    data = request.json or {}
    incident_id = (data.get("incident_id") or "").strip()
    description = (data.get("description") or "").strip()
    use_internet = data.get("use_internet_sources", True)

    # If incident_id is provided, look it up in the database (local only)
    if incident_id:
        incident_record = get_incident_by_id(incident_id)
        if incident_record:
            description = incident_record.get("description", "")
            incident_number = str(incident_record.get("incident_id", incident_id))
        else:
            logger.warning(f"Incident {incident_id} not found in local database")
            return jsonify({"error": f"Incident with ID {incident_id} not found in database."}), 404
    elif not description:
        return jsonify({"error": "Missing incident description or incident ID."}), 400
    else:
        incident_number = f"INC-{int(time.time())}"

    try:
        # Find similar incidents from local + internet sources
        logger.info(f"Finding similar incidents for: {description[:50]}...")
        similar_incidents = find_similar(description, use_internet_sources=use_internet)
        
        logger.info(f"Found {len(similar_incidents)} similar incidents")
        
        # Perform RCA analysis
        rca_analysis = analyze_with_gemini(description, similar_incidents, incident_number)
        if isinstance(rca_analysis, dict):
            rca_analysis["incident_number"] = incident_number

        # Add source information
        sources_used = set()
        for incident in similar_incidents:
            if "source" in incident:
                sources_used.add(incident["source"])
            else:
                sources_used.add("Local Database")

        return jsonify({
            "incident_number": incident_number,
            "similar_incidents": similar_incidents,
            "rca_analysis": rca_analysis,
            "rca": rca_analysis,
            "data_sources_used": list(sources_used),
            "internet_sources_enabled": use_internet
        })
    
    except Exception as e:
        logger.error(f"Error in analysis: {str(e)}", exc_info=True)
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@app.route("/chat", methods=["POST"])
def chat():
    """Conversational endpoint for chatbot with internet source integration"""
    data = request.json or {}
    message = (data.get("message") or "").strip()
    history = data.get("history", [])
    use_internet = data.get("use_internet_sources", True)
    
    if not message:
        return jsonify({"error": "Missing message"}), 400
    
    try:
        # Check if this message contains incident information
        full_context = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in history[-4:] + [{"role": "user", "content": message}]])
        
        # Use Gemini to generate conversational response
        model = genai.GenerativeModel("gemini-flash-latest")
        
        system_prompt = """You are a helpful RCA (Root Cause Analysis) Assistant. Your job is to:
1. Help users describe their incidents in a friendly, conversational way
2. Ask clarifying questions if needed
3. Extract relevant information about incidents
4. Provide empathetic and actionable responses

When a user describes an incident, acknowledge it and ask for any missing details like:
- What systems are affected
- When did it start
- How many users are impacted
- What error messages they see

Keep responses concise and friendly. Use emojis occasionally to be approachable."""

        response = model.generate_content(f"{system_prompt}\n\nUser: {message}\n\nAssistant:", stream=False)
        reply = response.text.strip()
        
        # Check if the message contains sufficient incident details
        incident_keywords = ["down", "broken", "error", "issue", "problem", "crash", "fail", "not working", "slow", "timeout", "service", "system", "bug", "exception", "alert"]
        has_incident_info = any(keyword in message.lower() for keyword in incident_keywords)
        
        analysis_data = None
        similar_incidents = []
        
        # If message has incident info, perform RCA analysis
        if has_incident_info and len(message) > 30:
            try:
                logger.info(f"Incident detected in chat: {message[:50]}...")
                similar_incidents = find_similar(message, use_internet_sources=use_internet)
                rca_analysis = analyze_with_gemini(message, similar_incidents, f"INC-{int(time.time())}")
                analysis_data = rca_analysis
            except Exception as e:
                logger.warning(f"RCA analysis error in chat: {e}")
                pass
        
        return jsonify({
            "reply": reply,
            "analysis": analysis_data,
            "similar_incidents": similar_incidents,
            "internet_sources_used": use_internet
        })
        
    except Exception as err:
        logger.error(f"Chat error: {str(err)}", exc_info=True)
        error_msg = str(err) if str(err) else "Error processing chat request"
        return jsonify({"error": error_msg}), 500

@app.route("/config", methods=["GET"])
def get_config():
    """Return system configuration"""
    return jsonify({
        "data_sources": DATA_SOURCES,
        "features": {
            "local_analysis": True,
            "internet_sources": True,
            "chatbot": True,
            "similar_incident_matching": True,
            "rca_analysis": True
        }
    })

if __name__ == "__main__":
    logger.info("Starting RCA Gemini Agent with Internet Sources")
    logger.info(f"Enabled data sources: {', '.join([k for k, v in DATA_SOURCES.items() if v.get('enabled')])}")
    app.run(host="0.0.0.0", port=5000)
