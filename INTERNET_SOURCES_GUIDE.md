# Internet Sources Integration Guide

## Overview

The RCA Gemini Agent now fetches incident and problem data from open-source internet sources to supplement local analysis. This significantly enhances the quality of RCA by comparing issues against real-world solutions from GitHub, Stack Overflow, security advisories, and status pages.

## 🌐 Available Data Sources

### 1. **GitHub Issues** 🐙
- **Source**: Public GitHub repositories
- **Data**: Issue reports, discussions, error messages
- **Use Cases**: 
  - Find how others resolved similar technical issues
  - Discover known bugs and workarounds
  - Access patch information and fixes
- **Example**: Searching "database connection timeout" finds resolved issues from popular projects

### 2. **Stack Overflow** 📚
- **Source**: Stack Overflow Q&A platform
- **Data**: Technical questions, answers, solutions
- **Use Cases**:
  - Find best practices and common solutions
  - Learn from community expertise
  - Get multiple perspectives on problems
- **Example**: "Slow API response" returns solutions tagged with performance optimization

### 3. **CISA/NVD Security Advisories** 🔒
- **Source**: National Vulnerability Database
- **Data**: CVE advisories, security vulnerabilities
- **Use Cases**:
  - Identify security-related root causes
  - Get official remediation guidance
  - Check for known exploits
- **Example**: "SQL injection" returns relevant CVE information

### 4. **Public Status Pages** 📊
- **Source**: GitHub Status, Cloudflare Status, and other public status pages
- **Data**: Service incidents, outages, postmortems
- **Use Cases**:
  - Learn from major platform outages
  - Understand infrastructure-level issues
  - Get incident timelines and resolutions
- **Example**: "Service down" may match known cloud provider outages

### 5. **Local Database** 💾
- **Source**: incidents.csv (your local incident history)
- **Data**: Historical incidents from your organization
- **Use Cases**:
  - Reference previous similar incidents
  - Maintain institutional knowledge
  - Ensure consistency with local practices
- **Note**: Always enabled; other sources augment it

## 🔧 Configuration

### Enable/Disable Sources

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

### Control per Request

Toggle in UI: Check/uncheck "🌐 Use Internet Sources" before analyzing
Or via API:
```json
{
  "description": "Payment service is down",
  "use_internet_sources": true
}
```

## 📊 How It Works

```
User Input
    ↓
[Incident Analysis]
    ↓
+───────────────────────────────────────────┐
│ Data Collection (if enabled)              │
├───────────────────────────────────────────┤
│ 1. Fetch from GitHub issues               │
│ 2. Fetch from Stack Overflow              │
│ 3. Fetch CISA security advisories         │
│ 4. Check public status pages              │
│ 5. Load local incidents.csv               │
└───────────────────────────────────────────┘
    ↓
[TF-IDF Similarity Matching]
    ↓
Rank incidents by relevance (score 0-1)
    ↓
[Gemini RCA Analysis]
    ↓
+──────────────────────────┐
│ Generate:                │
│ - Root causes            │
│ - Recommended actions    │
│ - Risk assessment        │
│ - Confidence level       │
└──────────────────────────┘
    ↓
Display Results with Source Attribution
```

## 🔌 API Endpoints

### Get Available Data Sources
```bash
GET /data-sources
```

Response:
```json
{
  "sources": {
    "github": {"enabled": true, "description": "GitHub public issues..."},
    "stackoverflow": {"enabled": true, "description": "Stack Overflow Q&A..."},
    ...
  }
}
```

### Analyze with Internet Sources
```bash
POST /analyze
Content-Type: application/json

{
  "description": "Database timeout errors",
  "use_internet_sources": true
}
```

Response includes:
```json
{
  "similar_incidents": [
    {
      "source": "GitHub",
      "incident_id": "GH-12345",
      "title": "...",
      "description": "...",
      "url": "...",
      "labels": [...],
      "score": 0.85
    }
  ],
  "data_sources_used": ["GitHub", "Stack Overflow", "Local Database"],
  "rca_analysis": {...}
}
```

## 🎯 Best Practices

### 1. **Include Specific Error Messages**
Instead of: "API is slow"
Try: "API returning 503 Service Unavailable errors, timeout after 30 seconds"

### 2. **Mention Technology Stack**
Include framework/language: "Node.js API", "Python Flask service", "MySQL database"

### 3. **Provide Context**
- When did it start?
- Did anything change recently?
- How many users affected?
- What services depend on this?

### 4. **Enable Internet Sources for Unknown Issues**
- New incidents with unfamiliar patterns → Enable internet sources
- Recurring known issues → Can rely on local database

### 5. **Review Source Attribution**
Check "Data Sources" badge to understand:
- Which sources contributed to the analysis
- Whether it's based on local vs. external data
- Credibility of similar incidents

## 🔐 Privacy & Security

### Data Sent to External Services
When internet sources enabled, this data is sent:
- Incident description/keywords
- Service/system names
- Error messages

### NOT Sent
- Your company name
- User identification
- Complete incident details (truncated)
- Business metrics

### API Authentication
- **GitHub**: Optional token (for higher rate limits)
- **Stack Overflow**: No auth needed (public API)
- **CISA**: No auth needed (public API)
- **Status Pages**: No auth needed (public APIs)

Set GitHub token (optional):
```bash
setx GITHUB_TOKEN "your_token_here"
```

## 📈 Performance Considerations

### Response Times
- **Local only** (CSV): ~100ms
- **With internet sources**: ~2-5 seconds (depends on API availability)
- **On network issues**: Falls back to local data gracefully

### Rate Limits
- **GitHub API**: 60 req/hour (unauthenticated), 5000 req/hour (authenticated)
- **Stack Overflow**: 300 req/day (fair use)
- **CISA NVD**: No specific limit

### Optimization
If performance is critical:
1. Disable less-used sources in config.py
2. Reduce max_results per source
3. Cache responses (TTL: 300 seconds)
4. Set GitHub token for better rate limits

## 🐛 Troubleshooting

### Internet Sources Not Working
1. **Check internet connection**: Required for external APIs
2. **Firewall rules**: Ensure outbound HTTPS is allowed
3. **API Availability**: Try `/data-sources` endpoint to verify connectivity
4. **Logs**: Check Python logs for specific API errors

### Slow Analysis
- Internet sources may timeout → Falls back to local
- Use "Local only" toggle if speed is critical
- Check network latency with:
  ```bash
  curl -w "@curl-format.txt" https://api.github.com/
  ```

### No Similar Incidents Found
1. Query may be too specific → Try more general terms
2. All sources offline → Falls back to local CSV
3. Local CSV empty → Populate incidents.csv
4. Try different phrasing of the issue

### False Matches
- Low similarity scores (< 50%) are less reliable
- Review source context before acting
- Confirm match is applicable to your case
- Mark as irrelevant to improve future matches

## 📝 Example Scenarios

### Scenario 1: Database Connection Issue

**User Input**: "Database connection timeout. Started after we upgraded MySQL from 5.7 to 8.0"

**Internet Sources Find**:
- GitHub: MySQL 8.0 connection pool issues (#4521)
- Stack Overflow: Performance degradation after upgrade
- Local DB: Similar incident 3 months ago with solution

**Result**: AI correlates all sources → Recommends connection pool adjustment

### Scenario 2: Security Vulnerability

**User Input**: "Suspicious SQL errors in logs, could be injection attack"

**Internet Sources Find**:
- CISA: Recent CVE-2024-XXXXX SQL injection in popular framework
- Stack Overflow: Mitigation strategies
- Local DB: No similar incidents

**Result**: AI escalates to CRITICAL, provides CVE-specific guidance

### Scenario 3: Unknown Error

**User Input**: "Getting error code E-2847, never seen before"

**Internet Sources Find**:
- GitHub: Exact error code in issue tracker with solution
- Stack Overflow: Community workarounds
- Local DB: No match

**Result**: Internet sources provide breakthrough vs. local-only dead end

## 🔄 Feedback Loop

The system learns from internet sources:
1. When similar incidents found → Success rate increases
2. When no matches → May suggest adding to local database
3. When patterns repeat → Can adjust similarity thresholds
4. User feedback → Improves relevance of AI responses

## 📚 Related Files

**Modified:**
- `ai-engine/similarity.py` - Now fetches internet data
- `ai-engine/app.py` - Added /data-sources endpoint
- `frontend/app.js` - Internet source toggle
- `frontend/index.html` - UI for source selection

**New:**
- `ai-engine/open_source_data.py` - Internet data fetching
- `ai-engine/config.py` - Source configuration
- `requirements.txt` - Added `requests` library

---

**Internet Sources Version**: 1.0  
**Last Updated**: June 14, 2026  
**Status**: Production Ready

## Support

For issues with internet sources integration:
1. Check configuration in `config.py`
2. Review API connectivity
3. Check Python logs for detailed errors
4. Fall back to local-only mode if needed
5. Report persistent issues with error details
