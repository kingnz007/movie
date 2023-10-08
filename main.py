from pathlib import Path

import pickle
import requests

from fastapi import FastAPI


app = FastAPI()


def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path


BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
similarity = pickle.load(open(BASE_DIR / "algorithm/similarity.pkl", 'rb'))
pickle_movies = pickle.load(open(BASE_DIR / "algorithm/movie_list.pkl", 'rb'))


def recommend_movies(movie):
    try:
        index = pickle_movies[pickle_movies['title'] == movie].index[0]
    except IndexError:
        return False, ""
    distances = sorted(
        list(
            enumerate(similarity[index])
        ),
        reverse=True,
        key=lambda x: x[1]
    )

    movies = []
    for i in distances[1:6]:
        movie_id = pickle_movies.iloc[i[0]].movie_id
        movie = {
            "title": pickle_movies.iloc[i[0]].title,
            "poster": fetch_poster(movie_id)
        }
        movies.append(movie)
    return True, movies


@app.get("/")
def read_root(movie):
    status, movies = recommend_movies(movie)
    if status:
        return {"movies": movies}
    return {"error": "Movie not found in the database"}
