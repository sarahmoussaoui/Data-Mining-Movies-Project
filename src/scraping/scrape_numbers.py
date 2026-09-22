import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Setting the urls for scraping
BASE_URL = "https://www.the-numbers.com"
URL = BASE_URL + "/box-office-records/worldwide/all-movies/cumulative/released-in-2026"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

# Requesting the page and checking the status code
response = requests.get(URL, headers=HEADERS, timeout=15)
print("Status code :", response.status_code)
response.raise_for_status() 

soup = BeautifulSoup(response.text, "html.parser")

# Retrieving the table containg the box office numbers
table = soup.find("table")

# Retrieving the rows of the table
movies = []
for row in table.find_all("tr"):
    cells = row.find_all("td")

    # we use 6 to verify that its a valid movie row --> headers are ignored because they use <th> instead of <td> so they are skipped
    if len(cells) < 6:
        continue

    # The title is not always complete (there's ".."), the url keeps the full title
    link = cells[1].find("a")

    movies.append({
        "rank": cells[0].get_text(strip=True), # strip=True removes the linebreaks at the beginning and end of the string
        "title": cells[1].get_text(strip=True),
        "worldwide_box_office": cells[2].get_text(strip=True),
        "domestic_box_office": cells[3].get_text(strip=True),
        "international_box_office": cells[4].get_text(strip=True),
        "domestic_share": cells[5].get_text(strip=True),
        "url": urljoin(BASE_URL, link["href"]) if link else None,
    })

# Build the DataFrame
df = pd.DataFrame(movies)

print(df.shape)    # checking the number of rows and columns
print(df.head(10))

# Saving to csv file
# utf-8-sig is used because there's foreign movie titles
df.to_csv("data/raw/numbers/the_numbers_worldwide_2026.csv", index=False, encoding="utf-8-sig")
print("Saved to data/raw/numbers/the_numbers_worldwide_2026.csv")