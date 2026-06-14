"""
Open source internet data fetcher for incidents and problems.
Fetches data from various public sources to supplement RCA analysis.
"""

import requests
import json
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
import os

logger = logging.getLogger(__name__)

class OpenSourceDataFetcher:
    """Fetches incident and problem data from open internet sources"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", None)
        self.timeout = 5  # seconds
        
    def fetch_github_issues(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Fetch relevant issues from GitHub public repositories.
        Searches for issues related to common infrastructure problems.
        """
        try:
            # Search for high-starred repos with issues matching the query
            search_query = f"{query} in:title,body type:issue is:public stars:>100"
            url = "https://api.github.com/search/issues"
            
            headers = {}
            if self.github_token:
                headers["Authorization"] = f"token {self.github_token}"
            
            params = {
                "q": search_query,
                "sort": "stars",
                "order": "desc",
                "per_page": max_results
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            incidents = []
            
            for item in data.get("items", [])[:max_results]:
                incidents.append({
                    "source": "GitHub",
                    "incident_id": f"GH-{item['number']}",
                    "title": item.get("title", ""),
                    "description": item.get("body", "")[:500],
                    "url": item.get("html_url", ""),
                    "repository": item.get("repository_url", "").split("/")[-1],
                    "created_at": item.get("created_at", ""),
                    "labels": [label.get("name", "") for label in item.get("labels", [])],
                    "score": 0.0  # Will be set by similarity matching
                })
            
            return incidents
            
        except Exception as e:
            logger.warning(f"Error fetching GitHub issues: {str(e)}")
            return []
    
    def fetch_stack_overflow_tags(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Fetch relevant questions from Stack Overflow for common IT problems.
        """
        try:
            # Map common incident keywords to SO tags
            tag_mapping = {
                "database": "database",
                "connection": "connections",
                "timeout": "timeout",
                "crash": "crash",
                "memory": "memory",
                "cpu": "cpu",
                "disk": "disk-space",
                "network": "networking",
                "performance": "performance",
                "latency": "latency",
                "authentication": "authentication",
                "api": "api",
                "service": "microservices",
                "load": "load-balancing",
            }
            
            # Find relevant tags
            tags = []
            for keyword, tag in tag_mapping.items():
                if keyword.lower() in query.lower():
                    tags.append(tag)
            
            if not tags:
                tags = ["server-administration"]
            
            url = "https://api.stackexchange.com/2.3/questions"
            
            params = {
                "order": "desc",
                "sort": "votes",
                "tagged": ";".join(tags[:3]),
                "site": "stackoverflow",
                "pagesize": max_results,
                "filter": "!9_bDE8THJedRPmjH_"
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            incidents = []
            
            for item in data.get("items", [])[:max_results]:
                incidents.append({
                    "source": "Stack Overflow",
                    "incident_id": f"SO-{item['question_id']}",
                    "title": item.get("title", ""),
                    "description": f"Tags: {', '.join(item.get('tags', []))}. {item.get('title', '')}",
                    "url": item.get("link", ""),
                    "score": item.get("score", 0),
                    "views": item.get("view_count", 0),
                    "answers": item.get("answer_count", 0),
                    "score_normalized": 0.0  # Will be set by similarity matching
                })
            
            return incidents
            
        except Exception as e:
            logger.warning(f"Error fetching Stack Overflow data: {str(e)}")
            return []
    
    def fetch_cisa_advisories(self, query: str, max_results: int = 3) -> List[Dict]:
        """
        Fetch relevant CISA (Cybersecurity & Infrastructure Security Agency) advisories.
        Useful for security-related incidents.
        """
        try:
            url = "https://services.nvd.nist.gov/rest/json/cves/1.0"
            
            # Only fetch if it looks like a security issue
            security_keywords = ["exploit", "vulnerability", "breach", "security", "cve", "injection", "sql"]
            if not any(keyword in query.lower() for keyword in security_keywords):
                return []
            
            params = {
                "keyword": query,
                "resultsPerPage": max_results
            }
            
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            incidents = []
            
            for item in data.get("result", {}).get("CVE_Items", [])[:max_results]:
                cve_id = item.get("cve", {}).get("CVE_data_meta", {}).get("ID", "")
                description = item.get("cve", {}).get("description", {}).get("description_data", [])
                desc_text = description[0].get("value", "") if description else ""
                
                incidents.append({
                    "source": "CISA/NVD",
                    "incident_id": cve_id,
                    "title": f"Security Advisory: {cve_id}",
                    "description": desc_text[:500],
                    "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                    "type": "security",
                    "score": 0.0
                })
            
            return incidents
            
        except Exception as e:
            logger.warning(f"Error fetching CISA advisories: {str(e)}")
            return []
    
    def fetch_status_page_incidents(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        Fetch incidents from public status pages (e.g., status.io services).
        This is a mock implementation as most require authentication.
        """
        try:
            # Popular public status pages that provide incidents
            status_pages = [
                "https://www.githubstatus.com/api/v2/incidents.json",
                "https://www.cloudflarestatus.com/api/v2/incidents.json",
            ]
            
            incidents = []
            
            for page_url in status_pages:
                try:
                    response = requests.get(page_url, timeout=self.timeout)
                    response.raise_for_status()
                    
                    data = response.json()
                    
                    for item in data.get("incidents", [])[:2]:
                        if query.lower() in item.get("name", "").lower():
                            incidents.append({
                                "source": page_url.split("/")[2],
                                "incident_id": f"INC-{item['id']}",
                                "title": item.get("name", ""),
                                "description": item.get("impact", ""),
                                "status": item.get("status", ""),
                                "created_at": item.get("created_at", ""),
                                "updated_at": item.get("updated_at", ""),
                                "score": 0.0
                            })
                except:
                    continue
            
            return incidents[:max_results]
            
        except Exception as e:
            logger.warning(f"Error fetching status page incidents: {str(e)}")
            return []
    
    def fetch_all_sources(self, query: str, max_results_per_source: int = 3) -> List[Dict]:
        """
        Fetch incidents from all available open-source internet sources.
        Falls back gracefully if any source is unavailable.
        """
        all_incidents = []
        
        # Fetch from each source
        all_incidents.extend(self.fetch_github_issues(query, max_results_per_source))
        all_incidents.extend(self.fetch_stack_overflow_tags(query, max_results_per_source))
        all_incidents.extend(self.fetch_cisa_advisories(query, max_results_per_source // 2))
        all_incidents.extend(self.fetch_status_page_incidents(query, max_results_per_source))
        
        logger.info(f"Fetched {len(all_incidents)} incidents from open sources for query: {query}")
        return all_incidents


def get_internet_incidents(query: str, max_results: int = 5) -> List[Dict]:
    """
    Convenience function to fetch incidents from all internet sources.
    """
    fetcher = OpenSourceDataFetcher()
    return fetcher.fetch_all_sources(query, max_results_per_source=max_results)
