grapheme
========

A Python package for working with user perceived characters. More specifically,
string manipulation and calculation functions for working with grapheme cluster
groups (graphemes) as defined by the `Unicode Standard Annex #29 <http://unicode.org/reports/tr29/>`_.

`documentation <https://graphemeu.readthedocs.io/>`_

.. code-block:: console

    pip install graphemeu

Or similar.

The currently supported version of Unicode: 16.0.0.

This package is a fork of `grapheme <https://github.com/alvinlindstam/grapheme>`_ by Alvin Lindstam.

What? Why?
==========

Unicode strings are made up of a series of unicode characters, but a unicode character does not
always map to a user perceived character. Some human perceived characters are represented as two
or more unicode characters.

However, all built in python string functions and string methods work with single unicode characters
without considering their connection to each other.

.. code-block:: python

    >>> string = 'u̲n̲d̲e̲r̲l̲i̲n̲e̲d̲'
    >>> len(string)
    20
    >>> grapheme.length(string)
    10
    >>> string[:3]
    'u̲n'
    >>> grapheme.slice(string, 0, 3)
    'u̲n̲d̲'

This library implements the unicode default rules for extended grapheme clusters, and provides
a set of functions for string manipulation based on graphemes.

Documentation
=============

See `<https://graphemeu.readthedocs.io/en/latest/>`_.

When should I consider graphemes instead of unicode characters?
===============================================================

You should consider working with graphemes over unicode code points when:

* You wish to count characters as perceived by users.
* You wish to split or truncate text at some user perceived lengths.
* You wish to split or truncate text without risk of corrupting the characters.
* Formatting text by length, such as creating text based tables in monospaced fonts

You should work with normal python string functions when:

* You wish to count or split by unicode codepoints for compliance with storage
  limitations (such as database maximum length)
* When working with systems that put limits on strings by unicode character
  lengths
* When you prioritize performance over correctness (see performance notes below)
* When working with very long strings (see performance notes below)
* If simplicity is more important than accuracy

Performance
===========

Calculating graphemes require traversing the string and checking each character
against a set of rules and the previous character(s). Because of this, all
functions in this module will scale linearly to the string length.

Whenever possible, they will only traverse the string for as long as needed and return
early as soon as the requested output is generated. For example, the `grapheme.slice`
function only has to traverse the string until the last requested grapheme is found, and
does not care about the rest of the string.

You should probably only use this package for testing/manipulating fairly short strings
or with the beginning of long strings.

When testing with a string of 10 000 ascii characters, and a 3.1 GHz processor, the execution
time for some possible calls is roughly:

================================================================  ==========================
Code                                                              Approximate execution time
================================================================  ==========================
`len(long_ascii_string)`                                          3.0e-10 seconds
`grapheme.length(long_ascii_string)`                              4.3e-05 seconds
`grapheme.length(long_ascii_string, 500)`                         2.6e-06 seconds
`long_ascii_string[0:100]`                                        1.3e-09 seconds
`grapheme.slice(long_ascii_string, 0, 100)`                       6.3e-07 seconds
`long_ascii_string[:100] in long_ascii_string`                    7.8e-09 seconds
`grapheme.contains(long_ascii_string, long_ascii_string[:100])`   9.9e-07 seconds
`long_ascii_string[-100:] in long_ascii_string`                   2.0e-08 seconds
`grapheme.contains(long_ascii_string, long_ascii_string[-100:])`  6.9e-05 seconds
================================================================  ==========================

Execution times may improve in later releases, but calculating graphemes is and will continue
to be notably slower than just counting unicode code points.

Examples of grapheme cluster groups
===================================

This is not a complete list, but a some examples of when graphemes use multiple
characters:

* CR+LF
* Hangul (korean)
* Emoji with modifiers
* Combining marks
* Zero Width Join

Development quick start
=======================

If you wish to contribute or edit this package, create a fork and clone it.

Then install and run the tests.

.. code-block:: console

    uv run --extra dev -m pytest

For the documentation, use:

.. code-block:: console

    uv run --extra docs sphinx-autobuild docs dist/www

Unicode version upgrade
-----------------------

The library will issue a new release for each new unicode version.

The steps necessary for this:

1. Verify that there has been no material changes to the rulesets in Unicode
   `Annex #29 <http://unicode.org/reports/tr29/>`_ (see modifications).
2. Download the `data files <http://www.unicode.org/Public/>`_ from unicode into the unicode-data folder.
   For the given version, some are in `ucd` and some are in `ucd/auxiliary`.
3. Run `./unicode-data/read_property_file.py` to parse those files (will update the
   `grapheme_break_property.json` and `derived_core_property.json` files).
4. Update the unicode version in the documentation and in the source code.
5. Bump the version.
