import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_incident_by_id(incident_id):
    """Fetch a specific incident from the database by its ID."""
    data_path = Path(__file__).resolve().parent / "data" / "incidents.csv"
    df = pd.read_csv(data_path)
    
    try:
        # Try to convert incident_id to int if it's numeric
        id_value = int(incident_id) if incident_id.isdigit() else incident_id
    except (ValueError, AttributeError):
        return None
    
    result = df[df["incident_id"] == id_value]
    if result.empty:
        return None
    
    return result.iloc[0].to_dict()

def find_similar(incident_text):
    data_path = Path(__file__).resolve().parent / "data" / "incidents.csv"
    df = pd.read_csv(data_path)

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df["description"].tolist() + [incident_text])

    similarity_scores = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    df["score"] = similarity_scores

    top3 = df.sort_values("score", ascending=False).head(3)
    return top3.to_dict(orient="records")