import streamlit as st
import requests
from itertools import product

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
def search_books(query, limit=10):
    url = f"{BASE_URL}/search.json?q={query}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("docs", [])
    return []

# Function to fetch book details
def fetch_book_details(olid):
    url = f"{BASE_URL}/works/{olid}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch author details
def fetch_author_details(author_key):
    url = f"{BASE_URL}/authors/{author_key}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

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
            books.extend(search_books(query, limit=5))
        
        unique_books = {book["key"]: book for book in books}.values()
        top_books = list(unique_books)[:20]
        
        if top_books:
            for book in top_books:
                title = book.get("title", "Unknown Title")
                authors = book.get("author_key", [])
                author_names = ", ".join(book.get("author_name", ["Unknown Author"]))
                publish_year = book.get("first_publish_year", "Unknown Year")
                olid = book.get("key", "").split("/")[-1]
                cover_id = book.get("cover_i")
                description = "No description available."
                
                book_details = fetch_book_details(olid)
                if book_details:
                    description = book_details.get("description", description)
                    if isinstance(description, dict):
                        description = description.get("value", "No description available.")
                
                st.markdown("---")
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    if cover_id:
                        st.image(f"{COVER_URL}{cover_id}-M.jpg", use_container_width=True)
                    else:
                        st.write("No Cover Available")
                
                with col2:
                    st.subheader(title)
                    st.write(f"**Author:** {author_names}")
                    st.write(f"**Publish Year:** {publish_year}")
                    st.write(f"**Description:** {description}")
                    
                    if authors:
                        author_details = fetch_author_details(authors[0])
                        if author_details and "photos" in author_details:
                            author_image_id = author_details["photos"][0]
                            st.image(f"{COVER_URL}{author_image_id}-M.jpg", width=100, caption=author_names)
                        else:
                            st.write("No Author Image Available")
        else:
            st.write("No books found for your selections.")

if __name__ == "__main__":
    main()
