import pandas as pd

# Read the data from the text file into a DataFrame
movies_df = pd.read_csv("sample_movies.txt", sep="|", header=None, names=["movie_genre", "movie_id", "movie_name"])
rating_df = pd.read_csv("sample_ratings.txt", sep="|", header=None, names=["movie_name", "rating", "user_id"])

# Display the DataFrames
print(movies_df.head())
print(rating_df.head())

menu_options = """
Select an option:
1. Import movies dataset
2. Import ratings dataset
3. Show top N movies (overall)
4. Show top N movies by genre
5. Show your most preferred genre
6. Show 3 most popular movies from your favorite genre
7. Exit program
"""

