import pandas as pd
import re
import unicodedata
import os

from rapidfuzz import process
from rapidfuzz.distance import Levenshtein
from IPython.display import display


# ============================================================
# 1. Read datasets
# ============================================================

tmdb_df = pd.read_csv(
    "data/processed/tmdb_clean.csv"
)

numbers_df = pd.read_csv(
    "data/processed/the_numbers_worldwide_2026_cleaned.csv"
)

rotten_df = pd.read_csv(
    "data/processed/rotten_tomatoes_cleaned.csv",
    dtype={"aspect_ratio": "string"},
    low_memory=False
)


# ============================================================
# 2. Normalize titles
# ============================================================

def normalize_title(title):

    title = str(title).lower()

    # Remove accents
    title = unicodedata.normalize('NFKD', title)

    title = ''.join(
        c for c in title
        if not unicodedata.combining(c)
    )

    # Remove punctuation, numbers and non-ASCII characters
    title = re.sub(r'[^a-z\s]', '', title)

    # Remove extra spaces
    title = re.sub(r'\s+', ' ', title).strip()

    return title


tmdb_df['title_normalized'] = (
    tmdb_df['title'].apply(normalize_title)
)

numbers_df['title_normalized'] = (
    numbers_df['title'].apply(normalize_title)
)

rotten_df['title_normalized'] = (
    rotten_df['title'].apply(normalize_title)
)


# ============================================================
# 3. Rename year columns
# ============================================================

tmdb_df = tmdb_df.rename(
    columns={'release_year': 'year'}
)

rotten_df = rotten_df.rename(
    columns={'release_date_theaters_year': 'year'}
)



# ============================================================
# 4. Make year columns consistent
# ============================================================

tmdb_df['year'] = pd.to_numeric(
    tmdb_df['year'],
    errors='coerce'
)

numbers_df['year'] = pd.to_numeric(
    numbers_df['year'],
    errors='coerce'
)

rotten_df['year'] = pd.to_numeric(
    rotten_df['year'],
    errors='coerce'
)


# ============================================================
# 5. Create output folders
# ============================================================

os.makedirs(
    "data/merged/score_100",
    exist_ok=True
)

os.makedirs(
    "data/merged/similarities",
    exist_ok=True
)


# ============================================================
# 6. Generic pairwise fuzzy matching function
# ============================================================

def fuzzy_match(
    df1,
    df2,
    name1,
    name2
):

    matches = []

    for _, row1 in df1.iterrows():

        title1 = row1['title_normalized']
        year1 = row1['year']

        # Keep only movies from the same year
        df2_same_year = df2[
            df2['year'] == year1
        ]

        if df2_same_year.empty:
            continue

        titles2 = (
            df2_same_year['title_normalized'].tolist()
        )

        # Find best fuzzy match
        match = process.extractOne(
            title1,
            titles2,
            scorer=Levenshtein.normalized_similarity
        )

        if match is None:
            continue

        # Retrieve corresponding row
        row2 = df2_same_year[
            df2_same_year['title_normalized'] == match[0]
        ].iloc[0]

        similarity = match[1] * 100

        matches.append({

            f'{name1}_index': row1.name,
            f'{name2}_index': row2.name,

            f'{name1}_title': row1['title'],
            f'{name1}_normalized': row1['title_normalized'],
            f'{name1}_year': row1['year'],

            f'{name2}_title': row2['title'],
            f'{name2}_normalized': row2['title_normalized'],
            f'{name2}_year': row2['year'],

            'similarity': similarity
        })

    return pd.DataFrame(matches)


# ============================================================
# 7. TMDB ↔ Numbers
# ============================================================

tmdb_numbers_scores = fuzzy_match(
    tmdb_df,
    numbers_df,
    'tmdb',
    'numbers'
)

tmdb_numbers_scores = (
    tmdb_numbers_scores
    .sort_values(
        'similarity',
        ascending=False
    )
    .reset_index(drop=True)
)

display(tmdb_numbers_scores)

print(
    "TMDB ↔ Numbers:",
    len(tmdb_numbers_scores),
    "candidate matches"
)

print(
    "TMDB ↔ Numbers 100%:",
    (
        tmdb_numbers_scores['similarity'] == 100
    ).sum()
)


# ============================================================
# 8. TMDB ↔ Rotten Tomatoes
# ============================================================

tmdb_rotten_scores = fuzzy_match(
    tmdb_df,
    rotten_df,
    'tmdb',
    'rotten'
)

tmdb_rotten_scores = (
    tmdb_rotten_scores
    .sort_values(
        'similarity',
        ascending=False
    )
    .reset_index(drop=True)
)

display(tmdb_rotten_scores)

print(
    "TMDB ↔ Rotten:",
    len(tmdb_rotten_scores),
    "candidate matches"
)

print(
    "TMDB ↔ Rotten 100%:",
    (
        tmdb_rotten_scores['similarity'] == 100
    ).sum()
)


# ============================================================
# 9. Numbers ↔ Rotten Tomatoes
# ============================================================

numbers_rotten_scores = fuzzy_match(
    numbers_df,
    rotten_df,
    'numbers',
    'rotten'
)

numbers_rotten_scores = (
    numbers_rotten_scores
    .sort_values(
        'similarity',
        ascending=False
    )
    .reset_index(drop=True)
)

display(numbers_rotten_scores)

print(
    "Numbers ↔ Rotten:",
    len(numbers_rotten_scores),
    "candidate matches"
)

print(
    "Numbers ↔ Rotten 100%:",
    (
        numbers_rotten_scores['similarity'] == 100
    ).sum()
)


# ============================================================
# 10. Keep only 100% pairwise matches
# ============================================================

tmdb_numbers_100 = (
    tmdb_numbers_scores[
        tmdb_numbers_scores['similarity'] == 100
    ]
    .copy()
)

tmdb_rotten_100 = (
    tmdb_rotten_scores[
        tmdb_rotten_scores['similarity'] == 100
    ]
    .copy()
)

numbers_rotten_100 = (
    numbers_rotten_scores[
        numbers_rotten_scores['similarity'] == 100
    ]
    .copy()
)


# ============================================================
# 11. Build ALL-THREE similarity table
# ============================================================
#
# We start from TMDB ↔ Numbers matches.
#
# Then add the corresponding Rotten match.
#
# This gives us:
#
# TMDB index
# Numbers index
# Rotten index
# TMDB-Numbers similarity
# TMDB-Rotten similarity
# Numbers-Rotten similarity
#
# ============================================================

all_three_scores = (
    tmdb_numbers_scores[
        [
            'tmdb_index',
            'numbers_index',
            'tmdb_title',
            'numbers_title',
            'tmdb_year',
            'similarity'
        ]
    ]
    .rename(
        columns={
            'similarity':
                'similarity_tmdb_numbers'
        }
    )
)


# Add TMDB ↔ Rotten score
all_three_scores = all_three_scores.merge(
    tmdb_rotten_scores[
        [
            'tmdb_index',
            'rotten_index',
            'similarity'
        ]
    ],
    on='tmdb_index',
    how='inner'
)

all_three_scores = all_three_scores.rename(
    columns={
        'similarity':
            'similarity_tmdb_rotten'
    }
)


# Add Numbers ↔ Rotten score
all_three_scores = all_three_scores.merge(
    numbers_rotten_scores[
        [
            'numbers_index',
            'rotten_index',
            'similarity'
        ]
    ],
    on=[
        'numbers_index',
        'rotten_index'
    ],
    how='inner'
)

all_three_scores = all_three_scores.rename(
    columns={
        'similarity':
            'similarity_numbers_rotten'
    }
)


# Sort
all_three_scores = (
    all_three_scores
    .sort_values(
        [
            'similarity_tmdb_numbers',
            'similarity_tmdb_rotten',
            'similarity_numbers_rotten'
        ],
        ascending=False
    )
    .reset_index(drop=True)
)


# Display
display(all_three_scores)


print(
    "All three datasets:",
    len(all_three_scores),
    "candidate matches"
)


# ============================================================
# 12. Keep only ALL-THREE 100% matches
# ============================================================

all_three_100 = all_three_scores[
    (
        all_three_scores[
            'similarity_tmdb_numbers'
        ] == 100
    )
    &
    (
        all_three_scores[
            'similarity_tmdb_rotten'
        ] == 100
    )
    &
    (
        all_three_scores[
            'similarity_numbers_rotten'
        ] == 100
    )
].copy()


print(
    "All three datasets 100%:",
    len(all_three_100)
)

display(all_three_100)


# ============================================================
# 13. Create 100% MERGED datasets
# ============================================================

# ------------------------------------------------------------
# TMDB ↔ Numbers 100%
# ------------------------------------------------------------

tmdb_numbers_100_merged = (
    tmdb_numbers_100

    .merge(
        tmdb_df,
        left_on='tmdb_index',
        right_index=True,
        suffixes=('', '_tmdb')
    )

    .merge(
        numbers_df,
        left_on='numbers_index',
        right_index=True,
        suffixes=('', '_numbers')
    )
)


# ------------------------------------------------------------
# TMDB ↔ Rotten 100%
# ------------------------------------------------------------

tmdb_rotten_100_merged = (
    tmdb_rotten_100

    .merge(
        tmdb_df,
        left_on='tmdb_index',
        right_index=True,
        suffixes=('', '_tmdb')
    )

    .merge(
        rotten_df,
        left_on='rotten_index',
        right_index=True,
        suffixes=('', '_rotten')
    )
)


# ------------------------------------------------------------
# Numbers ↔ Rotten 100%
# ------------------------------------------------------------

numbers_rotten_100_merged = (
    numbers_rotten_100

    .merge(
        numbers_df,
        left_on='numbers_index',
        right_index=True,
        suffixes=('', '_numbers')
    )

    .merge(
        rotten_df,
        left_on='rotten_index',
        right_index=True,
        suffixes=('', '_rotten')
    )
)


# ============================================================
# 14. ALL THREE datasets — only 100%
# ============================================================

all_three_100_merged = (
    all_three_100

    .merge(
        tmdb_df,
        left_on='tmdb_index',
        right_index=True,
        suffixes=('', '_tmdb')
    )

    .merge(
        numbers_df,
        left_on='numbers_index',
        right_index=True,
        suffixes=('', '_numbers')
    )

    .merge(
        rotten_df,
        left_on='rotten_index',
        right_index=True,
        suffixes=('', '_rotten')
    )
)


# ============================================================
# 15. Display final 100% datasets
# ============================================================

print(
    "TMDB ↔ Numbers 100% shape:",
    tmdb_numbers_100_merged.shape
)

print(
    "TMDB ↔ Rotten 100% shape:",
    tmdb_rotten_100_merged.shape
)

print(
    "Numbers ↔ Rotten 100% shape:",
    numbers_rotten_100_merged.shape
)

print(
    "ALL THREE 100% shape:",
    all_three_100_merged.shape
)

# ============================================================
# CLEAN MERGED DATASETS BEFORE SAVING
# ============================================================

columns_to_drop_all_three = [
    "tmdb_index",
    "numbers_index",
    "rotten_index",
    "tmdb_title",
    "numbers_title",
    "title_numbers",
    "title_rotten",
    "tmdb_year",
    "year_numbers",
    "year_rotten",
    "similarity_tmdb_numbers",
    "similarity_tmdb_rotten",
    "similarity_numbers_rotten",
    "title_normalized",
    "title_normalized_numbers",
    "title_normalized_rotten",
    "tmdb_normalized",
    "numbers_normalized",
    "rotten_normalized",
    "url",
    "genre_ids",
    "original_language",
    "box office (gross usa)",
    # rotten either repetitive or empty
    "release_date_streaming",
    "rerelease date (theaters)",
    "release date (streaming)",
    "box office (gross usa)",
    "release date (tv)",
    "release date (dvd)",
    "release_date_theaters_year",
    "release_date_theaters_month",
    "release_date_theaters_day"
]

columns_to_drop_numbers_rotten = [
    "numbers_index",
    "rotten_index",
    "numbers_title",
    "rotten_title",
    "numbers_normalized",
    "rotten_normalized",
    "numbers_year",
    "rotten_year",
    "similarity",
    "title_normalized",
    "title_normalized_rotten",
    "url",
    "box office (gross usa)",
    # rotten either repetitive or empty
    "release_date_streaming",
    "rerelease date (theaters)",
    "release date (streaming)",
    "box office (gross usa)",
    "release date (tv)",
    "release date (dvd)",
    "release_date_theaters_year",
    "release_date_theaters_month",
    "release_date_theaters_day"    
]

columns_to_drop_tmdb_rotten = [
    "tmdb_index",
    "rotten_index",
    "tmdb_title",
    "rotten_title",
    "tmdb_normalized",
    "rotten_normalized",
    "tmdb_year",
    "rotten_year",
    "similarity",
    "title_normalized",
    "title_normalized_rotten",
    "genre_ids",
    "original_language",
    "box office (gross usa)",
# rotten either repetitive or empty
    "release_date_streaming",
    "rerelease date (theaters)",
    "release date (streaming)",
    "box office (gross usa)",
    "release date (tv)",
    "release date (dvd)",
    "release_date_theaters_year",
    "release_date_theaters_month",
    "release_date_theaters_day"
]

columns_to_drop_tmdb_numbers = [
    "tmdb_index",
    "numbers_index",
    "tmdb_title",
    "tmdb_normalized",
    "tmdb_year",
    "numbers_title",
    "numbers_normalized",
    "numbers_year",
    "similarity",
    "title_normalized",
    "title_numbers",
    "year_numbers",
    "url",
    "genre_ids",
    "original_language"
]

tmdb_numbers_100_merged = tmdb_numbers_100_merged.drop(
    columns=columns_to_drop_tmdb_numbers,
    errors="ignore"
)

numbers_rotten_100_merged = numbers_rotten_100_merged.drop(
    columns=columns_to_drop_numbers_rotten,
    errors="ignore"
)

tmdb_rotten_100_merged = tmdb_rotten_100_merged.drop(
    columns=columns_to_drop_tmdb_rotten,
    errors="ignore"
)

all_three_100_merged = all_three_100_merged.drop(
    columns=columns_to_drop_all_three,
    errors="ignore"
)
# ============================================================
# 16. Save 100% MERGED datasets
# ============================================================

tmdb_numbers_100_merged.to_csv(
    "data/merged/score_100/tmdb_numbers_100.csv",
    index=False
)

tmdb_rotten_100_merged.to_csv(
    "data/merged/score_100/tmdb_rotten_100.csv",
    index=False
)

numbers_rotten_100_merged.to_csv(
    "data/merged/score_100/numbers_rotten_100.csv",
    index=False
)

all_three_100_merged.to_csv(
    "data/merged/score_100/all_three_100.csv",
    index=False
)


# ============================================================
# 17. Save ALL SIMILARITY SCORES
# ============================================================

tmdb_numbers_scores.to_csv(
    "data/merged/similarities/tmdb_numbers_scores.csv",
    index=False
)

tmdb_rotten_scores.to_csv(
    "data/merged/similarities/tmdb_rotten_scores.csv",
    index=False
)

numbers_rotten_scores.to_csv(
    "data/merged/similarities/numbers_rotten_scores.csv",
    index=False
)

all_three_scores.to_csv(
    "data/merged/similarities/all_three_scores.csv",
    index=False
)


# ============================================================
# 18. Confirmation
# ============================================================

print("\nFiles saved in data/merged/score_100/:")
print("1. tmdb_numbers_100.csv")
print("2. tmdb_rotten_100.csv")
print("3. numbers_rotten_100.csv")
print("4. all_three_100.csv")

print("\nFiles saved in data/merged/similarities/:")
print("1. tmdb_numbers_scores.csv")
print("2. tmdb_rotten_scores.csv")
print("3. numbers_rotten_scores.csv")
print("4. all_three_scores.csv")