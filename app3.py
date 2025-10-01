import pickle
import streamlit as st
import requests
import time

API_KEY = "e81d85bc60e0d32c1f1982c204d2ef2a"  # replace with your TMDB API key


# Cached fetch to avoid repeated API calls
@st.cache_data
def fetch_poster(movie_id, retries=3, delay=1):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            poster_path = data.get("poster_path")
            if poster_path:
                return "https://image.tmdb.org/t/p/w500/" + poster_path
            else:
                st.warning(f"Could not find a poster for movie_id {movie_id}. Showing placeholder.")
                return "https://via.placeholder.com/500x750?text=No+Image"

        except requests.exceptions.RequestException:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
            else:
                st.warning(f"⚠️ Poster is not available for movie id {movie_id} ")
                return "https://via.placeholder.com/500x750?text=Error"


def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        # Ensure movie_id is an integer before passing it to the fetch function
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