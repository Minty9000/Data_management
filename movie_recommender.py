import pandas as pd

# Read the data from the text file into a DataFrame
movies_df = pd.read_csv("sample_movies.txt", sep="|", header=None, names=["movie_genre", "movie_id", "movie_name"])
rating_df = pd.read_csv("sample_ratings.txt", sep="|", header=None, names=["movie_name", "rating", "user_id"])

# Display the DataFrames
print(movies_df.head())
print(rating_df.head())

