import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
from open_source_data import get_internet_incidents

logger = logging.getLogger(__name__)

def get_local_incidents():
    """Load incidents from local CSV file."""
    try:
        data_path = Path(__file__).resolve().parent / "data" / "incidents.csv"
        if data_path.exists():
            return pd.read_csv(data_path)
    except Exception as e:
        logger.warning(f"Error loading local incidents: {str(e)}")
    return pd.DataFrame()

def get_incident_by_id(incident_id):
    """Fetch a specific incident from the database by its ID (local only)."""
    df = get_local_incidents()
    
    if df.empty:
        return None
    
    try:
        # Try to convert incident_id to int if it's numeric
        id_value = int(incident_id) if incident_id.isdigit() else incident_id
    except (ValueError, AttributeError):
        return None
    
    result = df[df["incident_id"] == id_value]
    if result.empty:
        return None
    
    return result.iloc[0].to_dict()

def find_similar(incident_text, use_internet_sources=True):
    """
    Find similar incidents from both local CSV and internet sources.
    
    Args:
        incident_text: Description of the incident to match
        use_internet_sources: Whether to fetch data from internet (default: True)
    
    Returns:
        List of similar incidents sorted by similarity score
    """
    all_incidents = []
    
    # Get local incidents from CSV
    df_local = get_local_incidents()
    if not df_local.empty:
        all_incidents.extend(df_local.to_dict(orient="records"))
    
    # Try to get internet-based incidents
    if use_internet_sources:
        try:
            internet_incidents = get_internet_incidents(incident_text, max_results=5)
            all_incidents.extend(internet_incidents)
            logger.info(f"Found {len(internet_incidents)} incidents from internet sources")
        except Exception as e:
            logger.warning(f"Could not fetch internet incidents: {str(e)}. Falling back to local data only.")
    
    # If no incidents found at all, return empty
    if not all_incidents:
        logger.warning("No incidents found from any source")
        return []
    
    # Prepare data for similarity calculation
    descriptions = [
        incident.get("description", incident.get("title", ""))
        for incident in all_incidents
    ]
    
    # Handle empty descriptions
    descriptions = [d if d and isinstance(d, str) else "" for d in descriptions]
    
    # If all descriptions are empty, return top incidents as-is
    if not any(descriptions):
        return all_incidents[:3]
    
    try:
        # TF-IDF similarity matching
        vectorizer = TfidfVectorizer(stop_words="english", max_features=1000)
        vectors = vectorizer.fit_transform(descriptions + [incident_text])
        
        similarity_scores = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
        
        # Add scores to incidents
        for idx, incident in enumerate(all_incidents):
            incident["score"] = float(similarity_scores[idx])
        
        # Sort by score and return top 3
        sorted_incidents = sorted(all_incidents, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_incidents[:3]
        
    except Exception as e:
        logger.error(f"Error in similarity calculation: {str(e)}")
        # Return top incidents without similarity scoring
        return all_incidents[:3]