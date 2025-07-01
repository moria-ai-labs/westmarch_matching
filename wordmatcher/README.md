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

## Usage

```python
from wordmatcher import find_closest_matches

target_words = ["apple", "banan", "grappe"]
choice_words = ["apricot", "banana", "grape", "orange", "pear"]

matches = find_closest_matches(target_words, choice_words)
print(matches)
# Expected output (will depend on the matching algorithm):
# {'apple': 'apricot', 'banan': 'banana', 'grappe': 'grape'}
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
```
