from unittest import TestCase

import pytest

from grapheme.api import graphemes


class CustomGraphemesCases(TestCase):
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

    def test_three_picto_joined(self):
        # from https://github.com/timendum/grapheme/issues/4
        base_str = "\U0001f469\u200d\U0001f469\u200d\U0001f467"
        self.assertEqual(list(graphemes(base_str)), [base_str])
        extra_str = "aa\n"
        self.assertEqual(list(graphemes(extra_str)), list(extra_str))
        input_str = extra_str + base_str
        self.assertEqual(list(graphemes(input_str)), list(extra_str) + [base_str])


if __name__ == "__main__":
    pytest.main()
