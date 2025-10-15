import pandas as pd
import os


# --- NEW INPUT CLEANING FUNCTION ---
def clean_input(text):
    """
    Cleans user input by stripping leading/trailing whitespace.
    It ensures consistency for string comparisons (e.g., ' F ' becomes 'F').
    """
    return str(text).strip()


# -----------------------------------


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
    """
    Displays the main menu and handles user interaction.

    Continuously prompts the user to select an option from the menu.
    Each option calls a corresponding function until the user chooses to exit.
    """
    while True:
        print(menu_options)

        # NOTE: choice is kept as raw input because it's validated numerically (1-8)
        # and doesn't need string cleaning beyond the existing validation logic.
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


# Function to load, save, and display movies dataset
def load_movies():
    """
    Loads or creates a movies dataset.

    Options:
        - Load from a .txt file (pipe-separated)
        - Enter new data manually and save to a file

    The dataset contains columns: ['movie_genre', 'movie_id', 'movie_name'].
    """
    global movies_df
    # 🧹 CLEANED INPUT
    choice = clean_input(input("Load from file (F) or enter new data (N)? ")).lower()

    # --- OPTION 1: Load from file ---
    if choice == "f":
        while True:
            # 🧹 CLEANED INPUT
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
            # We don't clean these inputs yet, as they are going into the DataFrame as raw data.
            # You might want to clean them later, but the primary security/parsing risk is on file paths/options.
            movie_name = input("Movie name (or 'done' to stop): ")
            if movie_name.lower() == "done":
                break
            movie_genre = input("Genre: ")
            movie_id = input("Movie ID: ")
            movies_df.loc[len(movies_df)] = [movie_genre, movie_id, movie_name]

        # Save file safely
        while True:
            file_path = clean_input(input("Enter filename to save: "))
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            # Only allow .txt files
            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            # Check if file already exists
            if os.path.exists(file_path):
                overwrite = input(f"⚠️ File '{file_path}' already exists. Overwrite? (Y/N): ").strip().lower()
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

    Options:
        - Load from a .txt file (pipe-separated)
        - Enter new data manually and save to a file

    The dataset contains columns: ['movie_name', 'rating', 'user_id'].
    Ratings are validated to be numeric and between 0 and 5.
    """
    global rating_df
    # 🧹 CLEANED INPUT
    choice = clean_input(input("Load from file (F) or enter new data (N)? ")).lower()

    # --- OPTION 1: Load from file ---
    if choice == "f":
        while True:
            # 🧹 CLEANED INPUT
            file_path = clean_input(input("Enter path to ratings dataset: "))
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            try:
                rating_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_name", "rating", "user_id"])

                # 🧠 Convert rating to numeric
                rating_df["rating"] = pd.to_numeric(rating_df["rating"], errors="coerce")

                # 🧠 Drop invalid or missing ratings
                rating_df.dropna(subset=["rating"], inplace=True)

                # 🧠 Ensure valid numeric range (optional but good)
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

        # 🧠 Convert and clean ratings here too
        rating_df["rating"] = pd.to_numeric(rating_df["rating"], errors="coerce")
        rating_df.dropna(subset=["rating"], inplace=True)
        rating_df = rating_df[(rating_df["rating"] >= 0) & (rating_df["rating"] <= 5)]

        while True:
            file_path = clean_input(input("Enter filename to save: "))
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            if os.path.exists(file_path):
                overwrite = input(f"⚠️ File '{file_path}' already exists. Overwrite? (Y/N): ").strip().lower()
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

    Prompts the user to enter N and prints the movies sorted by their
    average rating in descending order.
    """
    global rating_df

    if rating_df is None:
        print("Error: Please load the ratings dataset first (option 2).")
        return

    try:
        # User input for N is numeric, so clean_input is not strictly necessary,
        # but a simple .strip() is still good practice.
        n = int(input("Enter N: ").strip())
    except ValueError:
        print("Invalid number. Please enter a numeric value.")
        return
    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Name", "Average Rating"]

    print(f"\nTop {n} Movies:")
    print(avg_ratings_df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format}), "\n")


# Function to show top N movies by genre
def top_n_movies_genre():
    """
    Displays the top N movies within a given genre based on average ratings.

    Requires both the movies and ratings datasets to be loaded.
    """
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    # 🧹 CLEANED INPUT
    genre = clean_input(input("Enter genre: ")).lower()

    try:
        n = int(input("Enter N: ").strip())
    except ValueError:
        print("Invalid number. Please enter a numeric value.")
        return

    genre_movies = movies_df[movies_df["movie_genre"].str.lower() == genre]

    if genre_movies.empty:
        print(f"No movies found for genre '{genre}'.\n")
        return

    merged = rating_df.merge(genre_movies, on="movie_name", how="right")
    avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Name", "Average Rating"]

    print(f"\nTop {n} {genre} Movies:")
    print(avg_ratings_df.to_string(index=False, formatters={"Average Rating": "{:.2f}".format}), "\n")


# Function to show top N genres
def top_n_genre():
    """
    Displays the top N genres based on average movie ratings.

    Requires both the movies and ratings datasets to be loaded.
    """
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    try:
        n = int(input("Enter N: ").strip())
    except ValueError:
        print("Invalid number. Please enter a numeric value.")
        return

    merged = rating_df.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False).head(n)

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Genre", "Average Rating"]

    print(f"\nTop {n} Genres:")
    print(avg_ratings_df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format}), "\n")


# Function to show the user's most preferred genre
def preferred_genre(user_id=None):
    """
    Displays the user's most preferred genre based on their average ratings.

    Args:
        user_id (int, optional): User ID to calculate preferences for.
                                    If None, the user is prompted to enter one.

    Returns:
        str | list | None: The user's top genre(s), or None if no data is found.
    """
    global movies_df, rating_df

    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    if user_id is None:
        try:
            # Input for user_id is numeric, so .strip() is sufficient here
            user_id = int(input("Enter your user ID: ").strip())
        except ValueError:
            print("Invalid user ID. Please enter a numeric value.\n")
            return

    user_ratings = rating_df[rating_df["user_id"] == user_id]
    merged = user_ratings.merge(movies_df, on="movie_name", how="inner")

    if merged.empty:
        print("No ratings found for this user.\n")
        return None

    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False)

    top_score = avg_ratings.iloc[0]
    top_genres = avg_ratings[avg_ratings == top_score].index.tolist()
    print(f"\nYour most preferred genre(s): {', '.join(top_genres)}\n")

    return top_genres


# Function to show top 3 movies from the user's favorite genre
def top_3_movies_fav_genre():
    """
    Displays the top 3 movies from the user's most preferred genre.

    Uses the user's ratings and preferred genre to identify their top-rated
    movies within that genre.
    """
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return
    # 🔢 Keep user_id numeric for consistency
    try:
        # Input for user_id is numeric, so .strip() is sufficient here
        user_id = int(input("Enter your user ID: ").strip())
    except ValueError:
        print("Invalid user ID. Must be a number.")
        return
    fav_genre = preferred_genre(user_id)  # calls previous function
    if not fav_genre:
        return

    for genre in fav_genre:
        genre_movies = movies_df[movies_df["movie_genre"] == genre]
        merged = rating_df.merge(genre_movies, on="movie_name", how="inner")

        # ✅ Only include movies that this user actually rated
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
