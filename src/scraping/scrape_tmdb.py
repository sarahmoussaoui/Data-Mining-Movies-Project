"""
Recuperation des donnees TMDB via l'API (popularite, budget, revenus...).
"""
import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Charge la clé API depuis le fichier .env
load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def get_movie_by_title(title):
    """Cherche un film sur TMDB par son titre et retourne ses infos principales."""
    search_url = f"{BASE_URL}/search/movie"
    params = {"api_key": API_KEY, "query": title}
    response = requests.get(search_url, params=params)
    response.raise_for_status()
    results = response.json().get("results")
    return results[0] if results else None


def build_tmdb_dataset(titles):
    """Interroge TMDB pour chaque titre et construit un DataFrame des résultats."""
    rows = []
    not_found = []

    for title in titles:
        movie = get_movie_by_title(title)
        if movie:
            rows.append({
                "title_queried": title,
                "tmdb_title": movie.get("title"),
                "tmdb_id": movie.get("id"),
                "popularity": movie.get("popularity"),
                "vote_average": movie.get("vote_average"),
                "vote_count": movie.get("vote_count"),
                "release_date": movie.get("release_date"),
                "original_language": movie.get("original_language"),
                "adult": movie.get("adult"),
            })
        else:
            not_found.append(title)

        time.sleep(0.05)  # petite pause pour ne pas dépasser la limite de requêtes

    if not_found:
        print(f"[ATTENTION] {len(not_found)} films non trouvés sur TMDB : {not_found}")

    return pd.DataFrame(rows)


if __name__ == "__main__":
    # Charge les titres depuis le fichier de Sarah
    df_numbers = pd.read_csv("data/raw/numbers/the_numbers_worldwide_2026.csv")
    titles = df_numbers["title"].tolist()

    print(f"Recherche de {len(titles)} films sur TMDB...")
    df_tmdb = build_tmdb_dataset(titles)

    # Sauvegarde le résultat pour ne pas refaire tous les appels API à chaque fois
    os.makedirs("data/raw/tmdb", exist_ok=True)
    df_tmdb.to_csv("data/raw/tmdb/tmdb_raw.csv", index=False)

    print(f"[OK] {len(df_tmdb)} films récupérés, sauvegardés dans data/raw/tmdb/tmdb_raw.csv")
    print(df_tmdb.head())