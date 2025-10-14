import pandas as pd
import os

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


# Function to load, save, and display movies dataset
def load_movies():
    global movies_df
    choice = input("Load from file (F) or enter new data (N)? ").strip().lower()
    
    # --- OPTION 1: Load from file ---
    if choice == "f":
        while True:
            file_path = input("Enter path to movies dataset: ").strip()
            # Automatically add .txt if missing
            if not os.path.splitext(file_path)[1]:
                file_path += ".txt"

            # Only allow .txt files
            if not file_path.lower().endswith(".txt"):
                print("⚠️ Only .txt files are supported. Please try again.\n")
                continue

            # Try reading file
            try:
                movies_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_genre", "movie_id", "movie_name"])
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
            file_path = input("Enter filename to save: ").strip()
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
    global rating_df
    choice = input("Load from file (F) or enter new data (N)? ").strip().lower()
    
    # --- OPTION 1: Load from file ---
    if choice == "f":
        while True:
            file_path = input("Enter path to ratings dataset: ").strip()
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
            file_path = input("Enter filename to save: ").strip()
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
    global rating_df

    if rating_df is None:
        print("Error: Please load the ratings dataset first (option 2).")
        return

    n = int(input("Enter N: "))
    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Name", "Average Rating"]

    print(f"\nTop {n} Movies:")
    print(avg_ratings_df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format}), "\n")

# Function to show top N movies by genre
def top_n_movies_genre():

    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return
    
    genre = input("Enter genre: ").strip().lower()
    n = int(input("Enter N: "))
    genre_movies = movies_df[movies_df["movie_genre"].str.lower() == genre]

    if genre_movies.empty:
        print(f"No movies found for genre '{genre}'.\n")
        return
    
    merged = rating_df.merge(genre_movies, on="movie_name")
    avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Name", "Average Rating"]
    
    print(f"\nTop {n} {genre} Movies:")
    print(avg_ratings_df.to_string(index=False, formatters={"Average Rating": "{:.2f}".format}), "\n")

# Function to show top N genres
def top_n_genre():

    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return
    
    n = int(input("Enter N: "))
    merged = rating_df.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False).head(n)

    avg_ratings_df = avg_ratings.reset_index()
    avg_ratings_df.columns = ["Movie Genre", "Average Rating"]
    
    print(f"\nTop {n} Genres:")
    print(avg_ratings_df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format}), "\n")

# Function to show the user's most preferred genre
def preferred_genre(user_id=None):
    global movies_df, rating_df  # ensure access to global data

    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return

    if user_id is None:
        user_id = input("Enter your user ID: ").strip()

    try:
        user_id = int(user_id)
    except ValueError:
        print("Invalid user ID. Please enter a numeric value.\n")
        return

    user_ratings = rating_df[rating_df["user_id"] == user_id]
    merged = user_ratings.merge(movies_df, on="movie_name", how="inner")

    if merged.empty:
        print("No ratings found for this user.\n")
        return None

    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False)

    if avg_ratings.empty:
        print("No ratings found for this user.\n")
        return None

    top_score = avg_ratings.iloc[0]
    top_genres = avg_ratings[avg_ratings == top_score].index.tolist()
    print(f"\nYour most preferred genre(s): {', '.join(top_genres)}\n")

    return top_genres[0] if len(top_genres) == 1 else top_genres

# Function to show top 3 movies from the user's favorite genre
def top_3_movies_fav_genre():
    if movies_df is None or rating_df is None:
        print("Error: Please load both movies and ratings datasets first.")
        return
    # 🔢 Keep user_id numeric for consistency
    try:
        user_id = int(input("Enter your user ID: ").strip())
    except ValueError:
        print("Invalid user ID. Must be a number.")
        return
    fav_genre = preferred_genre(user_id)  # calls previous function
    if fav_genre:
        genre_movies = movies_df[movies_df["movie_genre"] == fav_genre]
        merged = rating_df.merge(genre_movies, on="movie_name", how="inner")

        # ✅ Only include movies that this user actually rated
        merged = merged[merged["user_id"] == user_id]

        if merged.empty:
            print(f"No {fav_genre} movies rated by user {user_id}.")
            return
        avg_ratings = (
            merged.groupby("movie_name")["rating"]
            .mean()
            .sort_values(ascending=False)
            .head(3)
        )
        avg_ratings_df = avg_ratings.reset_index()
        avg_ratings_df.columns = ["Movie Name", "Average Rating"]
        print(f"\nTop 3 {fav_genre} Movies for User {user_id}:")
        print(
            avg_ratings_df.to_string(
                index=False,
                justify="left",
                formatters={"Average Rating": "{:.2f}".format},
            ),
            "\n",
        )

# Run the menu
main_menu()
