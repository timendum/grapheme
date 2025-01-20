from unittest import TestCase

import pytest

from grapheme.api import graphemes


class ResetStates(TestCase):
    def test_ascii_then_cblinker(self):
        # from https://github.com/timendum/grapheme/issues/1
        base_str = "\u0915\u093c\u200d\u094d\u0924"
        self.assertEqual(list(graphemes(base_str)), [base_str])
        extra_str = "aa"
        self.assertEqual(list(graphemes(extra_str)), list(extra_str))
        input_str = extra_str + base_str
        self.assertEqual(list(graphemes(input_str)), list(extra_str) + [base_str])

    def test_ascii_cr_then_cblinker(self):
        # from https://github.com/timendum/grapheme/issues/2
        base_str = "\u0915\u093c\u200d\u094d\u0924"
        self.assertEqual(list(graphemes(base_str)), [base_str])
        extra_str = "aa\n"
        self.assertEqual(list(graphemes(extra_str)), list(extra_str))
        input_str = extra_str + base_str
        self.assertEqual(list(graphemes(input_str)), list(extra_str) + [base_str])


if __name__ == "__main__":
    pytest.main()
