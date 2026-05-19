import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def find_similar(incident_text):
    df = pd.read_csv("data/incidents.csv")

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(df["description"].tolist() + [incident_text])

    similarity_scores = cosine_similarity(vectors[-1], vectors[:-1]).flatten()
    df["score"] = similarity_scores

    top3 = df.sort_values("score", ascending=False).head(3)
    return top3.to_dict(orient="records")