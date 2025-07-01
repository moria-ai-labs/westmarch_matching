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

-   **Algorithm:** After an exact match check, for each of N target words, iterates through M choice words. Similarity is calculated using `difflib.SequenceMatcher.ratio()`.
-   **Time Complexity:** Approximately **`O(N * M * L^2)`** for the fuzzy matching part. The exact match check is `O(M)` setup (for set creation) + `N * O(L_avg)` on average for lookups.
-   **Space Complexity:** Approximately **`O(M*L + N*L + L^2)`**. `M*L` for the choice set, `N*L` for results, `L^2` for `SequenceMatcher`.

### 2. `find_closest_matches_rapidfuzz` (using `rapidfuzz`)

-   **Algorithm:** After an exact match check, for each of N target words, uses `rapidfuzz.process.extractOne` to find the best match from M choice words. The scorer used is `rapidfuzz.fuzz.WRatio`.
-   **Time Complexity:** Approximately **`O(N * M * L^2)`** for the fuzzy matching part (with smaller constant factors than `difflib`). Exact match check is efficient.
-   **Space Complexity:** Approximately **`O(M*L + N*L + L_min)`**.

### 3. `find_closest_matches_rapidfuzz_len_filter` (using `rapidfuzz` with length filtering)

-   **Algorithm:** Extends `find_closest_matches_rapidfuzz`. After the exact match check, it further filters the `choice_list` for each target word to include only choices with lengths close to the target word's length (target_length +/- `length_delta`). Then, `rapidfuzz.process.extractOne` operates on this smaller, length-filtered list.
-   **Time Complexity:** The fuzzy matching part becomes approximately **`O(N * M' * L^2)`**, where `M'` is the average size of the length-filtered choice list (`M' <= M`). The filtering step itself takes `O(M*L_avg_choice_word)` for each target word if re-filtering the original list each time, or `O(M)` if choices are pre-bucketed by length (not current implementation for simplicity). The current implementation is `O(N * M * L_avg_choice_word)` for filtering in total if not pre-bucketed, plus `O(N * M' * L^2)` for fuzzy matching. If `M'` is significantly smaller than `M`, this can lead to substantial speedups.
-   **Space Complexity:** Similar to `rapidfuzz` version, plus space for the temporary `filtered_choices` list (up to `O(M*L)` in worst case if no filtering occurs, but typically smaller `O(M'*L)`). So, approximately **`O(M*L + N*L + L_min)`**.

## Benchmark Setup

-   **Script:** `benchmarks/benchmark_matcher.py`
-   **Tool:** Python's `timeit` module for accurate time measurements.
-   **Method:** Randomly generated word lists were used for `target_list` and `choice_list` based on specified sizes and average word lengths. Each configuration was run multiple times (`num_benchmark_runs = 3`) and the average time was reported.
-   **Environment:** Standard Python environment with necessary libraries (`difflib` from standard library, `rapidfuzz` installed via pip).

## Benchmark Results

The following table shows the average execution time in seconds for various configurations. `Tgt Var` and `Cho Var` refer to the length variance (+/-) for target and choice words, respectively. The `rapidfuzz_len_filter` uses a `length_delta=3`.

*(Scroll right to see all columns for the full table)*
```
Function               | Target List  | Choice List  | Avg Word Len | Exact %  | Tgt Var | Cho Var | Avg Time (s)
-----------------------------------------------------------------------------------------------------------------------------
difflib                | 10           | 100          | 7            | 0.0    % | 2       | 2       | 0.003419
difflib                | 10           | 100          | 7            | 10.0   % | 2       | 2       | 0.003235
difflib                | 10           | 1000         | 7            | 0.0    % | 2       | 2       | 0.032630
difflib                | 100          | 100          | 7            | 0.0    % | 2       | 2       | 0.032220
difflib                | 100          | 100          | 7            | 10.0   % | 2       | 2       | 0.030442
difflib                | 10           | 1000         | 7            | 10.0   % | 2       | 2       | 0.029386
difflib                | 100          | 1000         | 3            | 0.0    % | 2       | 2       | 0.142941
difflib                | 100          | 1000         | 10           | 0.0    % | 2       | 2       | 0.404527
difflib                | 100          | 1000         | 7            | 0.0    % | 2       | 2       | 0.320285
difflib                | 100          | 1000         | 15           | 0.0    % | 2       | 2       | 0.591195
difflib                | 100          | 1000         | 10           | 0.0    % | 2       | 7       | 0.381886
difflib                | 100          | 1000         | 7            | 10.0   % | 2       | 2       | 0.297851
difflib                | 100          | 1000         | 7            | 50.0   % | 2       | 2       | 0.164163
difflib                | 100          | 1000         | 7            | 90.0   % | 2       | 2       | 0.032919
difflib                | 100          | 1000         | 7            | 100.0  % | 2       | 2       | 0.000106
difflib                | 500          | 1000         | 7            | 0.0    % | 2       | 2       | 1.647267
difflib                | 100          | 5000         | 7            | 0.0    % | 2       | 2       | 1.621984
difflib                | 500          | 1000         | 7            | 10.0   % | 2       | 2       | 1.429129
difflib                | 100          | 5000         | 7            | 10.0   % | 2       | 2       | 1.444357
rapidfuzz              | 10           | 100          | 7            | 0.0    % | 2       | 2       | 0.001655
rapidfuzz              | 10           | 100          | 7            | 10.0   % | 2       | 2       | 0.000878
rapidfuzz              | 10           | 1000         | 7            | 0.0    % | 2       | 2       | 0.009073
rapidfuzz              | 100          | 100          | 7            | 0.0    % | 2       | 2       | 0.009722
rapidfuzz              | 100          | 100          | 7            | 10.0   % | 2       | 2       | 0.008993
rapidfuzz              | 10           | 1000         | 7            | 10.0   % | 2       | 2       | 0.008023
rapidfuzz              | 100          | 1000         | 3            | 0.0    % | 2       | 2       | 0.048461
rapidfuzz              | 100          | 1000         | 10           | 0.0    % | 2       | 2       | 0.083387
rapidfuzz              | 100          | 1000         | 7            | 0.0    % | 2       | 2       | 0.091978
rapidfuzz              | 100          | 1000         | 15           | 0.0    % | 2       | 2       | 0.079011
rapidfuzz              | 100          | 1000         | 10           | 0.0    % | 2       | 7       | 0.121184
rapidfuzz              | 100          | 1000         | 7            | 10.0   % | 2       | 2       | 0.081906
rapidfuzz              | 100          | 1000         | 7            | 50.0   % | 2       | 2       | 0.045088
rapidfuzz              | 100          | 1000         | 7            | 90.0   % | 2       | 2       | 0.008659
rapidfuzz              | 100          | 1000         | 7            | 100.0  % | 2       | 2       | 0.000068
rapidfuzz              | 500          | 1000         | 7            | 0.0    % | 2       | 2       | 0.456194
rapidfuzz              | 100          | 5000         | 7            | 0.0    % | 2       | 2       | 0.455908
rapidfuzz              | 500          | 1000         | 7            | 10.0   % | 2       | 2       | 0.411390
rapidfuzz              | 100          | 5000         | 7            | 10.0   % | 2       | 2       | 0.422204
rapidfuzz_len_filter   | 10           | 100          | 7            | 0.0    % | 2       | 2       | 0.000947
rapidfuzz_len_filter   | 10           | 100          | 7            | 10.0   % | 2       | 2       | 0.000895
rapidfuzz_len_filter   | 10           | 1000         | 7            | 0.0    % | 2       | 2       | 0.009060
rapidfuzz_len_filter   | 100          | 100          | 7            | 0.0    % | 2       | 2       | 0.009814
rapidfuzz_len_filter   | 100          | 100          | 7            | 10.0   % | 2       | 2       | 0.008529
rapidfuzz_len_filter   | 10           | 1000         | 7            | 10.0   % | 2       | 2       | 0.007822
rapidfuzz_len_filter   | 100          | 1000         | 3            | 0.0    % | 2       | 2       | 0.059761
rapidfuzz_len_filter   | 100          | 1000         | 10           | 0.0    % | 2       | 2       | 0.079349
rapidfuzz_len_filter   | 100          | 1000         | 7            | 0.0    % | 2       | 2       | 0.088997
rapidfuzz_len_filter   | 100          | 1000         | 15           | 0.0    % | 2       | 2       | 0.083153
rapidfuzz_len_filter   | 100          | 1000         | 10           | 0.0    % | 2       | 7       | 0.046117
rapidfuzz_len_filter   | 100          | 1000         | 7            | 10.0   % | 2       | 2       | 0.078450
rapidfuzz_len_filter   | 100          | 1000         | 7            | 50.0   % | 2       | 2       | 0.044059
rapidfuzz_len_filter   | 100          | 1000         | 7            | 90.0   % | 2       | 2       | 0.009206
rapidfuzz_len_filter   | 100          | 1000         | 7            | 100.0  % | 2       | 2       | 0.000069
rapidfuzz_len_filter   | 500          | 1000         | 7            | 0.0    % | 2       | 2       | 0.433032
rapidfuzz_len_filter   | 100          | 5000         | 7            | 0.0    % | 2       | 2       | 0.430119
rapidfuzz_len_filter   | 500          | 1000         | 7            | 10.0   % | 2       | 2       | 0.391262
rapidfuzz_len_filter   | 100          | 5000         | 7            | 10.0   % | 2       | 2       | 0.389610
```

## Analysis & Comparison

 -   **Overall Speed (`rapidfuzz` vs `difflib`):** Consistent with previous findings, `rapidfuzz` significantly outperforms `difflib` when no exact matches are present (0% exact). The speedup factor for purely fuzzy matching generally ranges from **2.8x to 7x**.
 -   **Impact of "Exact Match First" Optimization:**
     -   This optimization provides substantial performance improvements for all implementations.
     -   The improvement is directly proportional to the percentage of target words that have exact matches in the choice list.
     -   At 100% exact matches, execution time becomes negligible for all methods.
 -   **Impact of "Length Filtering" (`rapidfuzz_len_filter` vs `rapidfuzz`):**
    -   **Low Choice Variance (Cho Var = 2):** When word lengths in `choice_list` are fairly uniform, `rapidfuzz_len_filter` offers a small additional speedup (e.g., ~3-5% faster for (100,1000,7,0%) and (100,5000,7,0%)). In some cases (e.g., (100,1000,15,0%)), it can be slightly slower, possibly due to the overhead of list filtering not being offset if few words are filtered out.
    -   **High Choice Variance (Cho Var = 7):** For the configuration (100 targets, 1000 choices, avg_word_len 10, 0% exact, TgtVar 2, ChoVar 7), the length filtering shows its strength:
        -   `rapidfuzz`: 0.121184 s
        -   `rapidfuzz_len_filter`: 0.046117 s (This is **~2.63x faster** than `rapidfuzz` without length filtering).
 -   **Scaling with List Sizes (N, M) and Word Length (L):** The general scaling trends observed previously (linear with N and M, super-linear with L for the fuzzy part) still hold for the portions of the workload that require fuzzy matching. The optimizations (exact match, length filtering) effectively reduce the number of words or pairs that undergo the most expensive fuzzy matching steps.
 -   **Constant Factors:** `rapidfuzz` maintains its advantage due to smaller constant factors in its fuzzy matching logic.

## Conclusion & Recommendations

 -   The **"Exact Match First" optimization** is highly beneficial and is standard in all matching functions.
 -   **`find_closest_matches_rapidfuzz_len_filter` is the recommended function for general use**, especially if the `choice_list` might contain words of widely varying lengths. It provides the best performance in such scenarios and a modest improvement or similar performance to `find_closest_matches_rapidfuzz` otherwise.
 -   If `choice_list` words are known to be very uniform in length and near the target word lengths, `find_closest_matches_rapidfuzz` might be marginally faster by avoiding the filtering overhead, but the difference is often small.
 -   `find_closest_matches` (using `difflib`) is the slowest but remains an option if avoiding C-dependencies (brought by `rapidfuzz`) is an absolute necessity.

Consider the expected rate of exact matches and the overall dataset characteristics, especially choice word length variance, when evaluating performance.
