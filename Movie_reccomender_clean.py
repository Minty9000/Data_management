import pandas as pd
import os

# Read the data from the text file into a DataFrame
movies_df = None
rating_df = None


# --- CENTRALIZED INPUT CLEANING FUNCTION ---
def clean_input(text):
    """
    Cleans user input by stripping leading/trailing whitespace.
    This ensures consistency for string comparisons and file paths.
    """
    return str(text).strip()


# -----------------------------------------------

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
    """
    Displays the main menu and handles user interaction.
    """
    while True:
        print(menu_options)

        # 🧹 CLEANED: Using clean_input to handle accidental spaces (e.g., '1 ')
        choice = clean_input(input("Enter your choice (1-8): "))

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


# Function to load, save, and display movies dataset
def load_movies():
    """
    Loads or creates a movies dataset.
    """
    global movies_df
    # 🧹 CLEANED: Using clean_input and then .lower()
    choice = clean_input(input("Load from file (F) or enter new data (N)? ")).lower()

    # --- OPTION 1: Load from file ---
    if choice == "f":
        while True:
            # 🧹 CLEANED: Using clean_input
            file_path = clean_input(input("Enter path to movies dataset: "))

            # Automatically add .txt if missing
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            # Only allow .txt files
            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            # Try reading file
            try:
                movies_df = pd.read_csv(file_path, sep="|", header=None,
                                        names=["movie_genre", "movie_id", "movie_name"])
                print("\n✅ Movies dataset loaded successfully.")
                print(movies_df.head(), "\n")
                break
            except FileNotFoundError:
                print("❌ File not found. Try again.\n")
            except Exception as e:
                print(f"⚠️ Error reading file: {e}\nPlease make sure it's a valid .txt file with '|' separators.\n")

    # --- OPTION 2: Enter new data manually ---
    elif choice == "n":
        movies_df = pd.DataFrame(columns=["movie_genre", "movie_id", "movie_name"])
        print("Enter movie data (type 'done' to finish):\n")
        while True:
            movie_name = input("Movie name (or 'done' to stop): ")
            if movie_name.lower() == "done":
                break
            movie_genre = input("Genre: ")
            movie_id = input("Movie ID: ")
            movies_df.loc[len(movies_df)] = [movie_genre, movie_id, movie_name]

        # Save file safely
        while True:
            # 🧹 CLEANED: Using clean_input
            file_path = clean_input(input("Enter filename to save: "))
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            # Only allow .txt files
            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            # Check if file already exists
            if os.path.exists(file_path):
                # 🧹 CLEANED: Using clean_input for overwrite prompt
                overwrite = clean_input(input(f"⚠️ File '{file_path}' already exists. Overwrite? (Y/N): ")).lower()
                if overwrite != "y":
                    print("Please choose a different filename.")
                    continue

            # Save the file
            movies_df.to_csv(file_path, sep="|", index=False, header=False)
            print(f"\n✅ Movies data successfully saved to '{file_path}'.")
            print(movies_df, "\n")
            break

    # --- INVALID OPTION ---
    else:
        print("Invalid choice. Please enter 'F' or 'N'.")


# Function to load, save, and display ratings dataset
def load_ratings():
    """
    Loads or creates a ratings dataset.
    """
    global rating_df
    # 🧹 CLEANED: Using clean_input and then .lower()
    choice = clean_input(input("Load from file (F) or enter new data (N)? ")).lower()

    # --- OPTION 1: Load from file ---
    if choice == "f":
        while True:
            # 🧹 CLEANED: Using clean_input
            file_path = clean_input(input("Enter path to ratings dataset: "))
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            try:
                rating_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_name", "rating", "user_id"])

                # Data Cleaning for ratings
                rating_df["rating"] = pd.to_numeric(rating_df["rating"], errors="coerce")
                rating_df.dropna(subset=["rating"], inplace=True)
                rating_df = rating_df[(rating_df["rating"] >= 0) & (rating_df["rating"] <= 5)]

                print("\n✅ Ratings dataset loaded successfully.")
                print(rating_df.head(), "\n")
                break

            except FileNotFoundError:
                print("❌ File not found. Try again.\n")
            except Exception as e:
                print(f"⚠️ Error reading file: {e}\nPlease make sure it's a valid .txt file with '|' separators.\n")

    # --- OPTION 2: Enter new data manually ---
    elif choice == "n":
        rating_df = pd.DataFrame(columns=["movie_name", "rating", "user_id"])
        print("Enter rating data (type 'done' to finish):\n")

        while True:
            movie_name = input("Movie name (or 'done' to stop): ")
            if movie_name.lower() == "done":
                break
            rating = input("Rating (0–5): ")
            user_id = input("User ID: ")
            rating_df.loc[len(rating_df)] = [movie_name, rating, user_id]

        # Data Cleaning for ratings
        rating_df["rating"] = pd.to_numeric(rating_df["rating"], errors="coerce")
        rating_df.dropna(subset=["rating"], inplace=True)
        rating_df = rating_df[(rating_df["rating"] >= 0) & (rating_df["rating"] <= 5)]

        while True:
            # 🧹 CLEANED: Using clean_input
            file_path = clean_input(input("Enter filename to save: "))
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            if os.path.exists(file_path):
                # 🧹 CLEANED: Using clean_input for overwrite prompt
                overwrite = clean_input(input(f"⚠️ File '{file_path}' already exists. Overwrite? (Y/N): ")).lower()
                if overwrite != "y":
                    print("Please choose a different filename.\n")
                    continue

            rating_df.to_csv(file_path, sep="|", index=False, header=False)
            print(f"\n✅ Ratings data successfully saved to '{file_path}'.")
            print(rating_df, "\n")
            break

    # --- INVALID OPTION ---
    else:
        print("Invalid choice. Please enter 'F' or 'N'.")


# Function to show top N movies overall
def top_n_movies():
    """
    Displays the top N movies with the highest average ratings.
    """
    global rating_df

    if rating_df is None:
        print("Error: Please load the ratings dataset first (option 2).")
        return

    try:
        # NOTE: No .strip() needed, but for full robustness,
        # it would ideally use a numeric validation function.
        n = int(input("Enter N: "))
    except ValueError:
        print("Invalid number. Please enter a numeric value.")
        return

    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)

    # FIX: Drop NaN values (movies with no valid ratings)
    avg_ratings = avg_ratings.dropna()

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Name", "Average Rating"]

    print(f"\nTop {n} Movies:")
    print(avg_ratings_df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format}), "\n")


# Function to show top N movies by genre
def top_n_movies_genre():
    """
    Displays the top N movies within a given genre based on average ratings.
    """
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    # 🧹 CLEANED: Using clean_input and then .lower()
    genre = clean_input(input("Enter genre: ")).lower()

    try:
        # NOTE: No .strip() needed.
        n = int(input("Enter N: "))
    except ValueError:
        print("Invalid number. Please enter a numeric value.")
        return

    genre_movies = movies_df[movies_df["movie_genre"].str.lower() == genre]

    if genre_movies.empty:
        print(f"No movies found for genre '{genre}'.\n")
        return

    merged = rating_df.merge(genre_movies, on="movie_name", how="right")
    avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)

    # FIX: Drop NaN values (movies with no valid ratings)
    avg_ratings = avg_ratings.dropna()

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Name", "Average Rating"]

    print(f"\nTop {n} {genre} Movies:")
    print(avg_ratings_df.to_string(index=False, formatters={"Average Rating": "{:.2f}".format}), "\n")


# Function to show top N genres
def top_n_genre():
    """
    Displays the top N genres based on average movie ratings.
    """
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    try:
        # NOTE: No .strip() needed.
        n = int(input("Enter N: "))
    except ValueError:
        print("Invalid number. Please enter a numeric value.")
        return

    merged = rating_df.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False).head(n)

    # FIX: Drop NaN values (genres with no valid ratings)
    avg_ratings = avg_ratings.dropna()

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Genre", "Average Rating"]

    print(f"\nTop {n} Genres:")
    print(avg_ratings_df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format}), "\n")


# Function to show the user's most preferred genre
def preferred_genre(user_id=None):
    """
    Displays the user's most preferred genre based on their average ratings.
    """
    global movies_df, rating_df

    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    if user_id is None:
        try:
            # NOTE: No .strip() needed.
            user_id = int(input("Enter your user ID: "))
        except ValueError:
            print("Invalid user ID. Please enter a numeric value.\n")
            return

    user_ratings = rating_df[rating_df["user_id"] == user_id]
    merged = user_ratings.merge(movies_df, on="movie_name", how="inner")

    if merged.empty:
        print("No ratings found for this user.\n")
        return None

    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False)

    # FIX: Drop NaN values (user has no valid ratings for a genre)
    avg_ratings = avg_ratings.dropna()

    if avg_ratings.empty:
        print("No valid genre preferences found for this user.\n")
        return None

    top_score = avg_ratings.iloc[0]
    top_genres = avg_ratings[avg_ratings == top_score].index.tolist()
    print(f"\nYour most preferred genre(s): {', '.join(top_genres)}\n")

    return top_genres


# Function to show top 3 movies from the user's favorite genre
def top_3_movies_fav_genre():
    """
    Displays the top 3 movies from the user's most preferred genre.
    """
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    try:
        # NOTE: No .strip() needed.
        user_id = int(input("Enter your user ID: "))
    except ValueError:
        print("Invalid user ID. Must be a number.")
        return

    fav_genre = preferred_genre(user_id)  # calls previous function
    if not fav_genre:
        return

    for genre in fav_genre:
        genre_movies = movies_df[movies_df["movie_genre"] == genre]
        merged = rating_df.merge(genre_movies, on="movie_name", how="inner")

        # Only include movies that this user actually rated
        merged = merged[merged["user_id"] == user_id]

        if merged.empty:
            print(f"No {genre} movies rated by user {user_id}.")
            return

        avg_ratings = (
            merged.groupby("movie_name")["rating"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )

        # FIX: Drop NaN values (movies in this genre user didn't rate validly)
        avg_ratings = avg_ratings.dropna()

        avg_ratings_df = avg_ratings.reset_index()
        avg_ratings_df.columns = ["Movie Name", "Average Rating"]
        print(f"\nTop 3 {genre} Movies for User {user_id}:")
        print(
            avg_ratings_df.to_string(
                index=False,
                justify="left",
                formatters={"Average Rating": "{:.2f}".format},
            ),
            "\n",
        )


if __name__ == "__main__":
    # Run the menu
    main_menu()
