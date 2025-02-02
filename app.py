import streamlit as st
import requests

# Open Library API base URL
BASE_URL = "https://openlibrary.org"
COVER_URL = "https://covers.openlibrary.org/b/id/"

# Expanded literature topics
literature_topics = [
    "poetry", "drama", "prose", "epic", "satire", "fable", "gothic", "fantasy", "mythology", "romance", 
    "horror", "mystery", "science fiction", "historical", "graphic novels", "dystopian", "short stories", 
    "autobiography", "biography", "memoir", "travel", "philosophy", "psychology", "self-help", "spirituality", 
    "classic", "contemporary", "war", "adventure", "crime", "detective", "thriller", "western", "comedy", 
    "children's literature", "young adult", "fairy tales", "legends", "folklore", "literary criticism", 
    "philosophical fiction", "experimental", "absurdist", "postmodern", "cyberpunk", "steampunk", "urban fantasy", 
    "weird fiction", "utopian", "magical realism", "epistolary", "bildungsroman", "chivalric romance", "feminist literature", 
    "noir", "psychological thriller", "supernatural", "transgressive fiction", "realism", "naturalism", "modernist", 
    "postcolonial", "existentialist", "metafiction", "picaresque", "tragicomedy", "literary nonfiction", "hard science fiction", 
    "soft science fiction", "military fiction", "political fiction", "climate fiction", "domestic fiction", "regional literature", 
    "Afrofuturism", "eco-fiction", "protest literature", "philosophical essays", "travel writing", "cultural studies", 
    "religious studies", "mythopoeia", "hagiography", "menippean satire", "lyrical prose", "proletarian literature", "war poetry"
]

genre_options = [
    "fiction", "non-fiction", "mystery", "romance", "fantasy", "biography", "adventure", "horror", "thriller", 
    "science fiction", "historical", "drama", "philosophy", "self-help", "psychology", "spirituality", "dystopian", 
    "young adult", "children", "graphic novels"
]

# Function to search books using Open Library Search API
def search_books(query, limit=20):
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
        selected_topic = st.selectbox("Select Literature Topic:", literature_topics)
        selected_genre = st.selectbox("Select Genre:", genre_options)
        st.write("Press the button below to get recommendations.")
        if st.button("Get Recommendations"):
            st.session_state.recommend = True
    
    if "recommend" in st.session_state:
        st.subheader("Top 20 Books Based on Your Selections:")
        query = f"{selected_topic} {selected_genre}"
        books = search_books(query, limit=20)

        if books:
            for book in books:
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
