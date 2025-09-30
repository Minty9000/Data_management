import pandas as pd

# Read the data from the text file into a DataFrame
movies_df = pd.read_csv("sample_movies.txt", sep="|", header=None, names=["movie_genre", "movie_id", "movie_name"])
rating_df = pd.read_csv("sample_ratings.txt", sep="|", header=None, names=["movie_name", "rating", "user_id"])

# Display the DataFrames
print(movies_df.head())
print(rating_df.head())

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
    # Takes arguments
    pass

# Function to load and display ratings dataset
def load_ratings():
    # Takes arguments
    pass

# Function to show top N movies overall
def top_n_movies():
    # Arguments: n - number of top movies to display
    pass

# Function to show top N movies by genre
def top_n_movies_genre():
    # Arguments: n - number of top movies to display, genre - genre to filter by
    pass

# Function to show top N genres
def top_n_genre():
    # Arguments: n - number of top genres to display
    pass

# Function to show the user's most preferred genre
def preferred_genre():
    # Arguments: user_id - ID of the user
    pass

# Function to show top 3 movies from the user's favorite genre
def top_3_movies_fav_genre():
    # Arguments: user_id - ID of the user
    # Calls preferred_genre() to get the user's favorite genre
    # Then calls top_n_movies_genre() with n=3 to get the top 3 movies in that genre
    pass



# Run the menu
main_menu()
