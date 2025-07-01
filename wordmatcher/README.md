# WordMatcher

WordMatcher is a Python library designed to efficiently find the closest match for a given set of words from a predefined list of choices. For each word in a target list, it identifies the most similar word in a choice list.

## Features

-   Fast and efficient matching.
-   Easy to integrate into Python projects.
-   Uses well-known string similarity algorithms.

## Installation

As this package is currently under development and not yet published on PyPI, you can install it directly from a local clone of the repository.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/yourusername/wordmatcher.git # Replace with the actual URL
    cd wordmatcher
    ```

2.  **Install the package:**
    You have a couple of options for installation:

    *   **Standard installation:**
        This installs the package like any other Python package.
        ```bash
        pip install .
        ```

    *   **Editable (development) installation:**
        This is recommended if you plan to make changes to the code. It installs the package in a way that your changes are immediately reflected without needing to reinstall.
        ```bash
        pip install -e .
        ```

    Both installation methods will also install `rapidfuzz`, which is a dependency for the high-performance matching functions.

## Usage

WordMatcher provides functions for finding closest matches, with different performance characteristics:

1.  `find_closest_matches_rapidfuzz_len_filter(target_list, choice_list, score_cutoff=60.0, length_delta=3)`:
    *   **Recommended for general use, especially if choice words have varied lengths.**
    *   Uses `rapidfuzz` and includes two optimizations:
        1.  Exact match first: Skips fuzzy matching if an exact match is found.
        2.  Length filtering: Narrows down choices to those with lengths similar to the target word (target_length +/- `length_delta`) before fuzzy matching.
    *   `score_cutoff` is 0-100 (default 60). `length_delta` (default 3) controls the length window.

2.  `find_closest_matches_rapidfuzz(target_list, choice_list, score_cutoff=60.0)`:
    *   Uses `rapidfuzz` and the "exact match first" optimization.
    *   Faster than `difflib`, and may be marginally faster than `_len_filter` version if choice word lengths are already very uniform and close to target lengths.

3.  `find_closest_matches(target_list, choice_list)`:
    *   Uses Python's built-in `difflib` and the "exact match first" optimization.
    *   Slowest, but has no external C dependencies (beyond those `rapidfuzz` might bring if also used).

**Example using `rapidfuzz_len_filter` (recommended):**
```python
from wordmatcher import find_closest_matches_rapidfuzz_len_filter

target_words = ["apple", "banan", "grappe"]
choice_words = ["apricot", "banana", "grape", "orange", "pear", "longchoiceexample"]

# Using default cutoff 60 and length_delta 3
matches = find_closest_matches_rapidfuzz_len_filter(target_words, choice_words)
print(matches)
# Expected output (rapidfuzz with WRatio might give different results than difflib, e.g.):
# {'apple': 'apricot', 'banan': 'banana', 'grappe': 'grape'}
# Actual results can vary based on scorer and specific string similarities.
```

**Example using `difflib`:**
```python
from wordmatcher import find_closest_matches

target_words = ["apple", "banan", "grappe"]
choice_words = ["apricot", "banana", "grape", "orange", "pear"]

matches = find_closest_matches(target_words, choice_words)
print(matches)
# Expected output (will depend on the matching algorithm and environment):
# {'apple': 'apricot', 'banan': 'banana', 'grappe': 'grape'}
# (Note: difflib behavior can be inconsistent in some environments as noted in PERFORMANCE.md)
```

For detailed performance analysis and benchmarks, please see [PERFORMANCE.md](PERFORMANCE.md).

## Performance Visualization

To visually compare the performance of the `difflib` and `rapidfuzz` based matchers (with the "exact match first" optimization applied), especially how they scale with the product of target and choice list sizes (N*M), you can generate a plot. The following plot shows performance when 10% of target words have an exact match in the choice list, with an average word length of 7.

**(You can generate `wordmatcher_performance_10perc_exact.png` by running the script below. If you place it in an `assets` subfolder in the repository, you can display it here using: `![Performance Plot](assets/wordmatcher_performance_10perc_exact.png)`)**

<details>
<summary>Click to view Python script for generating the performance plot</summary>

```python
# wordmatcher/benchmarks/plot_performance_graph.py
import matplotlib.pyplot as plt
import numpy as np

def generate_performance_plot():
    """
    Generates a plot comparing performance of difflib and rapidfuzz
    with 10% exact matches.
    """
    # Averaged Data for Plot (10% Exact Matches, Avg Word Len = 7)
    # N*M values (product of target list size and choice list size)
    nm_values = np.array([1000, 10000, 100000, 500000])

    # Average Time (s) for difflib
    difflib_times = np.array([
        0.002904,  # N*M = 1,000
        0.031906,  # N*M = 10,000
        0.277241,  # N*M = 100,000
        1.412573   # N*M = 500,000
    ])

    # Average Time (s) for rapidfuzz
    rapidfuzz_times = np.array([
        0.000946,  # N*M = 1,000
        0.009041,  # N*M = 10,000
        0.087245,  # N*M = 100,000
        0.422434   # N*M = 500,000
    ])

    plt.figure(figsize=(10, 6))

    plt.plot(nm_values, difflib_times, marker='o', linestyle='-', label='difflib (optimized)')
    plt.plot(nm_values, rapidfuzz_times, marker='s', linestyle='-', label='rapidfuzz (optimized)')

    plt.title('Performance Comparison (10% Exact Matches, Avg Word Len 7)')
    plt.xlabel('N*M (Product of Target List Size and Choice List Size)')
    plt.ylabel('Average Time (s)')

    plt.xscale('log')

    plt.xticks(nm_values, [f'{val:,}' for val in nm_values])
    plt.minorticks_off()

    plt.legend()
    plt.grid(True, which="both", ls="--", alpha=0.7)
    plt.tight_layout()

    output_filename = "wordmatcher_performance_10perc_exact.png"
    # To run this script, ensure you are in the 'wordmatcher/benchmarks/' directory
    # or adjust path for saving if running from project root.
    # For direct execution of this snippet, save to current dir:
    # import os
    # if os.path.basename(os.getcwd()) == "benchmarks":
    #     output_filename = "../assets/" + output_filename # Example: save to project_root/assets/
    # else: # Assuming script is run from project root where README is
    #     if not os.path.exists("assets"): os.makedirs("assets")
    #     output_filename = "assets/" + output_filename

    plt.savefig(output_filename) # Saves to current directory of script if not path specified
    print(f"Plot saved as {output_filename}")

if __name__ == "__main__":
    try:
        import matplotlib
    except ImportError:
        print("Matplotlib is not installed. Please install it to generate the plot:")
        print("  pip install matplotlib")
        exit()

    generate_performance_plot()
```
</details>

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```
