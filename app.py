import pickle
import streamlit as st
import requests
import time
import requests.exceptions  # Import the exceptions module

API_KEY = "e81d85bc60e0d32c1f1982c204d2ef2a"  # replace with your TMDB API key


# ✅ Cached fetch with smarter error handling
@st.cache_data
def fetch_poster(movie_id, retries=3, delay=2):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            # This will raise a specific HTTPError for bad responses (like 404 Not Found, 429 Too Many Requests)
            response.raise_for_status()
            data = response.json()
            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                # Movie exists but has no poster
                st.warning(f"Movie ID {movie_id} found, but it has no poster.")
                return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.HTTPError as e:
            # This handles server errors specifically.
            if e.response.status_code == 404:
                st.error(f"Movie with ID {movie_id} not found on TMDB. (Incorrect ID in your data file)")
            else:
                st.error(f"HTTP error for movie_id {movie_id}: {e}")
            # This is a permanent error for this ID, so we stop retrying.
            return "https://via.placeholder.com/500x750?text=Bad+ID"

        except requests.exceptions.RequestException as e:
            # This handles network-level errors (e.g., timeout, no connection)
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                st.warning(f"Network error for movie_id {movie_id} after retries. Please check your connection.")
                return "https://via.placeholder.com/500x750?text=Network+Error"

    # Fallback in case the loop finishes unexpectedly
    return "https://via.placeholder.com/500x750?text=Failed"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = int(movies.iloc[i[0]].movie_id)
        recommended_movie_posters.append(fetch_poster(movie_id))
        recommended_movie_names.append(movies.iloc[i[0]].title)
    return recommended_movie_names, recommended_movie_posters


# Streamlit UI
st.header('🎬 Movie Recommender System')
movies = pickle.load(open('movies_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))
movie_list = movies['title'].values
selected_movie = st.selectbox("Type or select a movie from the dropdown", movie_list)

if st.button('Show Recommendation', type="primary"):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.text(recommended_movie_names[i])
            st.image(recommended_movie_posters[i])