import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


def get_movies_page(year, page):
    """Recupere une page de resultats pour les films sortis une annee donnee (sans filtre)."""
    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": API_KEY,
        "primary_release_year": year,
        "sort_by": "popularity.desc",
        "page": page,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


def scrape_year(year):
    """Recupere tous les films d'une annee donnee (jusqu'a 500 pages / 10000 films max)."""
    first_page = get_movies_page(year, 1)
    total_pages = min(first_page["total_pages"], 500)

    print(f"\n=== Annee {year} : {first_page['total_results']} films trouves, {total_pages} pages a recuperer ===")

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

        if page % 50 == 0:
            print(f"  Page {page}/{total_pages} traitee...")
        time.sleep(0.05)

    return pd.DataFrame(rows)


if __name__ == "__main__":
    os.makedirs("data/raw/tmdb", exist_ok=True)
    output_path = "data/raw/tmdb/tmdb_raw_2019_2026.csv"

    # reprise : on charge ce qui existe deja, et on identifie les annees deja faites
    if os.path.exists(output_path):
        df_existing = pd.read_csv(output_path)
        annees_deja_faites = set(pd.to_datetime(df_existing["release_date"], errors="coerce").dt.year.dropna().astype(int))
        print(f"Reprise : annees deja scrapees = {sorted(annees_deja_faites)}")
    else:
        df_existing = pd.DataFrame()
        annees_deja_faites = set()

    all_years_df = [df_existing] if not df_existing.empty else []

    for year in range(2019, 2027):
        if year in annees_deja_faites:
            print(f"\n=== Annee {year} deja scrapee, on saute ===")
            continue

        df_year = scrape_year(year)
        all_years_df.append(df_year)

        df_so_far = pd.concat(all_years_df, ignore_index=True)
        df_so_far.to_csv(output_path, index=False)
        print(f"  -> Sauvegarde intermediaire : {len(df_so_far)} films au total jusqu'ici")

    print(f"\nTERMINE : {len(df_so_far)} films sauvegardes dans {output_path}")