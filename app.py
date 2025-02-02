import streamlit as st
import requests
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MultiLabelBinarizer
from gensim import corpora
from gensim.models import LdaModel
import nltk
from nltk.corpus import stopwords
import re

# Download NLTK stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

# Open Library API base URL
OPEN_LIBRARY_API = "https://openlibrary.org/search.json"

# Function to fetch book data from Open Library
def fetch_books(query, limit=100):
    params = {"q": query, "limit": limit}
    response = requests.get(OPEN_LIBRARY_API, params=params)
    if response.status_code == 200:
        data = response.json()
        books = []
        for doc in data.get("docs", []):
            book = {
                "title": doc.get("title", ""),
                "author": doc.get("author_name", [""])[0],
                "genre": doc.get("subject", []),
                "year": doc.get("first_publish_year", None),
                "description": doc.get("first_sentence", [""])[0] if doc.get("first_sentence") else ""
            }
            books.append(book)
        return books
    else:
        st.error("Failed to fetch data from Open Library.")
        return []

# Function to preprocess text
def preprocess_text(text):
    text = re.sub(r'\W', ' ', text.lower())  # Remove special characters and lowercase
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]  # Remove stopwords
    return ' '.join(tokens)

# Function to extract topics using LDA
def extract_topics(descriptions, num_topics=5):
    processed_texts = [preprocess_text(desc) for desc in descriptions]
    tokenized_texts = [text.split() for text in processed_texts]
    dictionary = corpora.Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    topics = []
    for text in tokenized_texts:
        bow = dictionary.doc2bow(text)
        topic_distribution = lda_model.get_document_topics(bow)
        topics.append(max(topic_distribution, key=lambda x: x[1])[0])
    return topics

# Function to compute similarity and recommend books
def recommend_books(input_books, all_books, top_n=20):
    # Combine features
    input_descriptions = [book["description"] for book in input_books]
    all_descriptions = [book["description"] for book in all_books]
    input_genres = [book["genre"] for book in input_books]
    all_genres = [book["genre"] for book in all_books]

    # Extract topics
    input_topics = extract_topics(input_descriptions)
    all_topics = extract_topics(all_descriptions)

    # Encode genres
    mlb = MultiLabelBinarizer()
    input_genres_encoded = mlb.fit_transform(input_genres)
    all_genres_encoded = mlb.transform(all_genres)

    # TF-IDF for descriptions
    vectorizer = TfidfVectorizer()
    input_tfidf = vectorizer.fit_transform(input_descriptions)
    all_tfidf = vectorizer.transform(all_descriptions)

    # Combine features
    input_features = np.hstack((input_tfidf.toarray(), input_genres_encoded, np.array(input_topics).reshape(-1, 1)))
    all_features = np.hstack((all_tfidf.toarray(), all_genres_encoded, np.array(all_topics).reshape(-1, 1)))

    # Compute similarity
    similarity_scores = cosine_similarity(input_features, all_features)
    avg_similarity = similarity_scores.mean(axis=0)

    # Rank and recommend
    ranked_indices = np.argsort(avg_similarity)[::-1][:top_n]
    recommendations = [all_books[i] for i in ranked_indices]
    return recommendations

# Streamlit App
def main():
    st.title("Book Recommendation System")
    st.write("Input 100 books to get recommendations based on topic, genre, and a 20-year time frame.")

    # Input query
    query = st.text_input("Enter a search query (e.g., 'science fiction'):")
    if not query:
        st.stop()

    # Fetch books
    st.write("Fetching books...")
    books = fetch_books(query, limit=100)
    if not books:
        st.stop()

    # Filter by time frame
    st.write("Filtering by time frame...")
    current_year = pd.Timestamp.now().year
    filtered_books = [book for book in books if book["year"] and (current_year - 20) <= book["year"] <= current_year]

    # Display input books
    st.write(f"Found {len(filtered_books)} books within the last 20 years.")
    if st.checkbox("Show input books"):
        st.write(pd.DataFrame(filtered_books))

    # Recommend books
    if st.button("Get Recommendations"):
        st.write("Generating recommendations...")
        recommendations = recommend_books(filtered_books, filtered_books)
        st.write("Top 20 Recommendations:")
        st.write(pd.DataFrame(recommendations))

if __name__ == "__main__":
    main()
