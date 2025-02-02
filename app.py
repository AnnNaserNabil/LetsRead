import streamlit as st
import requests

# Open Library API base URL
BASE_URL = "https://openlibrary.org"
COVER_URL = "https://covers.openlibrary.org/b/id/"

# Function to search books using Open Library Search API
def search_books(query, limit=10):
    url = f"{BASE_URL}/search.json?q={query}&limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("docs", [])
    return []

# Function to fetch book details by Open Library Work ID
def fetch_book_details(olid):
    url = f"{BASE_URL}/works/{olid}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Function to fetch author details
def fetch_author_details(author_olid):
    url = f"{BASE_URL}/authors/{author_olid}.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Streamlit App
def main():
    st.title("Book Recommendation App")
    st.write("Discover books based on your preferences!")

    # User selections
    content_options = ["science", "history", "technology", "philosophy", "art", "literature"]
    genre_options = ["fiction", "non-fiction", "mystery", "romance", "fantasy", "biography"]
    era_options = [
        "1800-1820", "1821-1840", "1841-1860", "1861-1880", "1881-1900",
        "1901-1920", "1921-1940", "1941-1960", "1961-1980", "1981-2000", "2001-2020"
    ]

    selected_content = st.multiselect("Select content topics:", content_options)
    selected_genre = st.multiselect("Select genres:", genre_options)
    selected_era = st.multiselect("Select time frames (20-year intervals):", era_options)

    if st.button("Get Recommendations"):
        if not selected_content or not selected_genre or not selected_era:
            st.warning("Please select at least one option for content, genre, and time frame.")
        else:
            st.subheader("Top Books Based on Your Selections:")
            
            # Combine user selections into queries
            queries = [f"{c} {g} {e}" for c in selected_content for g in selected_genre for e in selected_era]
            
            books = []
            for query in queries:
                results = search_books(query, limit=5)
                for book in results:
                    olid = book.get("key", "").split("/")[-1]
                    title = book.get("title", "Unknown Title")
                    author_key = book.get("author_key", [None])[0]
                    author_name = book.get("author_name", ["Unknown Author"])[0]
                    cover_id = book.get("cover_i")
                    publish_year = book.get("first_publish_year", "Unknown Year")
                    
                    # Fetch additional details if available
                    book_details = fetch_book_details(olid)
                    description = book_details.get("description", "No description available.") if book_details else "No description available."
                    
                    # Fetch author details if available
                    if author_key:
                        author_details = fetch_author_details(author_key)
                        author_name = author_details.get("name", author_name) if author_details else author_name
                    
                    books.append({
                        "title": title,
                        "author": author_name,
                        "publish_year": publish_year,
                        "description": description,
                        "cover_id": cover_id
                    })

            # Display fetched books
            if books:
                st.write(f"Total books fetched: **{len(books)}**")
                for book in books:
                    st.subheader(book['title'])
                    st.write(f"**Author:** {book['author']}")
                    st.write(f"**Publish Year:** {book['publish_year']}")
                    st.write(f"**Description:** {book['description']}")
                    if book['cover_id']:
                        st.image(f"{COVER_URL}{book['cover_id']}-M.jpg", caption=book['title'])
                    st.write("---")
            else:
                st.write("No books found for your selections.")

if __name__ == "__main__":
    main()
