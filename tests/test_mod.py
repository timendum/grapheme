from unittest import TestCase

import pytest

import grapheme
from grapheme.grapheme_property_group import GraphemePropertyGroup, get_group


class GetGroupTest(TestCase):
    def test_get_group_prepend(self):
        self.assertEqual(get_group("\u0605"), GraphemePropertyGroup.PREPEND)

    def test_get_group_cr(self):
        self.assertEqual(get_group("\u000d"), GraphemePropertyGroup.CR)

    def test_get_group_lf(self):
        self.assertEqual(get_group("\u000a"), GraphemePropertyGroup.LF)

    def test_get_group(self):
        self.assertEqual(get_group("s"), GraphemePropertyGroup.OTHER)


class GraphemesTest(TestCase):
    def test_empty(self):
        self.assertEqual(list(grapheme.graphemes("")), [])

    def test_simple(self):
        self.assertEqual(list(grapheme.graphemes("alvin")), list("alvin"))

    def test_emoji_with_modifier(self):
        input_str = "\U0001f476\U0001f3fb"
        self.assertEqual(list(grapheme.graphemes(input_str)), [input_str])

    def test_cr_lf(self):
        self.assertEqual(list(grapheme.graphemes("\u000d\u000a")), ["\u000d\u000a"])

    def test_mixed_text(self):
        input_str = " \U0001f476\U0001f3fb ascii \u000d\u000a"
        graphemes = [
            " ",
            "\U0001f476\U0001f3fb",
            " ",
            "a",
            "s",
            "c",
            "i",
            "i",
            " ",
            input_str[-2:],
        ]
        self.assertEqual(list(grapheme.graphemes(input_str)), graphemes)
        self.assertEqual(list(grapheme.grapheme_lengths(input_str)), [len(g) for g in graphemes])
        self.assertEqual(grapheme.slice(input_str, 0, 2), " \U0001f476\U0001f3fb")
        self.assertEqual(grapheme.slice(input_str, 0, 3), " \U0001f476\U0001f3fb ")
        self.assertEqual(grapheme.slice(input_str, end=3), " \U0001f476\U0001f3fb ")
        self.assertEqual(grapheme.slice(input_str, 1, 4), "\U0001f476\U0001f3fb a")
        self.assertEqual(grapheme.slice(input_str, 2), input_str[3:])
        self.assertEqual(grapheme.slice(input_str, 2, 4), " a")
        self.assertEqual(grapheme.length(input_str), 10)
        self.assertEqual(grapheme.length(input_str, until=0), 0)
        self.assertEqual(grapheme.length(input_str, until=1), 1)
        self.assertEqual(grapheme.length(input_str, until=4), 4)
        self.assertEqual(grapheme.length(input_str, until=10), 10)
        self.assertEqual(grapheme.length(input_str, until=11), 10)

    def test_contains(self):
        input_str = " \U0001f476\U0001f3fb ascii \u000d\u000a"

        self.assertFalse(grapheme.contains(input_str, " \U0001f476"))
        self.assertFalse(grapheme.contains(input_str, "\u000d"))
        self.assertFalse(grapheme.contains(input_str, "\U0001f3fb"))
        self.assertTrue(grapheme.contains(input_str, ""))

        graphemes = list(grapheme.graphemes(input_str))
        for grapheme_ in graphemes:
            self.assertTrue(grapheme.contains(input_str, grapheme_))

        for i in range(len(graphemes) - 1):
            self.assertTrue(grapheme.contains(input_str, "".join(graphemes[i : i + 2])))


if __name__ == "__main__":
    pytest.main()
