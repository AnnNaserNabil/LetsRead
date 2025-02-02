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

# Streamlit App
def main():
    st.title("Book Recommendation App")
    st.write("Discover books based on your preferences!")

    # User selections in sidebar
    with st.sidebar:
        selected_topics = st.multiselect("Select Literature Topics:", literature_topics)
        selected_genres = st.multiselect("Select Genres:", genre_options)
        selected_time_frames = st.multiselect("Select Time Frames:", time_frames)
        st.write("Press the button below to get recommendations.")
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
                author = ", ".join(book.get("author_name", ["Unknown Author"]))
                publish_year = book.get("first_publish_year", "Unknown Year")
                olid = book.get("key", "").split("/")[-1]
                pages = book.get("number_of_pages_median", "Unknown Pages")
                cover_id = book.get("cover_i")
                description = "No description available."
                
                book_details = fetch_book_details(olid)
                if book_details:
                    description = book_details.get("description", description)
                    if isinstance(description, dict):
                        description = description.get("value", "No description available.")
                
                st.subheader(title)
                st.write(f"**Author:** {author}")
                st.write(f"**Publish Year:** {publish_year}")
                st.write(f"**Total Pages:** {pages}")
                st.write(f"**Description:** {description}")
                if cover_id:
                    st.image(f"{COVER_URL}{cover_id}-M.jpg", caption=title)
                st.write("---")
        else:
            st.write("No books found for your selections.")

if __name__ == "__main__":
    main()
