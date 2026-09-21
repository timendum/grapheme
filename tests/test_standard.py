import os

import pytest

import grapheme
from grapheme.api import safe_split_index


def read_test_data():
    test_cases = []
    with open(
        os.path.join(os.path.dirname(__file__), "../unicode-data/GraphemeBreakTest.txt"),
    ) as f:
        for line in f.readlines():
            if line.startswith("#"):
                continue

            test_data, description = line.split("#")

            expected_graphemes = [
                "".join([chr(int(char, 16)) for char in cluster.split("×") if char.strip()])
                for cluster in test_data.split("÷")
                if cluster.strip()
            ]

            input_string = "".join(expected_graphemes)
            test_cases.append((input_string, expected_graphemes, description))
    return test_cases


TEST_CASES = read_test_data()


@pytest.mark.parametrize("input_string,expected_graphemes,description", TEST_CASES)
def test_default_grapheme_suit(input_string, expected_graphemes, description):
    assert list(grapheme.graphemes(input_string)) == expected_graphemes
    assert grapheme.length(input_string) == len(expected_graphemes)


@pytest.mark.parametrize("input_string,expected_graphemes,description", TEST_CASES)
def test_safe_split_index(input_string, expected_graphemes, description):
    # Verify that we can always find the last grapheme index
    cur_len = 0
    cur_grapheme_break_index = 0
    for g in expected_graphemes:
        next_limit = cur_grapheme_break_index + len(g)
        for _c in g:
            cur_len += 1
            if cur_len == next_limit:
                cur_grapheme_break_index = next_limit
            assert safe_split_index(input_string, cur_len) == cur_grapheme_break_index


@pytest.mark.parametrize("input_string,expected_graphemes,description", TEST_CASES)
def test_prefixes(input_string, expected_graphemes, description):
    prefix = ""
    allowed_prefixes = [prefix]
    for g in expected_graphemes:
        prefix += g
        allowed_prefixes.append(prefix)

    for i in range(len(input_string)):
        prefix = input_string[:i]
        assert grapheme.startswith(input_string, prefix) == (prefix in allowed_prefixes)


@pytest.mark.parametrize("input_string,expected_graphemes,description", TEST_CASES)
def test_suffixes(input_string, expected_graphemes, description):
    suffix = ""
    allowed_suffixes = [suffix]
    for g in reversed(expected_graphemes):
        suffix = g + suffix
        allowed_suffixes.append(suffix)

    for i in range(len(input_string)):
        suffix = input_string[i:]
        assert grapheme.endswith(input_string, suffix) == (suffix in allowed_suffixes)


@pytest.mark.parametrize("input_string,expected_graphemes,description", TEST_CASES)
def test_index(input_string, expected_graphemes, description):
    seen = set()
    for idx, expected_grapheme in enumerate(expected_graphemes):
        if expected_grapheme in seen:
            continue
        found_idx = grapheme.index(input_string, expected_grapheme)
        assert found_idx == idx, f"Failed to find {expected_grapheme} in {input_string} at {idx}"
        seen.add(expected_grapheme)


if __name__ == "__main__":
    pytest.main()
