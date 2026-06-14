# Configuration for open-source data fetching

"""
Open Source Data Sources Configuration

Controls which internet sources are used for incident data fetching.
"""

# Enable/disable specific data sources
DATA_SOURCES = {
    "github": {
        "enabled": True,
        "description": "GitHub public issues and discussions",
        "max_results": 3,
        "timeout": 5
    },
    "stackoverflow": {
        "enabled": True,
        "description": "Stack Overflow technical Q&A",
        "max_results": 3,
        "timeout": 5
    },
    "cisa": {
        "enabled": True,
        "description": "CISA security advisories and CVEs",
        "max_results": 2,
        "timeout": 5
    },
    "status_pages": {
        "enabled": True,
        "description": "Public status pages (GitHub, Cloudflare, etc.)",
        "max_results": 2,
        "timeout": 5
    },
    "local_csv": {
        "enabled": True,
        "description": "Local incidents.csv database",
        "max_results": 5,
        "timeout": 0
    }
}

# Incident keywords that trigger internet search
SEARCH_KEYWORDS = [
    "down", "crash", "outage", "error", "timeout", "slow",
    "broken", "failed", "not working", "offline", "unavailable",
    "bug", "issue", "problem", "failure", "service",
    "database", "api", "network", "connection", "authentication",
    "memory", "cpu", "disk", "performance", "latency"
]

# Risk level thresholds
RISK_LEVELS = {
    "low": {"threshold": 0.3, "impact": "Minimal impact"},
    "medium": {"threshold": 0.6, "impact": "Moderate impact"},
    "high": {"threshold": 0.8, "impact": "Significant impact"},
    "critical": {"threshold": 1.0, "impact": "Revenue/service blocking"}
}

# Similarity score thresholds
SIMILARITY_THRESHOLDS = {
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25
}

# Cache settings (in seconds)
CACHE_TTL = 300  # 5 minutes

# Enable logging
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"
