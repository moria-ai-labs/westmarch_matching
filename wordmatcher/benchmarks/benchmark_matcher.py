import timeit
import random
import string
import os
import sys

# Adjust path to import from the parent directory's wordmatcher package
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from wordmatcher import (
    find_closest_matches,
    find_closest_matches_rapidfuzz,
    find_closest_matches_rapidfuzz_len_filter
)

# Store functions in a dictionary for easy access by name
MATCHING_FUNCTIONS = {
    "difflib": find_closest_matches,
    "rapidfuzz": find_closest_matches_rapidfuzz,
    "rapidfuzz_len_filter": find_closest_matches_rapidfuzz_len_filter,
}

def generate_random_word(length: int) -> str:
    """Generates a random word of a given length."""
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(length))

def generate_word_list(num_words: int, avg_word_length: int, length_variance_actual: int = 2) -> list[str]:
    """
    Generates a list of random words.
    Word lengths will vary around avg_word_length by +/- length_variance_actual.
    """
    words = []
    for _ in range(num_words):
        length = random.randint(max(1, avg_word_length - length_variance_actual), avg_word_length + length_variance_actual)
        words.append(generate_random_word(length))
    return words

def prepare_benchmark_lists(
    num_target_words: int,
    num_choice_words: int,
    avg_word_len: int,
    exact_match_percentage: float = 0.0, # Percentage of target words that are exact matches
    target_length_variance: int = 2, # Separate variance for target list
    choice_length_variance: int = 2  # Separate variance for choice list
) -> tuple[list[str], list[str]]:
    """
    Prepares target and choice lists for benchmarking with a specified percentage of exact matches
    and potentially different word length variances for target and choice lists.
    """
    if not (0 <= exact_match_percentage <= 1):
        raise ValueError("exact_match_percentage must be between 0 and 1")

    base_choice_list = generate_word_list(num_choice_words, avg_word_len, choice_length_variance)

    num_exact_matches = int(num_target_words * exact_match_percentage)
    num_random_targets = num_target_words - num_exact_matches

    target_list = []

    # Add exact matches to target_list (sample from choice_list)
    if num_exact_matches > 0:
        if not base_choice_list:
            temp_choices_for_exact_match = generate_word_list(max(1, num_exact_matches), avg_word_len, choice_length_variance) # use choice_length_variance
            target_list.extend(random.sample(temp_choices_for_exact_match, min(num_exact_matches, len(temp_choices_for_exact_match))))
        elif len(base_choice_list) < num_exact_matches:
            exact_sample = base_choice_list * (num_exact_matches // len(base_choice_list) + 1)
            target_list.extend(random.sample(exact_sample, num_exact_matches))
        else:
            target_list.extend(random.sample(base_choice_list, num_exact_matches))

    # Add remaining random (likely non-matching) target words
    # These random targets should use target_length_variance
    random_targets = generate_word_list(num_random_targets, avg_word_len, target_length_variance)
    target_list.extend(random_targets)

    random.shuffle(target_list) # Shuffle to mix exact and random targets

    # Ensure choice_list is not empty if it was initially generated as such by num_choice_words=0
    # and target_list might need something to compare against for non-exact part.
    final_choice_list = base_choice_list
    if not final_choice_list and num_target_words > 0 : # if choice list is empty but target is not
        final_choice_list = [generate_random_word(avg_word_len)]


    # Ensure target_list is not empty if it was initially generated as such by num_target_words=0
    if not target_list and num_target_words > 0: # Should not happen with current logic but as safeguard
        target_list = [generate_random_word(avg_word_len)]

    return target_list, final_choice_list


def run_benchmark(
    matcher_function_name: str,
    target_list_size: int,
    choice_list_size: int,
    avg_word_len: int,
    exact_match_perc: float = 0.0,
    target_len_variance: int = 2, # New parameter
    choice_len_variance: int = 2,   # New parameter
    num_runs: int = 10
):
    """
    Runs a benchmark for a specified matching function with specified parameters.

    Args:
        target_list_size: Number of words in the target list.
        choice_list_size: Number of words in the choice list.
        avg_word_len: Average length of words to generate.
        exact_match_perc: Percentage of target words that are exact matches in choice_list.
        target_len_variance: Variance for target word lengths.
        choice_len_variance: Variance for choice word lengths.
        num_runs: Number of times to run the timeit measurement for averaging.

    Returns:
        Average execution time in seconds.
    """
    target_list, choice_list = prepare_benchmark_lists(
        num_target_words=target_list_size,
        num_choice_words=choice_list_size,
        avg_word_len=avg_word_len,
        exact_match_percentage=exact_match_perc,
        target_length_variance=target_len_variance,
        choice_length_variance=choice_len_variance
    )

    # Make sure lists are not empty for the function, though prepare_benchmark_lists should handle this.
    # Adding a safeguard here just in case.
    if not target_list and target_list_size > 0:
        target_list = [generate_random_word(avg_word_len)]
    if not choice_list and choice_list_size > 0:
        choice_list = [generate_random_word(avg_word_len)]
    # Handle case where target_list_size or choice_list_size is 0, lists could be empty.
    # The matching functions are designed to handle empty lists.

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

    # Define base benchmark configurations (no exact matches)
    # Tuple: (target_size, choice_size, avg_word_len, exact_match_percentage, target_len_var, choice_len_var)
    # Default variance is 2 for both target and choice.
    default_variance = 2
    base_configurations = [
        (10, 100, 7, 0.0, default_variance, default_variance),
        (10, 1000, 7, 0.0, default_variance, default_variance),
        (100, 100, 7, 0.0, default_variance, default_variance),
        (100, 1000, 7, 0.0, default_variance, default_variance),
        (100, 5000, 7, 0.0, default_variance, default_variance),
        (500, 1000, 7, 0.0, default_variance, default_variance),
        (100, 1000, 3, 0.0, default_variance, default_variance), # Short words
        (100, 1000, 10, 0.0, default_variance, default_variance), # Longer words
        (100, 1000, 15, 0.0, default_variance, default_variance), # Even longer words
    ]

    # Configurations to test impact of exact matches
    exact_match_impact_config_base = (100, 1000, 7) # t_size, c_size, w_len
    exact_match_impact_percentages = [0.0, 0.1, 0.5, 0.9, 1.0]
    exact_match_impact_configurations = [
        (*exact_match_impact_config_base, perc, default_variance, default_variance)
        for perc in exact_match_impact_percentages
    ]

    # Configurations specifically for the N*M plot with 10% exact matches
    plot_data_configurations_10_perc_exact = [
        (10, 100, 7, 0.1, default_variance, default_variance),
        (10, 1000, 7, 0.1, default_variance, default_variance),
        (100, 100, 7, 0.1, default_variance, default_variance),
        (100, 5000, 7, 0.1, default_variance, default_variance),
        (500, 1000, 7, 0.1, default_variance, default_variance),
    ]

    # Configuration to test wide variance in choice list word lengths
    # Target words have normal variance, choice words have wide variance.
    # Using avg_word_len = 10, target_variance = 2 (words 8-12), choice_variance = 7 (words 3-17)
    wide_variance_config = [
        (100, 1000, 10, 0.0, default_variance, 7)
    ]

    combined_configurations = list(set(
        base_configurations +
        exact_match_impact_configurations +
        plot_data_configurations_10_perc_exact +
        wide_variance_config
    ))

    num_benchmark_runs = 3

    print(f"{'Function':<22} | {'Target List':<12} | {'Choice List':<12} | {'Avg Word Len':<12} | {'Exact %':<8} | {'Tgt Var':<7} | {'Cho Var':<7} | {'Avg Time (s)':<15}")
    print("-" * 125) # Adjusted separator length

    for func_name in MATCHING_FUNCTIONS:
        print(f"\n--- Benchmarking for: {func_name} ---")
        # Tuple structure: (t_size, c_size, w_len, ex_perc, t_var, c_var)
        sorted_configurations = sorted(combined_configurations, key=lambda x: (x[0] * x[1], x[3], x[5], x[4]))

        for t_size, c_size, w_len, ex_perc, t_var, c_var in sorted_configurations:
            avg_time = run_benchmark(
                matcher_function_name=func_name,
                target_list_size=t_size,
                choice_list_size=c_size,
                avg_word_len=w_len,
                exact_match_perc=ex_perc,
                target_len_variance=t_var,
                choice_len_variance=c_var,
                num_runs=num_benchmark_runs
            )
            print(f"{func_name:<22} | {t_size:<12} | {c_size:<12} | {w_len:<12} | {ex_perc*100:<7.1f}% | {t_var:<7} | {c_var:<7} | {avg_time:<15.6f}")

    print("\nBenchmark finished.")
    print("Note: The `difflib` performance can be sensitive to word content and similarity.")
    print("These benchmarks use randomly generated strings.")
