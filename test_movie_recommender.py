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
# HELPER FUNCTIONS (CORE LOGIC COPIED FROM ORIGINAL)
# ========================================

def format_series_for_display(series, key_column_name):
    """
    Formats a result Series (index=Name/Genre, value=Avg Rating) into
    a string matching the main code's two-column, formatted output style.
    """
    if series.empty:
        return "No results."

    df = series.reset_index()

    # Assign the correct column names for display
    if key_column_name == "Movie Name":
        df.columns = ["Movie Name", "Average Rating"]
    elif key_column_name == "Movie Genre":
        df.columns = ["Movie Genre", "Average Rating"]
    else:
        df.columns = [key_column_name, "Average Rating"]

    # Use the exact formatting specified in the original main file
    return df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format})


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
    if rating_df is None: return pd.Series(dtype=float)
    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_top_n_movies_genre(genre, n):
    """Get top N movies in a specific genre"""
    if movies_df is None or rating_df is None: return pd.Series(dtype=float)
    genre_movies = movies_df[movies_df["movie_genre"].str.lower() == genre.lower()]  # Added .lower() for robustness
    if genre_movies.empty: return pd.Series(dtype=float)
    merged = rating_df.merge(genre_movies, on="movie_name")
    if merged.empty: return pd.Series(dtype=float)
    avg_ratings = merged.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_top_n_genres(n):
    """Get top N genres by average rating"""
    if movies_df is None or rating_df is None: return pd.Series(dtype=float)
    merged = rating_df.merge(movies_df, on="movie_name")
    if merged.empty: return pd.Series(dtype=float)
    avg_ratings = merged.groupby("movie_genre")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_preferred_genre(user_id):
    """Get user's most preferred genre"""
    if movies_df is None or rating_df is None: return None
    try:
        user_id_int = int(user_id)
    except ValueError:
        return None

    user_ratings = rating_df[rating_df["user_id"] == user_id_int]
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
        return get_top_n_movies_genre(fav_genre, 3)
    return None


# ========================================
# DATA SETUP FUNCTION (For Deterministic Testing)
# ========================================

TEST_MOVIE_CONTENT = """Action|101|Movie Z
Action|102|Movie X
Action|103|Movie Y
Comedy|104|Movie A
Comedy|105|Movie B
"""
# Averages: Z(5.0), X(4.5), Y(4.0), A(4.0), B(3.0). Action Avg: 4.5, Comedy Avg: 4.0
TEST_RATING_CONTENT = """Movie X|5.0|1
Movie Y|4.0|1
Movie Z|5.0|2
Movie A|3.0|2
Movie X|4.0|3
Movie Y|4.0|3
Movie A|5.0|4
Movie Z|5.0|4
Movie B|3.0|4
"""


def setup_deterministic_data():
    """
    Creates and loads rich test files used for the FEATURE COVERAGE and
    EDGE CASE tests to ensure assertions are reliable.
    """
    global movies_df, rating_df

    # Create test files
    with open("test_movies.txt", "w") as f:
        f.write(TEST_MOVIE_CONTENT)
    with open("test_ratings.txt", "w") as f:
        f.write(TEST_RATING_CONTENT)

    # Load test files into globals for the tests that follow
    load_movies_from_file("test_movies.txt")
    load_ratings_from_file("test_ratings.txt")


# ========================================
# TEST FUNCTIONS (With Hard Assertions and Expected/Actual Printouts)
# ========================================

# --- Feature Coverage Tests (Uses Deterministic Data) ---

def test_feature_coverage():
    """Runs all feature tests with hard assertions."""
    print("\n" + "=" * 60)
    print("FEATURE COVERAGE TESTS (With Hard Assertions)")
    print("=" * 60)

    # Setup known deterministic data for all assertions
    setup_deterministic_data()

    # --- Test 1: Load Movies (Sanity Check) ---
    print("\n--- TEST 1: Load Movies (Sanity Check) ---")
    assert movies_df is not None, "❌ Movies dataframe is None after load"
    assert len(movies_df) == 5, f"❌ Expected 5 movies, got {len(movies_df)}"
    print("✓ Movies dataset loaded successfully")

    # --- Test 2: Load Ratings (Sanity Check) ---
    print("\n--- TEST 2: Load Ratings (Sanity Check) ---")
    assert rating_df is not None, "❌ Ratings dataframe is None after load"
    assert len(rating_df) == 9, f"❌ Expected 9 ratings, got {len(rating_df)}"
    print("✓ Ratings dataset loaded successfully")

    # --- Test 3: Top N Movies (Overall) ---
    N = 2
    top_n = get_top_n_movies(N)

    # Expected: Movie Z (5.0), Movie X (4.5)
    expected_ratings = pd.Series([5.0, 4.5], index=["Movie Z", "Movie X"])

    print(f"\n--- TEST 3: Top {N} Movies (Overall) ---")
    print("Expected:\n" + format_series_for_display(expected_ratings, "Movie Name"))
    print("Actual:\n" + format_series_for_display(top_n, "Movie Name"))

    assert len(top_n) == N, f"❌ Top N Movies failed length check: Expected {N}, got {len(top_n)}"
    assert top_n.index.tolist() == expected_ratings.index.tolist(), "❌ Top N Movies failed ranking check"
    assert (top_n.round(2) == expected_ratings.round(2)).all(), "❌ Top N Movies failed rating check"
    print("✓ Top N Movies passed assertions.")

    # --- Test 4: Top N Movies in a Genre (Action) ---
    GENRE = "Action"
    top_genre = get_top_n_movies_genre(GENRE, 2)

    # Expected: Movie Z (5.0), Movie X (4.5)
    expected_ratings = pd.Series([5.0, 4.5], index=["Movie Z", "Movie X"])

    print(f"\n--- TEST 4: Top 2 Movies in '{GENRE}' ---")
    print("Expected:\n" + format_series_for_display(expected_ratings, "Movie Name"))
    print("Actual:\n" + format_series_for_display(top_genre, "Movie Name"))

    assert len(top_genre) == 2, f"❌ Top Genre Movies failed length check: Expected 2, got {len(top_genre)}"
    assert top_genre.index.tolist() == expected_ratings.index.tolist(), "❌ Top Genre Movies failed ranking check"
    print("✓ Top N Movies in Genre passed assertions.")

    # --- Test 5: Top N Genres ---
    N = 1
    top_genres = get_top_n_genres(N)

    # Expected: Action (4.5)
    expected_ratings = pd.Series([4.5], index=["Action"])

    print(f"\n--- TEST 5: Top {N} Genre ---")
    print("Expected:\n" + format_series_for_display(expected_ratings, "Movie Genre"))
    print("Actual:\n" + format_series_for_display(top_genres, "Movie Genre"))

    assert len(top_genres) == N, f"❌ Top N Genres failed length check: Expected {N}, got {len(top_genres)}"
    assert top_genres.index.tolist() == expected_ratings.index.tolist(), "❌ Top N Genres failed ranking check"
    print("✓ Top N Genres passed assertions.")

    # --- Test 6: Preferred Genre (User 4) ---
    USER_ID = 4
    pref_genre = get_preferred_genre(USER_ID)

    # Expected: Action (U4 rated A(5.0, Comedy), Z(5.0, Action), B(3.0, Comedy) -> Action Avg 5.0 > Comedy Avg 4.0)
    expected_genre = "Action"

    print(f"\n--- TEST 6: Preferred Genre (User {USER_ID}) ---")
    print(f"Expected: {expected_genre}")
    print(f"Actual: {pref_genre}")

    assert pref_genre == expected_genre, f"❌ Preferred Genre failed: Expected {expected_genre}, got {pref_genre}"
    print("✓ Preferred Genre passed assertions.")

    # --- Test 7: Top 3 Movies from Favorite Genre (User 4) ---
    top_3_user = get_top_3_movies_fav_genre(USER_ID)

    # Expected: Z(5.0), X(4.5), Y(4.0) (all Action)
    expected_ratings = pd.Series([5.0, 4.5, 4.0], index=["Movie Z", "Movie X", "Movie Y"])

    print(f"\n--- TEST 7: Top 3 Movies from User {USER_ID}'s Favorite Genre ---")
    print("Expected:\n" + format_series_for_display(expected_ratings, "Movie Name"))
    print("Actual:\n" + format_series_for_display(top_3_user, "Movie Name"))

    assert len(top_3_user) == 3, f"❌ Top 3 Fav Genre failed length check: Expected 3, got {len(top_3_user)}"
    assert top_3_user.index.tolist() == expected_ratings.index.tolist(), "❌ Top 3 Fav Genre failed ranking check"
    print("✓ Top 3 Movies from Favorite Genre passed assertions.")


def test_sequential_run():
    """Runs a sequential check using the user's sample_files."""
    print("\n" + "=" * 60)
    print("QUICK SEQUENTIAL RUN (Uses sample_movies.txt and sample_ratings.txt)")
    print("=" * 60)

    # We must reset globals before loading user's files
    global movies_df, rating_df
    movies_df = None
    rating_df = None

    # Load Data (Simulates Menu Options 1 & 2) using physical files
    if load_movies_from_file("sample_movies.txt"):
        print("✅ Movies file loaded successfully.")
    else:
        print("❌ FAILED to load sample_movies.txt. Check file path/existence.")
        return

    if load_ratings_from_file("sample_ratings.txt"):
        print("✅ Ratings file loaded successfully. (Bad data filtered)")
    else:
        print("❌ FAILED to load sample_ratings.txt. Check file path/existence.")
        return

    # Set up known parameters for the sequential run
    N = 2
    USER_ID = 1

    # Run Feature Functions and Display (Simulates Menu Options 3-7)

    top_n = get_top_n_movies(N)
    print(f"\n--- 3. Top {N} Movies (Overall) ---")
    print(format_series_for_display(top_n, "Movie Name"))

    GENRE = "Action"
    top_n_genre = get_top_n_movies_genre(GENRE, N)
    print(f"\n--- 4. Top {N} Movies in '{GENRE}' ---")
    print(format_series_for_display(top_n_genre, "Movie Name"))

    top_n_genres = get_top_n_genres(N)
    print(f"\n--- 5. Top {N} Genres ---")
    print(format_series_for_display(top_n_genres, "Movie Genre"))

    fav_genre = get_preferred_genre(USER_ID)
    print(f"\n--- 6. Preferred Genre for User {USER_ID} ---")
    print(f"Result: {fav_genre}")

    if fav_genre:
        top_3_fav = get_top_3_movies_fav_genre(USER_ID)
        print(f"\n--- 7. Top 3 Movies from Favorite Genre ('{fav_genre}') ---")
        print(format_series_for_display(top_3_fav, "Movie Name"))
    else:
        print(f"\n--- 7. Top 3 Movies from Favorite Genre ---")
        print(f"Cannot run: User {USER_ID} has no preferred genre (or movie not mapped).")

    print("\n" + "=" * 60)
    print("END OF SEQUENTIAL RUN")
    print("=" * 60)


def test_edge_cases():
    """Test edge cases and negative scenarios."""

    # ⚠️ NOTE: This function relies on the latest load being the deterministic test data.

    print("\n" + "=" * 60)
    print("EDGE CASE & NEGATIVE TESTS (Uses Deterministic Data)")
    print("=" * 60)

    # Reload deterministic data to ensure a clean start for the edge cases
    setup_deterministic_data()

    # --- Edge Case 1: Non-numeric User ID ---
    print("\n--- EDGE CASE 1: Non-numeric User ID ---")
    result = get_preferred_genre("non-numeric")
    assert result is None, "❌ Non-numeric ID should return None."
    print("✓ Correctly handles non-numeric user ID.")

    # --- Edge Case 2: Duplicate Ratings Averaging ---
    print("\n--- EDGE CASE 2: Duplicate Ratings Averaging ---")
    # Reset data to manually inject tied movies for this specific test
    global movies_df, rating_df

    # Data: Movie D (4.0), Movie E (4.0)
    rating_df = pd.DataFrame({
        "movie_name": ["Movie D", "Movie D", "Movie E"],
        "rating": [5.0, 3.0, 4.0],  # D avg: 4.0, E avg: 4.0
        "user_id": [1, 1, 2]
    })

    top_2 = get_top_n_movies(2)
    expected_ratings = pd.Series([4.0, 4.0], index=["Movie D", "Movie E"])

    print("Expected:\n" + format_series_for_display(expected_ratings, "Movie Name"))
    print("Actual:\n" + format_series_for_display(top_2, "Movie Name"))

    assert (top_2.round(2) == expected_ratings.round(2)).all(), "❌ Duplicate rating average failed."
    print("✓ Duplicate ratings averaged correctly (4.0/4.0).")

    # Reload deterministic data after modifying rating_df
    setup_deterministic_data()

    # --- Edge Case 3: Out-of-Range Ratings Filtering ---
    print("\n--- EDGE CASE 3: Out-of-Range Ratings Filtering ---")
    with open("temp_bad_ratings.txt", "w") as f:
        f.write("Movie Z|4.0|1\n")
        f.write("Movie Y|10.0|2\n")  # Too high
        f.write("Movie X|-2.5|3\n")  # Negative
        f.write("Movie A|3.0|4\n")

    load_ratings_from_file("temp_bad_ratings.txt")

    # Expected: Only Z (4.0) and A (3.0) remain. Total 2 rows.
    assert len(rating_df) == 2, f"❌ Range filtering failed: Expected 2 rows, got {len(rating_df)}"
    assert rating_df["rating"].max() == 4.0, "❌ Range filtering failed: Max rating should be 4.0."
    print("✓ Out-of-range and negative ratings filtered successfully.")
    os.remove("temp_bad_ratings.txt")

    # Reload deterministic data after modifying rating_df
    setup_deterministic_data()

    # --- Edge Case 4: Non-existent file ---
    print("\n--- EDGE CASE 4: Non-existent File ---")
    result = load_movies_from_file("nonexistent_file_xyz.txt")
    assert result == False, "❌ Should return False for non-existent file."
    print("✓ Correctly handles non-existent file.")

    # --- Edge Case 5: Empty File ---
    print("\n--- EDGE CASE 5: Empty File ---")
    with open("temp_empty.txt", "w") as f:
        pass

    load_movies_from_file("temp_empty.txt")
    assert movies_df.empty, "❌ Empty file should result in empty DataFrame."
    print("✓ Correctly handles empty file.")
    os.remove("temp_empty.txt")

    # Reload deterministic data after modifying movies_df
    setup_deterministic_data()

    # --- Edge Case 6: Requesting More Items Than Available ---
    print("\n--- EDGE CASE 6: Requesting More Items Than Available ---")
    # State is now guaranteed to be clean (5 movies available)
    top_100 = get_top_n_movies(100)
    assert len(top_100) == 5, f"❌ Requesting 100 movies returned wrong count: {len(top_100)}"
    print(f"✓ Requesting N=100 returns {len(top_100)} available movies.")


# ========================================
# RUN ALL TESTS
# ========================================

def run_all_tests():
    """Run all tests"""
    try:
        # 1. Run Sequential Check (Uses user's sample_files)
        test_sequential_run()

        # 2. Run Feature Coverage (Uses deterministic test_files)
        test_feature_coverage()

        # 3. Run Edge Cases (Uses deterministic data)
        test_edge_cases()

        # Final cleanup of the deterministic files
        os.remove("test_movies.txt")
        os.remove("test_ratings.txt")

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
