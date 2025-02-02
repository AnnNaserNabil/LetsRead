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
                "title": doc.get("title", "Unknown Title"),
                "author": doc.get("author_name", ["Unknown Author"])[0],
                "genre": doc.get("subject", ["Unknown Genre"]),
                "year": doc.get("first_publish_year", None),
                "description": doc.get("first_sentence", ["No description available"])[0],
                "cover_id": doc.get("cover_i", None),
                "author_id": doc.get("author_key", [None])[0]
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
    processed_texts = [preprocess_text(desc) for desc in descriptions if desc.strip()]
    if not processed_texts:
        return [0] * len(descriptions)  # Return dummy topic if no descriptions are available

    tokenized_texts = [text.split() for text in processed_texts]
    dictionary = corpora.Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=15)
    topics = []
    for text in tokenized_texts:
        bow = dictionary.doc2bow(text)
        topic_distribution = lda_model.get_document_topics(bow)
        topics.append(max(topic_distribution, key=lambda x: x[1])[0] if topic_distribution else 0)
    return topics

# Function to compute similarity and recommend books
def recommend_books(input_books, all_books, top_n=20):
    if not input_books or not all_books:
        st.error("No sufficient data to compute recommendations.")
        return []

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
    mlb.fit(all_genres)
    input_genres_encoded = mlb.transform(input_genres)
    all_genres_encoded = mlb.transform(all_genres)

    # TF-IDF for descriptions
    vectorizer = TfidfVectorizer()
    all_tfidf = vectorizer.fit_transform(all_descriptions)
    input_tfidf = vectorizer.transform(input_descriptions)

    # Combine features
    input_features = np.hstack((input_tfidf.toarray(), input_genres_encoded, np.array(input_topics).reshape(-1, 1)))
    all_features = np.hstack((all_tfidf.toarray(), all_genres_encoded, np.array(all_topics).reshape(-1, 1)))

    if input_features.shape[0] == 0 or all_features.shape[0] == 0:
        st.error("Not enough data to compute recommendations.")
        return []

    # Compute similarity
    similarity_scores = cosine_similarity(input_features, all_features)
    avg_similarity = similarity_scores.mean(axis=0)

    # Rank and recommend
    ranked_indices = np.argsort(avg_similarity)[::-1][:top_n]
    recommendations = [all_books[i] for i in ranked_indices]
    return recommendations

# Streamlit App
def main():
    st.set_page_config(page_title="Book Recommendation System", layout="wide")
    
    # Sidebar Inputs
    st.sidebar.title("Book Search")
    query = st.sidebar.text_input("Enter a search query (e.g., 'science fiction'):")
    
    if not query:
        st.sidebar.warning("Please enter a search query.")
        return

    # Fetch books
    st.sidebar.write("Fetching books...")
    books = fetch_books(query, limit=100)
    if not books:
        return

    # Filter by time frame
    current_year = pd.Timestamp.now().year
    filtered_books = [book for book in books if book["year"] and (current_year - 20) <= book["year"] <= current_year]

    st.sidebar.write(f"Books found: **{len(filtered_books)}**")

    if not filtered_books:
        st.warning("No books found within the last 20 years.")
        return

    # Recommend books
    if st.sidebar.button("Get Recommendations"):
        st.sidebar.write("Generating recommendations...")
        recommendations = recommend_books(filtered_books, filtered_books)

        st.title("📚 Recommended Books")
        if recommendations:
            for book in recommendations[:20]:
                col1, col2 = st.columns([1, 3])
                with col1:
                    if book["cover_id"]:
                        st.image(f"https://covers.openlibrary.org/b/id/{book['cover_id']}-M.jpg", use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/150", use_container_width=True)

                with col2:
                    st.markdown(f"### {book['title']}")
                    st.markdown(f"**Author:** {book['author']}")
                    if book["author_id"]:
                        st.image(f"https://covers.openlibrary.org/a/olid/{book['author_id']}-M.jpg", width=100)
                    st.markdown(f"**Published Year:** {book['year']}")
                    st.markdown(f"**Description:** {book['description']}")
                    st.write("---")

if __name__ == "__main__":
    main()
