import streamlit as st
import requests
import pandas as pd
from itertools import product
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Open Library API base URL
BASE_URL = "https://openlibrary.org"
COVER_URL = "https://covers.openlibrary.org/b/id/"

# Literature topics, genres, and time frames
literature_topics = [
    "poetry", "drama", "prose", "epic", "satire", "fable", "gothic", "fantasy", "mythology", "romance", 
    "horror", "mystery", "science fiction", "historical", "graphic novels", "dystopian", "short stories", 
    "autobiography", "biography", "memoir", "travel", "philosophy", "psychology", "self-help", "spirituality", 
    "classic", "contemporary", "war", "adventure", "crime", "detective", "thriller", "western", "comedy", 
    "children's literature", "young adult", "fairy tales", "legends", "folklore", "literary criticism", "modernist"
]

genre_options = [
    "fiction", "non-fiction", "mystery", "romance", "fantasy", "biography", "adventure", "horror", "thriller", 
    "science fiction", "historical", "drama", "philosophy", "self-help", "psychology", "spirituality", "dystopian", 
    "young adult", "children", "graphic novels"
]

time_frames = [
    "1800-1820", "1821-1840", "1841-1860", "1861-1880", "1881-1900",
    "1901-1920", "1921-1940", "1941-1960", "1961-1980", "1981-2000", "2001-2020"
]

# Function to search books using Open Library Search API
def search_books(query, limit=100):
    url = f"{BASE_URL}/search.json?q={query}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("docs", [])
    return []

# Function to get the most common books using TF-IDF and cosine similarity
def get_top_books(books):
    if not books:
        return []
    
    book_titles = [book.get("title", "") for book in books]
    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(book_titles)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    book_scores = Counter()
    for i, row in enumerate(similarity_matrix):
        book_scores[i] = sum(row)
    
    top_indices = [index for index, _ in book_scores.most_common(20)]
    return [books[i] for i in top_indices]

# Streamlit App
def main():
    st.set_page_config(page_title="Book Recommendation App", layout="wide")
    st.title("📚 Book Recommendation Dashboard")
    st.write("Discover books based on your preferences!")

    # Sidebar for user selections
    with st.sidebar:
        st.header("Filter Books")
        selected_topics = st.multiselect("Select Literature Topics:", literature_topics)
        selected_genres = st.multiselect("Select Genres:", genre_options)
        selected_time_frames = st.multiselect("Select Time Frames:", time_frames)
        if st.button("Get Recommendations"):
            st.session_state.recommend = True
    
    if "recommend" in st.session_state:
        st.subheader("Top 20 Books Based on Your Selections:")
        all_queries = [f"{topic} {genre} {time}" for topic, genre, time in product(selected_topics, selected_genres, selected_time_frames)]
        books = []
        
        for query in all_queries:
            books.extend(search_books(query, limit=100))
        
        top_books = get_top_books(books)
        
        if top_books:
            for book in top_books:
                title = book.get("title", "Unknown Title")
                authors = book.get("author_name", ["Unknown Author"])
                publish_year = book.get("first_publish_year", "Unknown Year")
                cover_id = book.get("cover_i")
                
                st.markdown("---")
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if cover_id:
                        st.image(f"{COVER_URL}{cover_id}-M.jpg", use_container_width=True)
                    else:
                        st.write("No Cover Available")
                
                with col2:
                    st.subheader(title)
                    st.write(f"**Author:** {', '.join(authors)}")
                    st.write(f"**Publish Year:** {publish_year}")
        else:
            st.write("No books found for your selections.")

if __name__ == "__main__":
    main()
