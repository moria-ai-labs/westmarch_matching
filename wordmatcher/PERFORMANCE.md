# WordMatcher Performance Analysis

This document details the performance characteristics of the matching functions provided by the WordMatcher library.

## Overview

Understanding the performance implications of different list sizes and word lengths is crucial for choosing the right approach and anticipating execution times. We benchmarked two primary matching functions:

1.  `find_closest_matches`: Uses Python's built-in `difflib` module.
2.  `find_closest_matches_rapidfuzz`: Uses the `rapidfuzz` library, which provides highly optimized string similarity calculations.

## Matching Algorithms & Complexity

Let N be the number of words in the `target_list`, M be the number of words in the `choice_list`, and L be the average word length.

### 1. `find_closest_matches` (using `difflib`)

-   **Algorithm:** For each of N target words, iterates through M choice words. Similarity is calculated using `difflib.SequenceMatcher.ratio()`.
-   **Time Complexity:** Approximately **`O(N * M * L^2)`**. The `L^2` term arises from the string comparison in `SequenceMatcher`, which can be quadratic in word length in the worst case.
-   **Space Complexity:** Approximately **`O(N*L + L^2)`**. This includes space for the results dictionary and internal space used by `SequenceMatcher` for comparing a pair of strings.

### 2. `find_closest_matches_rapidfuzz` (using `rapidfuzz`)

-   **Algorithm:** For each of N target words, uses `rapidfuzz.process.extractOne` to find the best match from M choice words. The scorer used is `rapidfuzz.fuzz.WRatio`, which is based on Levenshtein distance.
-   **Time Complexity:** Approximately **`O(N * M * L^2)`**. While the asymptotic complexity class is the same as the `difflib` version, `rapidfuzz` uses highly optimized C/C++ implementations for its calculations. This results in significantly smaller constant factors and thus much faster real-world performance.
-   **Space Complexity:** Approximately **`O(N*L + L_min)`**, where `L_min` is the length of the shorter string in a pair comparison for Levenshtein distance. This is generally more memory-efficient for the comparison part than `difflib`.

## Benchmark Setup

-   **Script:** `benchmarks/benchmark_matcher.py`
-   **Tool:** Python's `timeit` module for accurate time measurements.
-   **Method:** Randomly generated word lists were used for `target_list` and `choice_list` based on specified sizes and average word lengths. Each configuration was run multiple times (`num_benchmark_runs = 3`) and the average time was reported.
-   **Environment:** Standard Python environment with necessary libraries (`difflib` from standard library, `rapidfuzz` installed via pip).

## Benchmark Results

The following table shows the average execution time in seconds for various configurations:

| Function    | Target List | Choice List | Avg Word Len | Avg Time (s) |
|-------------|-------------|-------------|--------------|--------------|
| **difflib** |             |             |              |              |
| difflib     | 10          | 100         | 7            | 0.002604     |
| difflib     | 10          | 1000        | 7            | 0.027489     |
| difflib     | 100         | 100         | 7            | 0.029659     |
| difflib     | 100         | 1000        | 7            | 0.291927     |
| difflib     | 100         | 5000        | 7            | 1.448822     |
| difflib     | 500         | 1000        | 7            | 1.451844     |
| difflib     | 100         | 1000        | 3            | 0.167251     |
| difflib     | 100         | 1000        | 10           | 0.358723     |
| difflib     | 100         | 1000        | 15           | 0.515804     |
| **rapidfuzz**|            |             |              |              |
| rapidfuzz   | 10          | 100         | 7            | 0.000930     |
| rapidfuzz   | 10          | 1000        | 7            | 0.008381     |
| rapidfuzz   | 100         | 100         | 7            | 0.010038     |
| rapidfuzz   | 100         | 1000        | 7            | 0.087544     |
| rapidfuzz   | 100         | 5000        | 7            | 0.424047     |
| rapidfuzz   | 500         | 1000        | 7            | 0.423450     |
| rapidfuzz   | 100         | 1000        | 3            | 0.044390     |
| rapidfuzz   | 100         | 1000        | 10           | 0.074641     |
| rapidfuzz   | 100         | 1000        | 15           | 0.073090     |

## Analysis & Comparison

-   **Overall Speed:** `rapidfuzz` consistently outperforms `difflib` across all tested configurations. The speedup factor ranges from approximately **2.8x to 7x**.
-   **Scaling with List Sizes (N, M):** Both implementations show roughly linear scaling with increases in `target_list` size (N) and `choice_list` size (M), which is consistent with their `O(N*M*...)` complexity.
-   **Scaling with Word Length (L):**
    -   `difflib` shows a clear increase in execution time as average word length increases.
    -   `rapidfuzz` also shows an increase, but its performance advantage becomes even more pronounced for longer strings (e.g., ~7x faster for average word length 15 compared to ~3.7x for length 3). This highlights the efficiency of `rapidfuzz`'s underlying string comparison algorithms.
-   **Constant Factors:** The primary difference in real-world performance, despite similar asymptotic complexities, comes from the vastly smaller constant factors in `rapidfuzz` due to its optimized C/C++ backend and efficient algorithms (like those used in Levenshtein distance calculations).

## Conclusion & Recommendations

-   For applications requiring efficient word matching, **`find_closest_matches_rapidfuzz` is strongly recommended** due to its superior performance. The speed benefits are substantial, especially for larger datasets or when dealing with longer words.
-   The `find_closest_matches` function (using `difflib`) remains a viable alternative if there's an extremely strict requirement against external C-dependencies. However, `rapidfuzz` is a widely used and generally easy-to-install library on most platforms.

Consider the expected size of your word lists and average word lengths when choosing. For all but the smallest tasks, `rapidfuzz` will likely provide a noticeably better user experience by reducing processing time.
