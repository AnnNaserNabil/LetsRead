import streamlit as st
import requests

# Open Library API base URL
BASE_URL = "https://openlibrary.org"

# Function to fetch books by subject (topic, genre, or era)
def fetch_books_by_subject(subject, limit=50):
    url = f"{BASE_URL}/subjects/{subject}.json?limit={limit}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

# Streamlit app
def main():
    st.title("Book Recommendation App")
    st.write("Discover books based on your preferences!")

    # Dropdown menus for user inputs
    content_options = ["science", "history", "technology", "philosophy", "art", "literature"]
    genre_options = ["fiction", "non-fiction", "mystery", "romance", "fantasy", "biography"]
    era_options = ["19th century", "20th century", "21st century", "classic", "modern"]

    selected_content = st.selectbox("Select a content topic:", content_options)
    selected_genre = st.selectbox("Select a genre:", genre_options)
    selected_era = st.selectbox("Select an era:", era_options)

    if st.button("Get Recommendations"):
        st.subheader(f"Top 50 Books Based on Your Selections:")

        # Combine user selections into a query
        query = f"{selected_content} {selected_genre} {selected_era}"
        st.write(f"Fetching books related to: **{query}**")

        # Fetch books based on the combined query
        book_data = fetch_books_by_subject(query.lower().replace(" ", "_"))
        if book_data and 'works' in book_data:
            for i, work in enumerate(book_data['works'][:50], 1):  # Display top 50 books
                st.write(f"**{i}. Title:** {work.get('title', 'N/A')}")
                st.write(f"**Author:** {work.get('authors', [{}])[0].get('name', 'N/A')}")
                st.write(f"**Description:** {work.get('description', 'No description available.')}")
                st.write("---")
        else:
            st.write("No books found for your selections.")

if __name__ == "__main__":
    main()
