<!-- @format -->

# Movie Data Integration and Exploratory Analysis

## Overview

This project focuses on collecting, cleaning, integrating, and analyzing movie data from three different sources:

- **TMDB (The Movie Database):** movie metadata, popularity, ratings, vote counts, genres, original languages, and other movie attributes.
- **The Numbers:** domestic and worldwide box-office revenues.
- **Rotten Tomatoes:** critics' and audience ratings.

The main objective is to combine these heterogeneous datasets into an integrated dataset that can be used to explore relationships between movie characteristics, box-office performance, and audience and critics' evaluations.

The project covers the complete data preparation workflow, from web scraping and data cleaning to record matching, dataset integration, and exploratory data analysis.

## Project Objectives

The main objectives are:

- Collect movie data from multiple sources.
- Clean and standardize the collected datasets.
- Analyze the similarities between movie titles across sources.
- Identify matching records and integrate the datasets.
- Preserve source-specific information and ensure data traceability.
- Explore movie characteristics, box-office revenues, and ratings through statistical analysis and visualizations.

## Data Sources

| Source          | Description                       | Main Purpose                                                    |
| --------------- | --------------------------------- | --------------------------------------------------------------- |
| TMDB            | Movie metadata and user ratings   | Analyze movie characteristics, popularity, and audience ratings |
| The Numbers     | Movie box-office data             | Study domestic and worldwide box-office performance             |
| Rotten Tomatoes | Critics' and audience evaluations | Compare critics' opinions with audience ratings                 |

The raw data collected from these sources is stored separately from the cleaned datasets and the intermediate and final integration results.

## Repository Structure

```text
.
├── data/
│   ├── raw/
│   │   ├── numbers/
│   │   ├── rotten_tomatoes/
│   │   └── tmdb/
│   ├── processed/
│   │   ├── tmdb_clean.csv
│   │   ├── the_numbers_worldwide_cleaned.csv
│   │   └── rotten_tomatoes_cleaned.csv
│   └── merged/
│       ├── similarities/
│       ├── score_100/
│       ├── df_for_analysis.csv
│       └── master_dataset.csv
│
├── src/
│   ├── scraping/
│   │   ├── scrape_numbers.py
│   │   ├── scrape_rotten_tomatoes.py
│   │   └── scrape_tmdb.py
│   │
│   ├── cleaning/
│   │   ├── clean_numbers.ipynb
│   │   ├── clean_rotten_tomatoes.ipynb
│   │   └── clean_tmdb.ipynb
│   │
│   ├── merging/
│   │   ├── merge_analysis.ipynb
│   │   ├── merge_datasets_pairwise.py
│   │   ├── merge_master_data.ipynb
│   │   ├── clean_master.ipynb
│   │   └── view_merged_columns.ipynb
│   │
│   └── eda/
        ├── plots/
│       ├── descriptive/
│       │   ├── numbers.ipynb
│       │   ├── rotten.ipynb
│       │   └── tmdb.ipynb
│       ├── box_office_tmdb_numbers.ipynb
│       ├── critics_vs_audience_tmdb_rotten_Analysis.ipynb
│       ├── characterics-film.ipynb
├── Project description/
├── video/
├── README.md
├── requirements.txt
└── .gitignore
```

## HOW TO RUN CODE

### Prerequisites

Before running the project, make sure you have:

- **Visual Studio Code (VS Code)** installed.
- **Python** installed.
- All required Python libraries installed using the `requirements.txt` file.

To run the code, you can open the `.py` or `.ipynb` files in VS Code and click the **Run** button in the top-left corner.

To better understand the overall project workflow, I recommend executing the files in the following order:

1. **`src/scraping`**: First, run all the scraping scripts. Note that the Rotten Tomatoes scraping script must be executed last because it retrieves movie information based on the data collected from TMDB. The generated CSV files should be saved in `data/raw`.

2. **`src/cleaning`**: Clean the collected datasets. The generated CSV files should be saved in `data/processed`.

3. **`src/merging`**: Merge the datasets from the different sources. The generated CSV files should be saved in `data/merged`.

4. **`src/eda`**: Perform exploratory data analysis and generate visualizations using the merged datasets.
