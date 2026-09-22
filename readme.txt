README - Projet Fouille de donnees (M2 SID, 2026-2027)
=========================================================

Structure du code :
  src\scraping\      -> collecte des donnees (IMDb, Rotten Tomatoes, TMDB)
  src\cleaning\      -> nettoyage, normalisation et fusion des 3 sources
  src\eda\           -> analyse exploratoire (stats, correlations, ACP)
  src\visualization\ -> visualisations (heatmap, ACP...)
  notebooks\demo.ipynb -> demonstration bout-en-bout du pipeline

Comment executer le projet :
  1. pip install -r requirements.txt
  2. Lancer les scripts de src\scraping dans l'ordre : imdb, rotten_tomatoes, tmdb
  3. Lancer les scripts de src\cleaning dans l'ordre : clean_*, puis merge_datasets.py
  4. Lancer les scripts de src\eda et src\visualization sur le jeu de donnees fusionne
  5. Ouvrir notebooks\demo.ipynb pour la demonstration complete

Fonctionnalites de chaque partie : voir l'en-tete de commentaire en haut de chaque fichier .py
