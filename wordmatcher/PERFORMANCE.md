# WordMatcher Performance Analysis

This document details the performance characteristics of the matching functions provided by the WordMatcher library.

## Overview

Understanding the performance implications of different list sizes and word lengths is crucial for choosing the right approach and anticipating execution times. We benchmarked two primary matching functions:

1.  `find_closest_matches`: Uses Python's built-in `difflib` module.
2.  `find_closest_matches_rapidfuzz`: Uses the `rapidfuzz` library, which provides highly optimized string similarity calculations.

## Matching Algorithms & Complexity

Let N be the number of words in the `target_list`, M be the number of words in the `choice_list`, and L be the average word length.

All matching functions now incorporate an **"Exact Match First" Optimization**:
Before performing fuzzy matching, each target word is first checked for an exact match within the `choice_list` (using an efficient set lookup). If an exact match is found, that word is used, and the more computationally intensive fuzzy matching step is skipped for that target word. This can lead to significant performance gains when exact matches are common.

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

The following table shows the average execution time in seconds for various configurations, including tests with a varying percentage of exact matches between the target and choice lists.

| Function    | Target List | Choice List | Avg Word Len | Exact % | Avg Time (s) |
|-------------|-------------|-------------|--------------|---------|--------------|
| **difflib** |             |             |              |         |              |
| difflib     | 10          | 100         | 7            | 0.0%    | 0.003266     |
| difflib     | 10          | 1000        | 7            | 0.0%    | 0.031702     |
| difflib     | 100         | 100         | 7            | 0.0%    | 0.032328     |
| difflib     | 100         | 1000        | 7            | 0.0%    | 0.309274     | <!-- Baseline for exact match comparison -->
| difflib     | 100         | 5000        | 7            | 0.0%    | 1.575112     |
| difflib     | 500         | 1000        | 7            | 0.0%    | 1.577692     |
| difflib     | 100         | 1000        | 3            | 0.0%    | 0.140131     |
| difflib     | 100         | 1000        | 10           | 0.0%    | 0.392606     |
| difflib     | 100         | 1000        | 15           | 0.0%    | 0.549253     |
| difflib     | 100         | 1000        | 7            | 0.0%    | 0.317895     | <!-- Repeated baseline for exact match series -->
| difflib     | 100         | 1000        | 7            | 10.0%   | 0.287208     |
| difflib     | 100         | 1000        | 7            | 50.0%   | 0.155853     |
| difflib     | 100         | 1000        | 7            | 90.0%   | 0.031734     |
| difflib     | 100         | 1000        | 7            | 100.0%  | 0.000068     |
| **rapidfuzz**|            |             |              |         |              |
| rapidfuzz   | 10          | 100         | 7            | 0.0%    | 0.001638     |
| rapidfuzz   | 10          | 1000        | 7            | 0.0%    | 0.009749     |
| rapidfuzz   | 100         | 100         | 7            | 0.0%    | 0.010175     |
| rapidfuzz   | 100         | 1000        | 7            | 0.0%    | 0.093841     | <!-- Baseline for exact match comparison -->
| rapidfuzz   | 100         | 5000        | 7            | 0.0%    | 0.455255     |
| rapidfuzz   | 500         | 1000        | 7            | 0.0%    | 0.469044     |
| rapidfuzz   | 100         | 1000        | 3            | 0.0%    | 0.055951     |
| rapidfuzz   | 100         | 1000        | 10           | 0.0%    | 0.087346     |
| rapidfuzz   | 100         | 1000        | 15           | 0.0%    | 0.080194     |
| rapidfuzz   | 100         | 1000        | 7            | 0.0%    | 0.094612     | <!-- Repeated baseline for exact match series -->
| rapidfuzz   | 100         | 1000        | 7            | 10.0%   | 0.083930     |
| rapidfuzz   | 100         | 1000        | 7            | 50.0%   | 0.046490     |
| rapidfuzz   | 100         | 1000        | 7            | 90.0%   | 0.009657     |
| rapidfuzz   | 100         | 1000        | 7            | 100.0%  | 0.000079     |

## Analysis & Comparison

-   **Overall Speed (`rapidfuzz` vs `difflib`):** Consistent with previous findings, `rapidfuzz` significantly outperforms `difflib` when no exact matches are present (0% exact). The speedup factor for purely fuzzy matching generally ranges from **2.8x to 7x**.
-   **Impact of "Exact Match First" Optimization:**
    -   This optimization provides substantial performance improvements for both `difflib` and `rapidfuzz` implementations.
    -   The improvement is directly proportional to the percentage of target words that have exact matches in the choice list.
    -   For the (100 targets, 1000 choices, 7 avg_word_len) configuration:
        -   At 50% exact matches, both functions are approximately **2x faster** than their 0% exact match baseline.
        -   At 90% exact matches, both functions are approximately **10x faster** than their 0% exact match baseline.
        -   At 100% exact matches, the execution time becomes negligible (around 0.07-0.08 milliseconds), as it's dominated by set lookups. This represents a speedup of over **1000-4000x** compared to the 0% exact match scenario for the same configuration.
-   **Scaling with List Sizes (N, M) and Word Length (L):** The general scaling trends observed previously (linear with N and M, super-linear with L for the fuzzy part) still hold for the portions of the workload that require fuzzy matching. The exact match optimization effectively reduces the number of words that undergo this more expensive fuzzy matching process.
-   **Constant Factors:** `rapidfuzz` maintains its advantage due to smaller constant factors in its fuzzy matching logic, even when the "exact match first" optimization is applied to both.

## Conclusion & Recommendations

-   The **"Exact Match First" optimization** is highly beneficial and is now standard in all matching functions.
-   For applications requiring efficient word matching, **`find_closest_matches_rapidfuzz` remains strongly recommended** due to its superior performance in the fuzzy matching component.
-   If a high percentage of exact matches is anticipated in the input data, users can expect even greater performance from both functions, with `rapidfuzz` still being faster if any fuzzy matching is required.
-   The `find_closest_matches` function (using `difflib`) is more significantly impacted by the "exact match first" optimization in terms of raw time saved (because its fuzzy matching is slower), but `rapidfuzz` still provides the fastest overall solution.

Consider the expected rate of exact matches and the overall dataset characteristics when evaluating performance. For all but the smallest tasks, or where exact matches are rare, `rapidfuzz` will likely provide a noticeably better user experience.
