import pandas as pd
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os
import re




df = pd.DataFrame(columns=["Title", "Summary","Director","Producer","Distributor","Genre","Original Language","Release Date(Streaming)","Runtime"])
html_file = requests.get("https://www.rottentomatoes.com/browse/movies_at_home?page=5").text

soup = BeautifulSoup(html_file,'lxml')
list_of_films_hrefs = soup.find_all("a",class_="js-tile-link")

def normalize_string(text):
    text = str(text).lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # remove symbols
    text = re.sub(r'\s+', '_', text)          # spaces → _
    return text
# string get stored as "\nproducer\n" so I created this function to remove \n result is "producer" instead of "\nproducer\n"
def remove_newlines(text):
    return text.replace("\n", "")

def get_text(soup, tag, attrs):
    element = soup.find(tag, attrs=attrs)
    if element is None:
        return ""
    
    return element.get_text(strip=True)

films = []
tmdb_films =  pd.read_csv("data/processed/tmdb_clean.csv")
c=1
for film in tmdb_films["title"]:
    href = normalize_string(film)
    print("href",href)
    
    html_film_details = requests.get(f"https://www.rottentomatoes.com/m/{href}").text
    soup = BeautifulSoup(html_film_details,'lxml')
    


    film_details = soup.find_all("div",class_="category-wrap",attrs={"data-qa":"item"})
    title = get_text(
    soup,
    "rt-text",
    {"slot": "title", "size": "1.25,1.75", "context": "heading"}
     ) 

    summary = get_text(
    soup,
    "rt-text",
    {"data-qa": "synopsis-value"}
    )

    critics_score = get_text(
    soup,
    "rt-text",
    {
    "slot": "critics-score",
    }
      )

    critics_reviews = get_text(
    soup,
    "rt-link",
    {"slot": "critics-reviews"}
     )

    audience_score = get_text(
    soup,
    "rt-text",
    {"slot": "audience-score"}
    )

    audience_reviews = get_text(
    soup,
    "rt-link",
    {"slot": "audience-reviews"}
     )
    details = {}
    details["Title"] = title
    details["Summary"] = summary
    details["Critics score"] = critics_score
    details["Critics reviews"] = critics_reviews
    details["Audience score"] = audience_score
    details["Audience reviews"] = audience_reviews
    # some of details of films are dynamic so I made this loop to get all childs of details wrapper
    for detail in list(film_details):
        title = detail.find("dt",class_="key").get_text()
        
        value = detail.find("dd",attrs={"data-qa":"item-value-group"}).get_text()
        title = remove_newlines(title)
        value = remove_newlines(value)
        details[title] = value

    
    
    df = pd.concat([df, pd.DataFrame([details])],ignore_index=True)
    
    df.to_csv("data/raw/rotten_tomatoes/rotten_tomatoes_raw.csv", index=False, encoding="utf-8-sig")
    
    #c+=1
    #if c==5:
    #   break
    
    



os.makedirs("data/raw/rotten_tomatoes", exist_ok=True)
# Saving to csv file
# utf-8-sig is used because there's foreign movie titles
df.to_csv("data/raw/rotten_tomatoes/rotten_tomatoes_raw.csv", index=False, encoding="utf-8-sig")
print("Saved to data/raw/numbers/rotten_tomatoes_raw.csv")
