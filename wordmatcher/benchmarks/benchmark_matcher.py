import timeit
import random
import string
import os
import sys

# Adjust path to import from the parent directory's wordmatcher package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from wordmatcher import find_closest_matches, find_closest_matches_rapidfuzz

# Store functions in a dictionary for easy access by name
MATCHING_FUNCTIONS = {
    "difflib": find_closest_matches,
    "rapidfuzz": find_closest_matches_rapidfuzz,
}

def generate_random_word(length: int) -> str:
    """Generates a random word of a given length."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def generate_word_list(num_words: int, avg_word_length: int, length_variance: int = 2) -> list[str]:
    """
    Generates a list of random words.
    Word lengths will vary around avg_word_length by +/- length_variance.
    """
    words = []
    for _ in range(num_words):
        length = random.randint(max(1, avg_word_length - length_variance), avg_word_length + length_variance)
        words.append(generate_random_word(length))
    return words

def run_benchmark(matcher_function_name: str, target_list_size: int, choice_list_size: int, avg_word_len: int, num_runs: int = 10):
    """
    Runs a benchmark for a specified matching function with specified parameters.

    Args:
        target_list_size: Number of words in the target list.
        choice_list_size: Number of words in the choice list.
        avg_word_len: Average length of words to generate.
        num_runs: Number of times to run the timeit measurement for averaging.

    Returns:
        Average execution time in seconds.
    """
    target_list = generate_word_list(target_list_size, avg_word_len)
    choice_list = generate_word_list(choice_list_size, avg_word_len)

    # Make sure lists are not empty for the function
    if not target_list: target_list = [generate_random_word(avg_word_len)]
    if not choice_list: choice_list = [generate_random_word(avg_word_len)]

    # Determine the actual function to benchmark
    current_matcher_func = MATCHING_FUNCTIONS.get(matcher_function_name)
    if current_matcher_func is None:
        raise ValueError(f"Unknown matching function: {matcher_function_name}")

    stmt_code = "current_matcher_func(target_list, choice_list)"

    # Pass the actual function and its data to timeit's globals
    timeit_globals = {
        "current_matcher_func": current_matcher_func,
        "target_list": target_list, # Generated fresh for this run
        "choice_list": choice_list, # Generated fresh for this run
    }

    # No complex setup needed if globals are correctly passed and stmt uses them.
    # timeit will execute stmt_code within a context where timeit_globals are available.
    setup_code = "" # Keep it minimal or import specific things if truly needed from __main__

    times = timeit.repeat(stmt_code, setup=setup_code, globals=timeit_globals, number=1, repeat=num_runs)

    return sum(times) / len(times) # Average time

if __name__ == "__main__":
    print("Running WordMatcher Benchmarks...\n")

    # Define benchmark configurations
    # (target_size, choice_size, avg_word_len)
    configurations = [
        (10, 100, 7),
        (10, 1000, 7),
        (100, 100, 7),
        (100, 1000, 7),
        (100, 5000, 7),
        (500, 1000, 7),
        # (1000, 1000, 7), # Can be slow
        # (1000, 5000, 7), # Can be very slow

        # Test with different word lengths
        (100, 1000, 3), # Short words
        (100, 1000, 10), # Longer words
        (100, 1000, 15), # Even longer words
    ]

    # For quick testing, reduce number of runs
    # For more accuracy, increase num_runs (e.g., 5, 10)
    # For the initial run, let's use a moderate number of runs.
    num_benchmark_runs = 3

    print(f"{'Function':<12} | {'Target List':<12} | {'Choice List':<12} | {'Avg Word Len':<12} | {'Avg Time (s)':<15}")
    print("-" * 80) # Adjusted separator length

    for func_name in MATCHING_FUNCTIONS:
        print(f"\n--- Benchmarking for: {func_name} ---")
        for t_size, c_size, w_len in configurations:
            avg_time = run_benchmark(
                matcher_function_name=func_name,
                target_list_size=t_size,
                choice_list_size=c_size,
                avg_word_len=w_len,
                num_runs=num_benchmark_runs
            )
            print(f"{func_name:<12} | {t_size:<12} | {c_size:<12} | {w_len:<12} | {avg_time:<15.6f}")

    print("\nBenchmark finished.")
    print("Note: The `difflib` performance can be sensitive to word content and similarity.")
    print("These benchmarks use randomly generated strings.")
