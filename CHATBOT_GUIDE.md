# RCA Chatbot Feature Guide

## 🎯 Overview

The chatbot feature transforms the RCA Gemini Agent into a user-friendly tool accessible to non-technical stakeholders. Instead of form-based input, users can now describe incidents naturally in a conversational interface.

## 🚀 Quick Start

### Access the Chatbot
1. Start the application (Python backend and Node.js server)
2. Open `http://localhost:3000` in your browser
3. Click the **"💬 Try Chatbot"** button in the top navigation
4. Or directly visit `http://localhost:3000/chatbot.html`

### Example Interaction

```
User: "The payment service crashed 15 minutes ago and customers can't checkout"

Bot: "That's urgent! 🚨 Payment service outages directly impact revenue. Let me gather more details.

Quick questions:
- How many customers are affected?
- Are there any error messages you're seeing?
- Did anything change recently (deployment, configuration update, etc.)?

[Analysis Results Appear]
Root Causes:
- Database connection timeout due to spike in traffic
- Insufficient connection pool size

Recommended Actions:
1. Immediately increase database connection pool size
2. Implement query caching for frequently accessed data
3. Check for traffic anomalies or DDoS

Risk Level: 🔴 CRITICAL
Similar Incident: INC-2024-001234 - Payment service timeout (resolved in 45 minutes)
```

## 📱 Features

### For End Users
- **Plain Language Input** - No technical jargon required
- **Conversational Responses** - Friendly, empathetic AI responses
- **Instant Analysis** - Automatic RCA when enough details provided
- **Helpful Suggestions** - Guidance on what information is most useful
- **Visual Results** - Clear display of root causes and actions
- **History Matching** - Learn from similar past incidents

### For IT Teams
- **Faster Incident Triage** - Non-technical users can self-serve initial analysis
- **Reduced Onboarding** - No training needed on structured forms
- **Better Data Capture** - Conversational flow naturally extracts needed info
- **Quality Consistency** - AI ensures comprehensive incident information

## 🏗️ Architecture

### Frontend Components

**chatbot.html**
- Two-column layout with chat on left, results on right
- Message display area with auto-scrolling
- Input textarea with send button
- Real-time loading indicators
- Responsive design (mobile to desktop)

**chatbot.js**
- Message rendering and auto-scroll
- Conversation history management
- API communication with `/chat` endpoint
- Result formatting and display
- Error handling and user feedback

**chatbot-style.css**
- Chat bubble styling (user vs. bot)
- Animation effects (slide-in, pulse)
- Responsive grid layout
- Risk level color coding
- Custom scrollbar styling

### Backend Endpoints

**POST /chat** (Node.js proxy)
```json
Request: {
  "message": "The database is responding slowly",
  "history": [
    {"role": "user", "content": "Our API is down"},
    {"role": "assistant", "content": "..."}
  ]
}

Response: {
  "reply": "I see the API is down...",
  "analysis": {
    "summary": "Database performance degradation",
    "root_causes": [...],
    "recommended_actions": [...],
    "risk_level": "high",
    "confidence": "high"
  },
  "similar_incidents": [...]
}
```

**Python /chat** (Flask backend)
- Generates conversational response using Gemini
- Detects incident information using keyword analysis
- Triggers RCA analysis if sufficient incident details found
- Returns structured JSON response

## 🧠 AI Logic

### Conversation Generation
- Uses Gemini Flash model for fast, natural responses
- System prompt guides AI to be helpful, empathetic, professional
- Asks clarifying questions when information is incomplete

### Incident Detection
- Monitors conversation for incident keywords:
  - Service terms: "down", "crashed", "broken", "slow", "timeout"
  - Issue types: "error", "bug", "exception", "alert", "failure"
- Minimum length check (>30 chars) ensures sufficient detail
- When detected, automatically performs RCA analysis

### Risk Assessment
The system evaluates and displays risk levels:
- **🟢 Low** - Minor impact, limited scope
- **🟡 Medium** - Moderate business impact
- **🟠 High** - Significant impact to users/services
- **🔴 Critical** - Revenue-blocking or widespread outage

## 💡 Usage Tips

### For Best Results, Include:
1. **Service/System Name** - "payment service", "API gateway", "database"
2. **Symptoms** - "slow response", "returns 500 errors", "connections refused"
3. **Timeline** - "started 30 minutes ago", "happening since deployment"
4. **Scope** - "all users affected", "50% of requests failing", "one region only"
5. **Recent Changes** - "deployed new version", "scaled infrastructure", "updated config"

### Example Good Incident Descriptions
- ✅ "The authentication service started returning 401 errors 20 minutes ago. All login attempts fail. This happened right after we deployed version 2.1."
- ✅ "Database connection timeout errors in production. High CPU usage on DB server. Started 1 hour ago during load test."
- ✅ "Payment processing is 50% slower than normal. Takes 30 seconds instead of 2 seconds. Traffic looks normal."

### Example Needs Improvement
- ❌ "System is broken" (too vague)
- ❌ "Something went wrong" (no specific service)
- ❌ "It's slow" (no baseline or scope)

## 🔄 Switching Between Modes

### Analyzer vs. Chatbot

| Feature | Analyzer | Chatbot |
|---------|----------|---------|
| Input Style | Structured form | Free text |
| Audience | Technical teams | Anyone |
| Analysis Trigger | Manual click | Automatic |
| Learning Curve | Moderate | None |
| Speed | Fast | Interactive |
| Guidance | Minimal | Extensive |

Use **Analyzer** when:
- You have structured incident data
- You're an experienced incident responder
- You want quick, direct results

Use **Chatbot** when:
- You need to explain an issue naturally
- You're new to incident management
- You want AI guidance through the process

## 🛠️ Customization

### Modify Chatbot Personality
Edit the system prompt in `ai-engine/app.py`:
```python
system_prompt = """You are a helpful RCA (Root Cause Analysis) Assistant..."""
```

### Adjust Incident Detection Keywords
Edit keyword list in `ai-engine/app.py`:
```python
incident_keywords = ["down", "broken", "error", "issue", ...]
```

### Change Risk Level Colors
Edit risk badge styles in `chatbot-style.css`:
```css
.risk-critical { background: #fee2e2; color: #991b1b; }
```

## 📊 Monitoring & Analytics

To track chatbot usage, add logging to:
1. `chatbot.js` - Log user messages and interactions
2. `backend-node/server.js` - Log API calls and response times
3. `ai-engine/app.py` - Log RCA analysis triggers and results

Example logging addition in app.py:
```python
import logging
logging.info(f"Chat request: {message[:50]}...")
logging.info(f"RCA triggered: {has_incident_info}")
```

## 🐛 Troubleshooting

### Chatbot Not Responding
- Check Python backend is running: `http://localhost:5000/`
- Check Node.js proxy: `http://localhost:3000/`
- Check browser console for JavaScript errors (F12)
- Verify GEMINI_API_KEY is set

### Analysis Not Triggering
- Use more incident-specific language
- Ensure message is >30 characters
- Include service names and error types
- Check Python logs for analysis errors

### Slow Response Times
- May indicate Gemini API latency
- Check internet connection
- Reduce conversation history length if very long

## 📚 Related Files

**Modified:**
- `backend-node/server.js` - Added `/chat` endpoint
- `ai-engine/app.py` - Added `/chat` endpoint  
- `frontend/index.html` - Added chatbot navigation link
- `frontend/style.css` - Added nav-link styling
- `README.md` - Added chatbot documentation

**Created:**
- `frontend/chatbot.html` - Chatbot interface
- `frontend/chatbot.js` - Chatbot logic
- `frontend/chatbot-style.css` - Chatbot styling

---

**Version:** 1.0  
**Last Updated:** June 14, 2026  
**Status:** Production Ready
