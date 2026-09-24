import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

# minimum de votes pour qu'un film soit considere comme ayant une existence reelle
# (evite de recuperer des milliers de films inconnus jamais suivis par le public)
MIN_VOTE_COUNT = 20


def get_movies_page(year, page, min_vote_count=MIN_VOTE_COUNT):
    """Recupere une page de resultats pour les films sortis une annee donnee,
    en ne gardant que ceux ayant un minimum de votes (filtre de pertinence)."""
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "primary_release_year": year,
        "sort_by": "popularity.desc",
        "vote_count.gte": min_vote_count,
        "page": page,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def build_tmdb_dataset(year=2026, max_pages=None):
    """Recupere tous les films d'une annee donnee ayant au moins MIN_VOTE_COUNT votes."""
    first_page = get_movies_page(year, 1)
    total_pages = min(first_page["total_pages"], 500)  # limite dure de l'API TMDB
    if max_pages:
        total_pages = min(total_pages, max_pages)

    print(f"Total apres filtre (vote_count >= {MIN_VOTE_COUNT}) : {first_page['total_results']} films sur {total_pages} pages")

    rows = []
    for page in range(1, total_pages + 1):
        data = first_page if page == 1 else get_movies_page(year, page)
        for movie in data["results"]:
            rows.append({
                "tmdb_id": movie.get("id"),
                "title": movie.get("title"),
                "original_title": movie.get("original_title"),
                "popularity": movie.get("popularity"),
                "vote_average": movie.get("vote_average"),
                "vote_count": movie.get("vote_count"),
                "release_date": movie.get("release_date"),
                "original_language": movie.get("original_language"),
                "genre_ids": movie.get("genre_ids"),
                "adult": movie.get("adult"),
            })

        if page % 20 == 0:
            print(f"Page {page}/{total_pages} traitee...")
        time.sleep(0.05)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df_tmdb = build_tmdb_dataset(year=2026)

    os.makedirs("data/raw/tmdb", exist_ok=True)
    df_tmdb.to_csv("data/raw/tmdb/tmdb_raw.csv", index=False)

    print(f"{len(df_tmdb)} films sauvegardes dans data/raw/tmdb/tmdb_raw.csv")