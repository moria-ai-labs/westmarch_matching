import difflib

def find_closest_matches(target_list: list[str], choice_list: list[str]) -> dict[str, str | None]:
    """
    Finds the closest match in choice_list for each word in target_list.

    Args:
        target_list: A list of words to find matches for.
        choice_list: A list of words to choose from.

    Returns:
        A dictionary where keys are words from target_list and
        values are their closest matches from choice_list.
        If no suitable match is found for a target word (e.g., choice_list is empty
        or no word is close enough based on difflib's cutoff),
        the value will be None.
    """
    matches = {}
    if not choice_list: # If choice_list is empty, no matches can be found
        for target_word in target_list:
            matches[target_word] = None
        return matches

    # Convert choice_list to a set for efficient exact match lookups
    choice_set = set(choice_list)

    for target_word in target_list:
        # Step 1: Check for an exact match
        if target_word in choice_set:
            matches[target_word] = target_word
            continue # Move to the next target word

        # Step 2: If no exact match, proceed with fuzzy matching
        # difflib.get_close_matches returns a list of good matches.
        # We take the first one if the list is not empty, otherwise None.
        # The `n=1` argument means we want at most 1 match.
        # The `cutoff` argument (default 0.6) determines how similar words must be.
        # We can adjust this cutoff if needed.
        close_matches = difflib.get_close_matches(target_word, choice_list, n=1, cutoff=0.6)
        if close_matches:
            matches[target_word] = close_matches[0]
        else:
            matches[target_word] = None
    return matches


from rapidfuzz import process, fuzz

def find_closest_matches_rapidfuzz(target_list: list[str], choice_list: list[str], score_cutoff: float = 60.0) -> dict[str, str | None]:
    """
    Finds the closest match in choice_list for each word in target_list using RapidFuzz.

    Args:
        target_list: A list of words to find matches for.
        choice_list: A list of words to choose from.
        score_cutoff: A score (0-100) below which matches are considered not close enough.
                      Defaults to 60, analogous to difflib's 0.6.

    Returns:
        A dictionary where keys are words from target_list and
        values are their closest matches from choice_list.
        If no suitable match is found, the value will be None.
    """
    matches = {}
    if not choice_list: # If choice_list is empty, no matches can be found
        for target_word in target_list:
            matches[target_word] = None
        return matches

    # Convert choice_list to a set for efficient exact match lookups
    choice_set = set(choice_list)

    for target_word in target_list:
        # Step 1: Check for an exact match
        if target_word in choice_set:
            matches[target_word] = target_word
            continue # Move to the next target word

        # Step 2: If no exact match, proceed with fuzzy matching
        # process.extractOne returns a tuple (choice, score, index) or None
        # We use WRatio as it's often a good general-purpose ratio.
        # Other scorers like fuzz.ratio, fuzz.partial_ratio could also be used.
        result = process.extractOne(
            target_word,
            choice_list,
            scorer=fuzz.WRatio, # Weighted Ratio, good for different length strings
            score_cutoff=score_cutoff
        )
        if result:
            matches[target_word] = result[0] # result[0] is the best choice string
        else:
            matches[target_word] = None
    return matches


def find_closest_matches_rapidfuzz_len_filter(
    target_list: list[str],
    choice_list: list[str],
    score_cutoff: float = 60.0,
    length_delta: int = 3
) -> dict[str, str | None]:
    """
    Finds the closest match in choice_list for each word in target_list using RapidFuzz,
    with an additional optimization to pre-filter choices by word length.

    Args:
        target_list: A list of words to find matches for.
        choice_list: A list of words to choose from.
        score_cutoff: A score (0-100) below which matches are considered not close enough.
        length_delta: Consider choice words whose length is target_word_length +/- length_delta.

    Returns:
        A dictionary where keys are words from target_list and
        values are their closest matches from choice_list.
    """
    matches = {}
    if not choice_list:
        for target_word in target_list:
            matches[target_word] = None
        return matches

    choice_set = set(choice_list)

    for target_word in target_list:
        if target_word in choice_set:
            matches[target_word] = target_word
            continue

        target_len = len(target_word)
        min_len = max(1, target_len - length_delta)
        max_len = target_len + length_delta

        # Filter choice_list by length
        # Note: This creates a new list in each iteration for the target_word.
        # If choice_list is very large, pre-bucketing choices by length once
        # at the start could be more efficient. For now, this direct filtering is simpler.
        filtered_choices = [
            choice for choice in choice_list if min_len <= len(choice) <= max_len
        ]

        if not filtered_choices:
            matches[target_word] = None
            continue

        result = process.extractOne(
            target_word,
            filtered_choices, # Use the length-filtered list
            scorer=fuzz.WRatio,
            score_cutoff=score_cutoff
        )
        if result:
            matches[target_word] = result[0]
        else:
            matches[target_word] = None
    return matches


if __name__ == '__main__':
    # Example Usage
    target_words = ["apple", "banan", "grappe", "orangg", "kiwi"]
    choice_words = ["apricot", "banana", "grape", "orange", "pear", "kiwano"]

    closest_matches = find_closest_matches(target_words, choice_words)
    print("Finding matches for:", target_words)
    print("From choices:", choice_words)
    print("Closest matches found:")
    for target, match in closest_matches.items():
        print(f"  '{target}' -> '{match}'")

    print("\nExample with an empty choice list:")
    target_words_2 = ["hello", "world"]
    choice_words_2 = []
    closest_matches_2 = find_closest_matches(target_words_2, choice_words_2)
    for target, match in closest_matches_2.items():
        print(f"  '{target}' -> '{match}'")

    print("\nExample with no close matches:")
    target_words_3 = ["xyz", "abc"]
    choice_words_3 = ["apple", "banana", "grape"]
    closest_matches_3 = find_closest_matches(target_words_3, choice_words_3)
    for target, match in closest_matches_3.items():
        print(f"  '{target}' -> '{match}'")
