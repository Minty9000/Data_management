import pandas as pd
import pandas.errors as pe
import os
import sys

# Global variables to simulate the original program
movies_df = None
rating_df = None

print("=" * 60)
print("MOVIE RECOMMENDER AUTOMATED TESTING")
print("=" * 60)



# VALIDATION AND FORMATTING HELPER FUNCTIONS


def is_column_numeric(df, col_name):
    """Checks if a column can be reasonably converted to a numeric type."""
    col = pd.to_numeric(df[col_name], errors='coerce')
    original_non_null_count = df[col_name].dropna().shape[0]
    if original_non_null_count == 0:
        return False
    nan_count_after_coercion = col.isna().sum()
    return nan_count_after_coercion < (original_non_null_count * 0.1)


def validate_dataframe(df, expected_columns, numeric_check_col=None):
    """Checks if the loaded DataFrame has the correct columns."""
    if df.columns.tolist() != expected_columns:
        return False
    if numeric_check_col and not is_column_numeric(df, numeric_check_col):
        return False
    return True


def format_series_for_display(series, key_column_name):
    """Formats a result Series for display."""
    if series.empty:
        return "No results."
    df = series.reset_index()
    if key_column_name == "Movie Name":
        df.columns = ["Movie Name", "Average Rating"]
    elif key_column_name == "Movie Genre":
        df.columns = ["Movie Genre", "Average Rating"]
    else:
        df.columns = [key_column_name, "Average Rating"]
    return df.to_string(index=False, justify="left", formatters={"Average Rating": "{:.2f}".format})



# DATA LOADER FUNCTIONS


def load_movies_from_file(file_path):
    """Load movies dataset from file, including bi-directional validation and empty file handling."""
    global movies_df
    expected_movie_cols = ["movie_genre", "movie_id", "movie_name"]

    try:
        temp_df = pd.read_csv(file_path, sep="|", header=None, names=expected_movie_cols)

    except pe.EmptyDataError:
        movies_df = pd.DataFrame(columns=expected_movie_cols)
        return True

    except FileNotFoundError:
        return False
    except Exception as e:
        return False

    if not validate_dataframe(temp_df, expected_movie_cols, numeric_check_col="movie_id"):
        return False

    is_mostly_integer = False
    try:
        pd.to_numeric(temp_df["movie_name"], errors='raise').astype(int)
        is_mostly_integer = True
    except (ValueError, TypeError):
        pass

    if is_mostly_integer:
        return False

    temp_df["movie_id"] = pd.to_numeric(temp_df["movie_id"], errors='coerce')
    movies_df = temp_df.dropna(subset=['movie_id'])
    return True


def load_ratings_from_file(file_path):
    """Load ratings dataset from file, including bi-directional validation and empty file handling."""
    global rating_df
    expected_rating_cols = ["movie_name", "rating", "user_id"]

    try:
        temp_df = pd.read_csv(file_path, sep="|", header=None, names=expected_rating_cols)

    except pe.EmptyDataError:
        rating_df = pd.DataFrame(columns=expected_rating_cols)
        return True

    except FileNotFoundError:
        return False
    except Exception as e:
        return False

    if not validate_dataframe(temp_df, expected_rating_cols, numeric_check_col="rating"):
        return False

    is_mostly_integer = False
    try:
        pd.to_numeric(temp_df["user_id"], errors='raise').astype(int)
        is_mostly_integer = True
    except (ValueError, TypeError):
        pass

    if not is_mostly_integer:
        return False

    temp_df["rating"] = pd.to_numeric(temp_df["rating"], errors="coerce")
    temp_df.dropna(subset=["rating"], inplace=True)
    rating_df = temp_df[(temp_df["rating"] >= 0) & (temp_df["rating"] <= 5)]

    return True


# DATA ANALYSIS FUNCTIONS (REINSERTED)


def get_top_n_movies(n):
    """Get top N movies overall by average rating"""
    if rating_df is None: return pd.Series(dtype=float)
    avg_ratings = rating_df.groupby("movie_name")["rating"].mean().sort_values(ascending=False).head(n)
    return avg_ratings


def get_top_n_movies_genre(genre, n):
    """Get top N movies in a specific genre"""
    if movies_df is None or rating_df is None: return pd.Series(dtype=float)
    genre_movies = movies_df[movies_df["movie_genre"].str.lower() == genre.lower()]
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

    user_ratings = rating_df[rating_df["user_id"].astype(str) == str(user_id)]
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


# DATA SETUP FUNCTION


TEST_MOVIE_CONTENT = """Action|101|Movie Z
Action|102|Movie X
Action|103|Movie Y
Comedy|104|Movie A
Comedy|105|Movie B
"""
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
INVALID_MOVIE_CONTENT = """Action|101|Movie Z
Comedy|104|Movie A
"""
INVALID_RATING_CONTENT = """Movie X|5.0|1
Movie Y|4.0|1
"""


def setup_deterministic_data():
    """Creates and loads rich test files used for assertions."""
    global movies_df, rating_df

    with open("test_movies.txt", "w") as f:
        f.write(TEST_MOVIE_CONTENT)
    with open("test_ratings.txt", "w") as f:
        f.write(TEST_RATING_CONTENT)
    with open("invalid_movies_file.txt", "w") as f:
        f.write(INVALID_MOVIE_CONTENT)
    with open("invalid_ratings_file.txt", "w") as f:
        f.write(INVALID_RATING_CONTENT)

    load_movies_from_file("test_movies.txt")
    load_ratings_from_file("test_ratings.txt")



# TEST FUNCTIONS


def test_feature_coverage():
    """Runs all feature tests with hard assertions."""
    print("\n" + "=" * 60)
    print("FEATURE COVERAGE TESTS (With Hard Assertions)")
    print("=" * 60)
    setup_deterministic_data()

    # --- Test 1-7 (UNCHANGED LOGIC) ---
    global movies_df, rating_df
    # ... (tests 1 and 2)
    assert movies_df is not None
    assert len(movies_df) == 5
    assert rating_df is not None
    assert len(rating_df) == 9
    print("✓ Data loaded successfully")

    # Test 3: Top N Movies (Overall)
    N = 2
    top_n = get_top_n_movies(N)
    expected_ratings = pd.Series([5.0, 4.5], index=["Movie Z", "Movie X"])
    assert len(top_n) == N
    assert top_n.index.tolist() == expected_ratings.index.tolist()
    print("✓ Top N Movies passed assertions.")

    # Test 4: Top N Movies in a Genre (Action)
    GENRE = "Action"
    top_genre = get_top_n_movies_genre(GENRE, 2)
    expected_ratings = pd.Series([5.0, 4.5], index=["Movie Z", "Movie X"])
    assert len(top_genre) == 2
    assert top_genre.index.tolist() == expected_ratings.index.tolist()
    print("✓ Top N Movies in Genre passed assertions.")

    # Test 5: Top N Genres
    N = 1
    top_genres = get_top_n_genres(N)
    expected_ratings = pd.Series([4.5], index=["Action"])
    assert len(top_genres) == N
    assert top_genres.index.tolist() == expected_ratings.index.tolist()
    print("✓ Top N Genres passed assertions.")

    # Test 6: Preferred Genre (User 4)
    USER_ID = 4
    pref_genre = get_preferred_genre(USER_ID)
    expected_genre = "Action"
    assert pref_genre == expected_genre
    print("✓ Preferred Genre passed assertions.")

    # Test 7: Top 3 Movies from Favorite Genre (User 4)
    top_3_user = get_top_3_movies_fav_genre(USER_ID)
    expected_ratings = pd.Series([5.0, 4.5, 4.0], index=["Movie Z", "Movie X", "Movie Y"])
    assert len(top_3_user) == 3
    assert top_3_user.index.tolist() == expected_ratings.index.tolist()
    print("✓ Top 3 Movies from Favorite Genre passed assertions.")


def test_sequential_run():
    """Runs a sequential check using the user's sample_files."""
    print("\n" + "=" * 60)
    print("QUICK SEQUENTIAL RUN (Uses sample_movies.txt and sample_ratings.txt)")
    print("=" * 60)

    global movies_df, rating_df
    movies_df = None
    rating_df = None

    if load_movies_from_file("sample_movies.txt"):
        print("✅ Movies file loaded successfully.")
    else:
        print("❌ FAILED to load sample_movies.txt. Check file path/existence or validation.")
        return

    if load_ratings_from_file("sample_ratings.txt"):
        print("✅ Ratings file loaded successfully. (Bad data filtered)")
    else:
        print("❌ FAILED to load sample_ratings.txt. Check file path/existence or validation.")
        return

    N = 2
    USER_ID = 1

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
    print("\n" + "=" * 60)
    print("EDGE CASE & NEGATIVE TESTS (Uses Deterministic Data)")
    print("=" * 60)

    setup_deterministic_data()
    global movies_df, rating_df

    # --- Edge Case 1: Validation Mismatch Check ---
    movies_df = None
    is_valid = load_movies_from_file("invalid_ratings_file.txt")
    assert is_valid == False, "❌ Movies loader failed to block ratings file."
    print("✓ Movies loader correctly blocked ratings file.")

    rating_df = None
    is_valid = load_ratings_from_file("invalid_movies_file.txt")
    assert is_valid == False, "❌ Ratings loader failed to block movies file."
    print("✓ Ratings loader correctly blocked movies file.")

    load_movies_from_file("test_movies.txt")
    load_ratings_from_file("test_ratings.txt")

    # --- Edge Case 2: Non-numeric User ID ---
    print("\n--- EDGE CASE 2: Non-numeric User ID ---")
    result = get_preferred_genre("non-numeric")
    assert result is None, "❌ Non-numeric ID should return None."
    print("✓ Correctly handles non-numeric user ID.")

    # --- Edge Case 3: Duplicate Ratings Averaging ---
    print("\n--- EDGE CASE 3: Duplicate Ratings Averaging ---")
    rating_df = pd.DataFrame({
        "movie_name": ["Movie D", "Movie D", "Movie E"],
        "rating": [5.0, 3.0, 4.0],
        "user_id": [1, 1, 2]
    })
    top_2 = get_top_n_movies(2)
    expected_ratings = pd.Series([4.0, 4.0], index=["Movie D", "Movie E"])
    assert (top_2.round(2) == expected_ratings.round(2)).all(), "❌ Duplicate rating average failed."
    print("✓ Duplicate ratings averaged correctly (4.0/4.0).")
    setup_deterministic_data()

    # --- Edge Case 4: Out-of-Range Ratings Filtering ---
    print("\n--- EDGE CASE 4: Out-of-Range Ratings Filtering ---")
    with open("temp_bad_ratings.txt", "w") as f:
        f.write("Movie Z|4.0|1\n")
        f.write("Movie Y|10.0|2\n")
        f.write("Movie X|-2.5|3\n")
        f.write("Movie A|3.0|4\n")

    load_ratings_from_file("temp_bad_ratings.txt")
    assert len(rating_df) == 2, f"❌ Range filtering failed: Expected 2 rows, got {len(rating_df)}"
    assert rating_df["rating"].max() == 4.0, "❌ Range filtering failed: Max rating should be 4.0."
    print("✓ Out-of-range and negative ratings filtered successfully.")
    os.remove("temp_bad_ratings.txt")
    setup_deterministic_data()

    # --- Edge Case 5: Non-existent file ---
    print("\n--- EDGE CASE 5: Non-existent File ---")
    result = load_movies_from_file("nonexistent_file_xyz.txt")
    assert result == False, "❌ Should return False for non-existent file."
    print("✓ Correctly handles non-existent file.")

    # --- Edge Case 6: Empty File (Checking for Expected Failure) ---
    print("\n--- EDGE CASE 6: Empty File (Checking for Expected Failure) ---")
    with open("temp_empty.txt", "w") as f:
        pass

    # Isolate the test for cleanliness
    movies_df = None

    # ⬅️ FIX: Assert that the loader returns FALSE, confirming the expected behavior.
    result = load_movies_from_file("temp_empty.txt")
    assert result == False, "❌ Empty file loader should return False upon error (EmptyDataError)."
    assert movies_df is None, "❌ Global DF should remain None upon failure."
    print("✓ Correctly fails to load empty file, triggering retry/exit flow.")
    os.remove("temp_empty.txt")

    setup_deterministic_data()

    # --- Edge Case 7: Requesting More Items Than Available ---
    print("\n--- EDGE CASE 7: Requesting More Items Than Available ---")
    top_100 = get_top_n_movies(100)
    assert len(top_100) == 5, f"❌ Requesting 100 movies returned wrong count: {len(top_100)}"
    print(f"✓ Requesting N=100 returns {len(top_100)} available movies.")



# RUN ALL TESTS


def run_all_tests():
    """Run all tests"""
    try:
        # Create dummy files for the Quick Sequential Run
        with open("sample_movies.txt", "w") as f:
            f.write(TEST_MOVIE_CONTENT)
        with open("sample_ratings.txt", "w") as f:
            f.write(TEST_RATING_CONTENT)

        test_sequential_run()
        test_feature_coverage()
        test_edge_cases()

        # Final cleanup of all temporary files
        os.remove("test_movies.txt")
        os.remove("test_ratings.txt")
        os.remove("invalid_movies_file.txt")
        os.remove("invalid_ratings_file.txt")
        os.remove("sample_movies.txt")
        os.remove("sample_ratings.txt")

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
