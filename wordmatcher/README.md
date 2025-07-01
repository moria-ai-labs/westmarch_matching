# WordMatcher

WordMatcher is a Python library designed to efficiently find the closest match for a given set of words from a predefined list of choices. For each word in a target list, it identifies the most similar word in a choice list.

## Features

-   Fast and efficient matching.
-   Easy to integrate into Python projects.
-   Uses well-known string similarity algorithms.

## Installation

```bash
pip install wordmatcher
```
This will install the package along with `rapidfuzz`, which is used by the recommended high-performance matching function.

## Usage

WordMatcher provides two functions for finding closest matches:

1.  `find_closest_matches_rapidfuzz(target_list, choice_list, score_cutoff=60.0)`:
    *   **Recommended for most uses due to significantly better performance.**
    *   Uses the `rapidfuzz` library.
    *   `score_cutoff` is on a 0-100 scale (default 60 is similar to `difflib`'s 0.6).
    *   Includes an "exact match first" optimization: if a target word is found exactly in the choice list, that match is returned immediately, skipping fuzzy matching for that word.

2.  `find_closest_matches(target_list, choice_list)`:
    *   Uses Python's built-in `difflib`.
    *   Slower, but has no external C dependencies beyond what `pip` might pull for `rapidfuzz` if installed.
    *   Also includes the "exact match first" optimization.

**Example using `rapidfuzz` (recommended):**
```python
from wordmatcher import find_closest_matches_rapidfuzz

target_words = ["apple", "banan", "grappe"]
choice_words = ["apricot", "banana", "grape", "orange", "pear"]

# Using a cutoff of 60 (similar to difflib's 0.6)
matches = find_closest_matches_rapidfuzz(target_words, choice_words, score_cutoff=60)
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

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```
