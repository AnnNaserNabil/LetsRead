import streamlit as st
import requests

# Open Library API base URL
BASE_URL = "https://openlibrary.org"

# Function to fetch books by subject
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

    # Dropdown menus for user inputs (multiple selections allowed)
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
            st.subheader("Top 50 Books Based on Your Selections:")

            # Combine user selections into queries
            queries = []
            for content in selected_content:
                for genre in selected_genre:
                    for era in selected_era:
                        queries.append(f"{content}_{genre}_{era}".lower().replace(" ", "_"))

            # Initialize progress bar and counter
            progress_bar = st.progress(0)
            total_queries = len(queries)
            books_fetched = 0

            # Fetch and display books for each query
            all_books = []
            for i, query in enumerate(queries):
                st.write(f"Fetching books for: **{query.replace('_', ' ')}**")
                book_data = fetch_books_by_subject(query)
                if book_data and 'works' in book_data:
                    all_books.extend(book_data['works'][:50])  # Add top 50 books for each query

                # Update progress bar
                progress_bar.progress((i + 1) / total_queries)

            # Display all fetched books
            if all_books:
                st.write(f"Total books fetched: **{len(all_books)}**")
                for i, work in enumerate(all_books[:50], 1):  # Display top 50 books overall
                    st.write(f"**{i}. Title:** {work.get('title', 'N/A')}")
                    st.write(f"**Author:** {work.get('authors', [{}])[0].get('name', 'N/A')}")
                    st.write(f"**Description:** {work.get('description', 'No description available.')}")
                    st.write("---")
            else:
                st.write("No books found for your selections.")

if __name__ == "__main__":
    main()
