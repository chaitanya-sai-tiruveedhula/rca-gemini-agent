# RCA Gemini Agent

A powerful agent pipeline for root cause analysis using Gemini and incident similarity matching from both local and internet sources.

**Features**: Conversational chatbot for non-technical users 💬 + Internet-powered incident analysis 🌐

## Setup

1. Install Python dependencies:

```bash
pip install -r requirements.txt
```

2. Install Node dependencies:

```bash
cd backend-node
npm install
```

3. Set your Gemini API key:

```bash
setx GEMINI_API_KEY "your_api_key"
```

4. (Optional) Set GitHub token for higher API rate limits:

```bash
setx GITHUB_TOKEN "your_github_token"
```

5. (Optional) Override the Python API URL:

```bash
setx PYTHON_SERVICE_URL "http://127.0.0.1:5000"
```

## Run

1. Start the Python API:

```bash
python ai-engine/app.py
```

2. Start the Node server:

```bash
cd backend-node
npm start
```

3. Open `http://localhost:3000` in your browser.

## How it works

- Frontend calls the Node proxy at `http://localhost:3000/analyze` or `/chat`
- Node forwards requests to the Python Flask service at `http://127.0.0.1:5000/analyze` or `/chat`
- Python combines:
  - Local incident database (incidents.csv)
  - Internet sources (GitHub, Stack Overflow, CISA, Status Pages)
  - Gemini AI for analysis and conversation
- Results include source attribution and similarity scoring

## Features

### 📊 Technical Analyzer (index.html)
- Structured form-based incident input
- Detailed RCA analysis with root causes and recommended actions
- Historical incident matching with source attribution
- **🌐 Internet-powered similarity matching**:
  - GitHub issues and discussions
  - Stack Overflow solutions
  - Security advisories from CISA
  - Public status page incidents
  - Combined with local CSV database
- Risk level assessment (Low/Medium/High/Critical)
- Confidence scoring
- Toggle to enable/disable internet sources per analysis

### 💬 Conversational Chatbot (chatbot.html)
A user-friendly chatbot interface designed for non-technical users:
- **Natural Language Input**: Describe incidents in plain English
- **Guided Conversation**: AI asks clarifying questions
- **Real-time Analysis**: Automatically triggers RCA with internet sources
- **Friendly Interface**: Clean chat with emojis and helpful tips
- **Smart Response Generation**: Combines conversational AI with RCA analysis
- **Similar Incident Matching**: Shows patterns from GitHub, Stack Overflow, and local history
- **Easy Navigation**: Switch between modes instantly

### How to Use the Analyzer with Internet Sources

1. Go to `http://localhost:3000`
2. Check "🌐 Use Internet Sources" (enabled by default)
3. Describe your incident with details
4. Results show data sources (GitHub, Stack Overflow, Local DB, etc.)
5. Click links to view original sources

### How to Use the Chatbot

1. Click "💬 Try Chatbot" or go to `http://localhost:3000/chatbot.html`
2. Describe your incident naturally
3. Chatbot asks clarifying questions
4. RCA analysis appears automatically
5. Similar incidents shown with sources

### Example Analysis with Internet Sources

**Input**: "Database connection timeout errors, started after upgrade to MySQL 8.0"

**Data Sources**: GitHub 🐙, Stack Overflow 📚, Local Database 💾

**Results**:
- **GitHub Match**: MySQL 8.0 connection pool issues (80% similarity)
- **Stack Overflow**: Performance degradation recommendations
- **Local Match**: Similar incident 3 months ago with resolution
- **Root Causes**: Connection pool exhaustion, thread limit exceeded
- **Actions**: Adjust max_connections, implement connection pooling
- **Risk**: Medium | **Confidence**: High

## 🌐 Internet Sources

The system can fetch incident data from:

| Source | Type | Data | Icon |
|--------|------|------|------|
| **GitHub** | Issues/Discussions | Public repository problems | 🐙 |
| **Stack Overflow** | Q&A | Community solutions | 📚 |
| **CISA/NVD** | Security | CVE advisories | 🔒 |
| **Status Pages** | Incidents | Service outages | 📊 |
| **Local CSV** | History | Your incident database | 💾 |

**All sources are optional and can be disabled** in `ai-engine/config.py`

See [INTERNET_SOURCES_GUIDE.md](INTERNET_SOURCES_GUIDE.md) for detailed configuration and best practices.

## Architecture

```
Frontend (HTML/CSS/JS)
├── index.html (Technical Analyzer)
├── chatbot.html (Conversational Interface)
├── app.js (Analyzer with internet toggle)
├── chatbot.js (Chatbot with internet sources)
├── style.css (Base styles)
└── chatbot-style.css (Chatbot styles)

Node.js Server (Express)
├── /analyze (RCA with sources)
├── /chat (Conversational with sources)
└── /data-sources (Available sources info)

Python Backend (Flask)
├── /analyze (Local + Internet analysis)
├── /chat (Conversational + internet analysis)
├── /data-sources (Source configuration)
├── similarity.py (Matching + internet fetch)
├── open_source_data.py (Internet fetching)
├── config.py (Source configuration)
├── gemini_rca.py (Gemini analysis)
└── incidents.csv (Local database)
```

## API Endpoints

### Get Available Data Sources
```
GET /data-sources

Response:
{
  "sources": {
    "github": {"enabled": true, "description": "..."},
    "stackoverflow": {"enabled": true, "description": "..."},
    ...
  }
}
```

### Analyze Incident
```
POST /analyze

Request:
{
  "description": "Database timeout",
  "use_internet_sources": true,
  "incident_id": "INC-123" (optional)
}

Response:
{
  "similar_incidents": [...],
  "rca_analysis": {...},
  "data_sources_used": ["GitHub", "Stack Overflow", "Local Database"]
}
```

### Conversational Chat
```
POST /chat

Request:
{
  "message": "The API is slow",
  "history": [{...}],
  "use_internet_sources": true
}

Response:
{
  "reply": "...",
  "analysis": {...},
  "similar_incidents": [...],
  "internet_sources_used": true
}
```

### System Configuration
```
GET /config

Returns all data source settings and feature availability
```

## Configuration

### Enable/Disable Internet Sources

Edit `ai-engine/config.py`:

```python
DATA_SOURCES = {
    "github": {"enabled": True, "max_results": 3},
    "stackoverflow": {"enabled": True, "max_results": 3},
    "cisa": {"enabled": True, "max_results": 2},
    "status_pages": {"enabled": True, "max_results": 2},
    "local_csv": {"enabled": True, "max_results": 5}
}
```

### Per-Request Control

Users can toggle internet sources in the UI for each analysis:
- **Enabled by default** for comprehensive analysis
- **Disable** if speed is critical (local-only mode)
- Shows which sources were used in results

## 📚 Documentation

- [CHATBOT_GUIDE.md](CHATBOT_GUIDE.md) - Detailed chatbot usage and customization
- [INTERNET_SOURCES_GUIDE.md](INTERNET_SOURCES_GUIDE.md) - Internet sources configuration and privacy
- [README.md](README.md) - This file

## Performance

- **Local only (CSV)**: ~100ms
- **With internet sources**: ~2-5s (graceful fallback if sources unavailable)
- **Caching**: 5-minute TTL for internet results
- **Rate limits**: Respects GitHub (60-5000 req/hour), Stack Overflow (300 req/day)

## Privacy & Security

### What's sent to internet APIs:
- Incident description/keywords
- Service/system names
- Error messages

### What's NOT sent:
- Company name
- User identification  
- Complete incident details
- Business metrics

Internet sources are optional and can be completely disabled in configuration.

## Troubleshooting

### Internet sources not working?
1. Check network connectivity (firewall may block outbound HTTPS)
2. Verify API availability via `/data-sources` endpoint
3. Check Python logs for specific API errors
4. Set `GITHUB_TOKEN` for higher rate limits
5. Disable unused sources to improve performance

### Slow analysis?
1. Internet sources may timeout → Falls back to local
2. Toggle "Use Internet Sources" to false for speed
3. Reduce `max_results` in `config.py`
4. Check network latency

### No internet sources available?
1. System falls back to local database automatically
2. Check internet connectivity
3. Verify API endpoints are accessible
4. Review logs for timeout/auth errors

## File Structure

```
rca-gemini-agent/
├── README.md
├── CHATBOT_GUIDE.md
├── INTERNET_SOURCES_GUIDE.md
├── requirements.txt
├── ai-engine/
│   ├── app.py (Flask backend with internet support)
│   ├── gemini_rca.py
│   ├── similarity.py (Enhanced with internet sources)
│   ├── open_source_data.py (NEW: Internet data fetching)
│   ├── config.py (NEW: Source configuration)
│   ├── data/incidents.csv
│   └── __pycache__/
├── backend-node/
│   ├── server.js
│   ├── package.json
│   └── node_modules/
└── frontend/
    ├── index.html
    ├── chatbot.html
    ├── app.js
    ├── chatbot.js
    ├── style.css
    └── chatbot-style.css
```

---

**Version**: 2.0 (with Internet Sources)  
**Last Updated**: June 14, 2026  
**Status**: Production Ready
