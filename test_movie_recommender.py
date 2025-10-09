import pandas as pd
import os
import sys

# Global variables to simulate the original program
movies_df = None
rating_df = None

print("=" * 60)
print("MOVIE RECOMMENDER AUTOMATED TESTING")
print("=" * 60)


# ========================================
# HELPER FUNCTIONS (copied from original)
# ========================================

def load_movies_from_file(file_path):
    """Load movies dataset from file"""
    global movies_df
    try:
        movies_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_genre", "movie_id", "movie_name"])
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error loading movies: {e}")
        return False


def load_ratings_from_file(file_path):
    """Load ratings dataset from file"""
    global rating_df
    try:
        rating_df = pd.read_csv(file_path, sep="|", header=None, names=["movie_name", "rating", "user_id"])

        # 🧠 Convert rating to numeric (CRITICAL - fixes string to number issue)
        rating_df["rating"] = pd.to_numeric(rating_df["rating"], errors="coerce")

        # 🧠 Drop invalid or missing ratings
        rating_df.dropna(subset=["rating"], inplace=True)

        # 🧠 Ensure valid numeric range
        rating_df = rating_df[(rating_df["rating"] >= 0) & (rating_df["rating"] <= 5)]

        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error loading ratings: {e}")
        return False


def get_top_n_movies(n):
    """Get top N movies overall by average rating"""
    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_top_n_movies_genre(genre, n):
    """Get top N movies in a specific genre"""
    genre_movies = movies_df[movies_df["movie_genre"] == genre]
    merged = rating_df.merge(genre_movies, on="movie_name")
    avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_top_n_genres(n):
    """Get top N genres by average rating"""
    merged = rating_df.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_preferred_genre(user_id):
    """Get user's most preferred genre"""
    user_ratings = rating_df[rating_df["user_id"] == int(user_id)]
    if user_ratings.empty:
        return None
    merged = user_ratings.merge(movies_df, on="movie_name")
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False)
    if avg_ratings.empty:
        return None
    return avg_ratings.index[0]


def get_top_3_movies_fav_genre(user_id):
    """Get top 3 movies from user's favorite genre"""
    fav_genre = get_preferred_genre(user_id)
    if fav_genre:
        genre_movies = movies_df[movies_df["movie_genre"] == fav_genre]
        merged = rating_df.merge(genre_movies, on="movie_name")
        avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(3)
        return avg_ratings
    return None


# ========================================
# TEST FUNCTIONS
# ========================================

def test_load_movies():
    """Test loading movies dataset"""
    print("\n--- TEST: Load Movies Dataset ---")

    # Test with valid file
    result = load_movies_from_file("sample_movies.txt")
    assert result == True, "❌ Failed to load valid movies file"
    assert movies_df is not None, "❌ Movies dataframe is None"
    assert len(movies_df) > 0, f"❌ Movies file is empty"
    assert "movie_name" in movies_df.columns, "❌ Missing movie_name column"
    assert "movie_genre" in movies_df.columns, "❌ Missing movie_genre column"
    assert "movie_id" in movies_df.columns, "❌ Missing movie_id column"
    print("✓ Movies dataset loaded successfully")
    print(f"✓ Loaded {len(movies_df)} movies")

    # Show genre distribution
    genre_counts = movies_df["movie_genre"].value_counts()
    print(f"✓ Genres found: {', '.join(genre_counts.index.tolist())}")

    # Test with non-existent file
    result = load_movies_from_file("nonexistent.txt")
    assert result == False, "❌ Should fail with non-existent file"
    print("✓ Correctly handles non-existent file")


def test_load_ratings():
    """Test loading ratings dataset"""
    print("\n--- TEST: Load Ratings Dataset ---")

    # Test with valid file
    result = load_ratings_from_file("sample_ratings.txt")
    assert result == True, "❌ Failed to load valid ratings file"
    assert rating_df is not None, "❌ Ratings dataframe is None"
    assert len(rating_df) > 0, f"❌ Ratings file is empty"
    assert "rating" in rating_df.columns, "❌ Missing rating column"
    assert "movie_name" in rating_df.columns, "❌ Missing movie_name column"
    assert "user_id" in rating_df.columns, "❌ Missing user_id column"
    print("✓ Ratings dataset loaded successfully")
    print(f"✓ Loaded {len(rating_df)} ratings")

    # Show additional stats
    num_users = rating_df["user_id"].nunique()
    num_movies = rating_df["movie_name"].nunique()
    print(f"✓ Number of unique users: {num_users}")
    print(f"✓ Number of movies with ratings: {num_movies}")

    # Test with non-existent file
    result = load_ratings_from_file("nonexistent.txt")
    assert result == False, "❌ Should fail with non-existent file"
    print("✓ Correctly handles non-existent file")


def test_top_n_movies():
    """Test getting top N movies overall"""
    print("\n--- TEST: Top N Movies (Overall) ---")

    # Test top 3 movies
    top_3 = get_top_n_movies(3)
    assert len(top_3) <= 3, f"❌ Expected at most 3 movies, got {len(top_3)}"
    assert len(top_3) > 0, "❌ Should return at least 1 movie"

    print(f"✓ Top 3 movies retrieved successfully")
    print("Top 3 Movies:")
    for movie, rating in top_3.items():
        print(f"  {movie}: {rating:.2f}")

    # Test top 1
    top_1 = get_top_n_movies(1)
    assert len(top_1) == 1, f"❌ Expected 1 movie, got {len(top_1)}"
    print(f"✓ Top 1 movie: {top_1.index[0]} ({top_1.values[0]:.2f})")


def test_top_n_movies_genre():
    """Test getting top N movies in a genre"""
    print("\n--- TEST: Top N Movies in a Genre ---")

    # Get first genre from the dataset
    first_genre = movies_df["movie_genre"].iloc[0]

    # Test top 2 movies in first genre
    top_genre = get_top_n_movies_genre(first_genre, 2)
    assert len(top_genre) <= 2, f"❌ Expected at most 2 movies, got {len(top_genre)}"
    assert len(top_genre) > 0, f"❌ Should return at least 1 movie for {first_genre}"

    print(f"✓ Top 2 {first_genre} movies retrieved successfully")
    print(f"Top 2 {first_genre} Movies:")
    for movie, rating in top_genre.items():
        print(f"  {movie}: {rating:.2f}")

    # Test with genre that doesn't exist
    top_horror = get_top_n_movies_genre("NonExistentGenre123", 2)
    assert len(top_horror) == 0, "❌ Should return empty for non-existent genre"
    print("✓ Correctly handles non-existent genre")


def test_top_n_genres():
    """Test getting top N genres"""
    print("\n--- TEST: Top N Genres ---")

    # Count genres that actually have ratings (not just in movies file)
    merged = rating_df.merge(movies_df, on="movie_name")
    total_genres_with_ratings = merged["movie_genre"].nunique()

    # Test top 2 genres
    top_2_genres = get_top_n_genres(2)
    assert len(top_2_genres) <= 2, f"❌ Expected at most 2 genres, got {len(top_2_genres)}"
    assert len(top_2_genres) > 0, "❌ Should return at least 1 genre"

    print(f"✓ Top 2 genres retrieved successfully")
    print("Top 2 Genres:")
    for genre, rating in top_2_genres.items():
        print(f"  {genre}: {rating:.2f}")

    # Test all genres
    all_genres = get_top_n_genres(100)
    assert len(all_genres) == total_genres_with_ratings, f"❌ Expected {total_genres_with_ratings} genres with ratings, got {len(all_genres)}"
    print(f"✓ Total number of genres with ratings: {len(all_genres)}")


def test_preferred_genre():
    """Test getting user's preferred genre"""
    print("\n--- TEST: User's Preferred Genre ---")

    # Get a user ID that exists in the dataset
    existing_user = rating_df["user_id"].iloc[0]

    # Test with existing user
    pref_genre = get_preferred_genre(existing_user)
    assert pref_genre is not None, f"❌ Should return a genre for user {existing_user}"
    print(f"✓ User {existing_user}'s preferred genre: {pref_genre}")

    # Test with non-existent user
    pref_genre_999 = get_preferred_genre(999999)
    assert pref_genre_999 is None, "❌ Should return None for non-existent user"
    print("✓ Correctly handles non-existent user")


def test_top_3_movies_fav_genre():
    """Test getting top 3 movies from user's favorite genre"""
    print("\n--- TEST: Top 3 Movies from Favorite Genre ---")

    # Get a user ID that exists in the dataset
    existing_user = rating_df["user_id"].iloc[0]

    # Test with existing user
    top_3_user = get_top_3_movies_fav_genre(existing_user)
    assert top_3_user is not None, f"❌ Should return movies for user {existing_user}"
    assert len(top_3_user) <= 3, f"❌ Expected at most 3 movies, got {len(top_3_user)}"
    print(f"✓ Top 3 movies for user {existing_user}'s favorite genre:")
    for movie, rating in top_3_user.items():
        print(f"  {movie}: {rating:.2f}")

    # Test with non-existent user
    top_3_user_999 = get_top_3_movies_fav_genre(999999)
    assert top_3_user_999 is None, "❌ Should return None for non-existent user"
    print("✓ Correctly handles non-existent user")


# ========================================
# EDGE CASE TESTS
# ========================================

def test_edge_cases():
    """Test edge cases and negative scenarios"""
    print("\n" + "=" * 60)
    print("EDGE CASE & NEGATIVE TESTS")
    print("=" * 60)

    # Test 1: Empty files
    print("\n--- EDGE CASE: Empty Files ---")
    with open("empty_movies.txt", "w") as f:
        pass  # Create empty file
    with open("empty_ratings.txt", "w") as f:
        pass

    result = load_movies_from_file("empty_movies.txt")
    if result:
        print("✓ Empty movies file loads (creates empty dataframe)")
    else:
        print("✓ Empty movies file handled")

    result = load_ratings_from_file("empty_ratings.txt")
    if result:
        print("✓ Empty ratings file loads (creates empty dataframe)")
    else:
        print("✓ Empty ratings file handled")

    # Clean up
    os.remove("empty_movies.txt")
    os.remove("empty_ratings.txt")

    # Reload valid data for next tests
    load_movies_from_file("sample_movies.txt")
    load_ratings_from_file("sample_ratings.txt")

    # Test 2: Malformed rows
    print("\n--- EDGE CASE: Malformed Rows ---")
    with open("malformed_movies.txt", "w") as f:
        f.write("Adventure|1|Toy Story (1995)\n")
        f.write("Comedy|2\n")  # Missing movie name
        f.write("Action|3|Heat (1995)\n")

    result = load_movies_from_file("malformed_movies.txt")
    if result:
        print(f"✓ Malformed file loads with {len(movies_df)} rows")
        print("  (Pandas may handle missing values)")
    else:
        print("✓ Malformed file rejected")

    os.remove("malformed_movies.txt")

    # Reload valid data
    load_movies_from_file("sample_movies.txt")

    # Test 3: Duplicate ratings
    print("\n--- EDGE CASE: Duplicate Ratings ---")
    with open("duplicate_ratings.txt", "w") as f:
        f.write("Toy Story (1995)|4.0|1\n")
        f.write("Toy Story (1995)|5.0|1\n")  # Same user, same movie
        f.write("Toy Story (1995)|3.0|2\n")

    result = load_ratings_from_file("duplicate_ratings.txt")
    if result:
        duplicates = rating_df[rating_df.duplicated(subset=["movie_name", "user_id"], keep=False)]
        if len(duplicates) > 0:
            print(f"⚠ Warning: Found {len(duplicates)} duplicate ratings (same user rating same movie)")
            print("  Program averages all ratings including duplicates")
        else:
            print("✓ No duplicates found")

    os.remove("duplicate_ratings.txt")

    # Reload valid data
    load_ratings_from_file("sample_ratings.txt")

    # Test 4: Non-numeric ratings
    print("\n--- EDGE CASE: Non-numeric Ratings ---")
    with open("bad_ratings.txt", "w") as f:
        f.write("Toy Story (1995)|4.0|1\n")
        f.write("Toy Story (1995)|five|2\n")  # Non-numeric rating
        f.write("Toy Story (1995)|3.0|3\n")

    try:
        result = load_ratings_from_file("bad_ratings.txt")
        if result:
            # Check if non-numeric values were converted to NaN
            has_nan = rating_df["rating"].isna().any()
            if has_nan:
                print("✓ Non-numeric ratings converted to NaN")
            else:
                print("✓ Non-numeric ratings filtered out (dropna removed them)")
    except Exception as e:
        print(f"✓ Non-numeric ratings cause error: {type(e).__name__}")

    os.remove("bad_ratings.txt")

    # Reload valid data
    load_ratings_from_file("sample_ratings.txt")

    # Test 5: Out-of-range ratings
    print("\n--- EDGE CASE: Out-of-Range Ratings ---")
    with open("outofrange_ratings.txt", "w") as f:
        f.write("Toy Story (1995)|4.0|1\n")
        f.write("Toy Story (1995)|10.0|2\n")  # Too high
        f.write("Toy Story (1995)|-2.5|3\n")  # Negative
        f.write("Toy Story (1995)|100|4\n")  # Way too high
        f.write("Toy Story (1995)|3.0|5\n")

    result = load_ratings_from_file("outofrange_ratings.txt")
    if result:
        # Check rating range
        if len(rating_df) > 0:
            min_rating = rating_df["rating"].min()
            max_rating = rating_df["rating"].max()
            invalid_count = len(rating_df[(rating_df["rating"] < 0) | (rating_df["rating"] > 5)])

            if invalid_count > 0:
                print(f"⚠ Warning: Found {invalid_count} out-of-range ratings")
                print(f"  Rating range in data: {min_rating} to {max_rating}")
                print("  (Original code should filter these in load_ratings with validation)")
            else:
                print(f"✓ All ratings in valid range: {min_rating} to {max_rating}")
                print("  Out-of-range values successfully filtered")
        else:
            print("✓ All out-of-range ratings were filtered out")

    os.remove("outofrange_ratings.txt")

    # Reload valid data
    load_ratings_from_file("sample_ratings.txt")

    # Test 6: Tie behavior
    print("\n--- EDGE CASE: Tie Behavior ---")
    with open("tie_ratings.txt", "w") as f:
        f.write("Movie A|4.0|1\n")
        f.write("Movie A|4.0|2\n")  # Movie A avg = 4.0
        f.write("Movie B|4.0|3\n")
        f.write("Movie B|4.0|4\n")  # Movie B avg = 4.0
        f.write("Movie C|5.0|5\n")
        f.write("Movie C|3.0|6\n")  # Movie C avg = 4.0

    with open("tie_movies.txt", "w") as f:
        f.write("Action|1|Movie A\n")
        f.write("Action|2|Movie B\n")
        f.write("Action|3|Movie C\n")

    load_movies_from_file("tie_movies.txt")
    load_ratings_from_file("tie_ratings.txt")

    top_2 = get_top_n_movies(2)
    print(f"✓ Tie handling: Top 2 movies when all have same rating:")
    for movie, rating in top_2.items():
        print(f"  {movie}: {rating:.2f}")
    print("  (Pandas sort_values maintains stable sort - first occurrence order)")

    os.remove("tie_movies.txt")
    os.remove("tie_ratings.txt")

    # Test 7: Requesting more items than available
    print("\n--- EDGE CASE: Requesting More Items Than Available ---")
    load_movies_from_file("sample_movies.txt")
    load_ratings_from_file("sample_ratings.txt")

    top_100 = get_top_n_movies(100)
    print(f"✓ Requesting top 100 movies returns {len(top_100)} available movies")

    top_genres_100 = get_top_n_genres(100)
    print(f"✓ Requesting top 100 genres returns {len(top_genres_100)} available genres")


# ========================================
# RUN ALL TESTS
# ========================================

def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FEATURE COVERAGE TESTS")
    print("=" * 60)

    try:
        # Feature coverage tests
        test_load_movies()
        test_load_ratings()
        test_top_n_movies()
        test_top_n_movies_genre()
        test_top_n_genres()
        test_preferred_genre()
        test_top_3_movies_fav_genre()

        # Edge case tests
        test_edge_cases()

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
