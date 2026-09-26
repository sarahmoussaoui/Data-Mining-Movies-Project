"""
Scraping des notes critiques/public sur Rotten Tomatoes.
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
import os

df = pd.DataFrame(columns=["Title", "Summary","Director","Producer","Distributor","Genre","Original Language","Release Date(Streaming)","Runtime"])
html_file = requests.get("https://www.rottentomatoes.com/browse/movies_at_home?page=5").text

soup = BeautifulSoup(html_file,'lxml')
list_of_films_hrefs = soup.find_all("a",class_="js-tile-link")

# string get stored as "\nproducer\n" so I created this function to remove \n result is "producer" instead of "\nproducer\n"
def remove_newlines(text):
    return text.replace("\n", "")

def get_text(soup, tag, attrs):
    element = soup.find(tag, attrs=attrs)
    if element is None:
        return ""
    
    return element.get_text(strip=True)

films = []
c=0
for film in list(list_of_films_hrefs):
    href = film["href"]
    
    html_film_details = requests.get(f"https://www.rottentomatoes.com{href}").text
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
    details["title"] = title
    details["summary"] = summary
    details["critics score"] = critics_score
    details["critics reviews"] = critics_reviews
    details["audience score"] = audience_score
    details["audience reviews"] = audience_reviews
    # some of details of films are dynamic so I made this loop to get all childs of details wrapper
    for detail in list(film_details):
        title = detail.find("dt",class_="key").get_text()
        
        value = detail.find("dd",attrs={"data-qa":"item-value-group"}).get_text()
        title = remove_newlines(title)
        value = remove_newlines(value)
        details[title] = value

    
    #films.append(details)
    df = pd.concat([df, pd.DataFrame([details])],ignore_index=True)   
    df.to_csv("data/raw/rotten_tomatoes/rotten_tomatoes_raw.csv", index=False, encoding="utf-8-sig")

   
    
        




os.makedirs("data/raw/rotten_tomatoes", exist_ok=True)
# Saving to csv file
# utf-8-sig is used because there's foreign movie titles
df.to_csv("data/raw/rotten_tomatoes/rotten_tomatoes_raw.csv", index=False, encoding="utf-8-sig")
print("Saved to data/raw/numbers/rotten_tomatoes_raw.csv")
