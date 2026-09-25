import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import os

# Years to scrape
YEARS = [2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]

# Setting the base URL
BASE_URL = "https://www.the-numbers.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}


# Defining a function to get the title from the movie URL page
def get_title_from_movie_page(movie_url):
    try:
        response = requests.get(movie_url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        movie_soup = BeautifulSoup(response.text, "html.parser")
        h1 = movie_soup.find("h1")

        return h1.get_text(strip=True) if h1 else None

    except requests.RequestException as e:
        print("   Error:", e)
        return None


# Create output directory
os.makedirs("data/raw/numbers", exist_ok=True)

# Variable that will be used to concatenate all movies into one final dataframe
all_movies = []

# Scrape each year
for year in YEARS:

    print(f"\n{'='*50}")
    print(f"Scraping year {year}")
    print(f"{'='*50}")

    # URL changes only according to the year
    URL = BASE_URL + f"/box-office-records/worldwide/all-movies/cumulative/released-in-{year}"

    # Requesting the page
    response = requests.get(URL, headers=HEADERS, timeout=15)

    print("Status code :", response.status_code)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Retrieving the table containing the box office numbers
    table = soup.find("table")

    if table is None:
        print(f"No table found for {year}. Skipping...")
        continue

    # Retrieving the rows of the table
    movies = []

    for row in table.find_all("tr"):
        cells = row.find_all("td")

        # Headers are ignored because they use <th>
        # we use 6 to verify that its a valid movie row --> headers are ignored because they use <th> instead of <td> so they are skipped
        if len(cells) < 6:
            continue

        # The title is not always complete ("..")
        # The URL keeps the full title
        link = cells[1].find("a")

        movies.append({
            "rank": cells[0].get_text(strip=True),
            "title": cells[1].get_text(strip=True),
            "worldwide_box_office": cells[2].get_text(strip=True),
            "domestic_box_office": cells[3].get_text(strip=True),
            "international_box_office": cells[4].get_text(strip=True),
            "domestic_share": cells[5].get_text(strip=True),
            "url": urljoin(BASE_URL, link["href"]) if link else None,
        })

    print(f"{len(movies)} movies found for {year}")

    # Visiting each movie page to retrieve the full title
    for i, movie in enumerate(movies, start=1):

        print(f"[{i}/{len(movies)}] {movie['url']}")

        if movie["url"]:
            movie["title_url"] = get_title_from_movie_page(movie["url"])
        else:
            movie["title_url"] = None

        # Waiting between requests
        time.sleep(1.5)

    # Build DataFrame
    df = pd.DataFrame(movies)

    print("DataFrame shape:", df.shape)
    print(df.head(10))

    # Save one CSV per year
    output_file = f"data/raw/numbers/the_numbers_worldwide_{year}.csv"

    df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    all_movies.extend(movies)

    print(f"Saved to {output_file}")

# DataFrame containing all years
all_years_df = pd.DataFrame(all_movies)

print("\nAll years DataFrame:")
print(all_years_df.shape)
print(all_years_df.head())

# Save all years in one CSV
all_years_file = "data/raw/numbers/the_numbers_worldwide_all_years.csv"

all_years_df.to_csv(
    all_years_file,
    index=False,
    encoding="utf-8-sig"
)

print(f"Saved to {all_years_file}")