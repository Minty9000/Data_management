import pandas as pd

# Read the data from the text file into a DataFrame
movies_df = None
rating_df = None

# Define the menu options
menu_options = """\n
Select an option:
1. Import movies dataset
2. Import ratings dataset
3. Show top N movies (overall)
4. Show top N movies in a genre
5. Show top N genres
6. Show your most preferred genre
7. Show 3 most popular movies from your favorite genre
8. Exit program
"""


# Function to display the menu and handle user input
def main_menu():
    while True:
        print(menu_options)

        choice = input("Enter your choice (1-8): ")

        if choice == "1":
            print("Loading movies dataset...")
            load_movies()

        elif choice == "2":
            print("Loading ratings dataset...")
            load_ratings()

        elif choice == "3":
            print("Showing top N movies...")
            top_n_movies()

        elif choice == "4":
            print("Showing top N movies in a genre...")
            top_n_movies_genre()

        elif choice == "5":
            print("Showing top N genre...")
            top_n_genre()

        elif choice == "6":
            print("Showing your most preferred genre...")
            preferred_genre()

        elif choice == "7":
            print("Showing top 3 movies from your favorite genre...")
            top_3_movies_fav_genre()

        elif choice == "8":
            print("Exiting program. Goodbye!")
            break

        else:
            print("Invalid choice, please try again.")


# Function to load and display movies dataset
def load_movies():
    global movies_df
    file_path = input("Enter path to movies dataset: ")
    try:
        movies_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_genre", "movie_id", "movie_name"])
        print("\nMovies dataset loaded successfully.")
        print(movies_df.head(), "\n")
    except FileNotFoundError:
        print("❌ File not found. Try again.\n")

def load_ratings():
    global rating_df
    file_path = input("Enter path to ratings dataset: ")
    try:
        rating_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_name", "rating", "user_id"])
        print("\nRatings dataset loaded successfully.")
        print(rating_df.head(), "\n")
    except FileNotFoundError:
        print("❌ File not found. Try again.\n")

# Function to show top N movies overall
def top_n_movies():
    n = int(input("Enter N: "))
    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    print(f"\nTop {n} Movies (Overall):")
    print(avg_ratings, "\n")

# Function to show top N movies by genre
def top_n_movies_genre():
    genre = input("Enter genre: ")
    n = int(input("Enter N: "))
    genre_movies = movies_df[movies_df["movie_genre"] == genre]
    merged = rating_df.merge(genre_movies, on="movie_name")
    avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    print(f"\nTop {n} {genre} Movies:")
    print(avg_ratings, "\n")

# Function to show top N genres
def top_n_genre():
    n = int(input("Enter N: "))
    merged = rating_df.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False).head(n)
    print(f"\nTop {n} Genres:")
    print(avg_ratings, "\n")

# Function to show the user's most preferred genre
def preferred_genre():
    user_id = input("Enter your user ID: ")
    user_ratings = rating_df[rating_df["user_id"] == int(user_id)]
    merged = user_ratings.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False)
    if avg_ratings.empty:
        print("No ratings found for this user.\n")
        return None
    fav_genre = avg_ratings.index[0]
    print(f"\nYour most preferred genre is: {fav_genre}\n")
    return fav_genre

# Function to show top 3 movies from the user's favorite genre
def top_3_movies_fav_genre():
    user_id = input("Enter your user ID: ")
    fav_genre = preferred_genre()  # calls previous function
    if fav_genre:
        genre_movies = movies_df[movies_df["movie_genre"] == fav_genre]
        merged = rating_df.merge(genre_movies, on="movie_name")
        avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(3)
        print(f"\nTop 3 {fav_genre} Movies for User {user_id}:")
        print(avg_ratings, "\n")



# Run the menu
main_menu()
