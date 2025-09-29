## 0.8.1
Fix bug #4 found by alwaysmpe.
No API changes.

## 0.8.0
Added support for Unicode 17.
Changed supported python version. Now tested on python 3.8 - 3.13.

## 0.7.1
Fix bug #1 found by alwaysmpe.
No API changes.

## 0.7.0
Added support for Unicode 16.
Drops support for python 3.6. Now tested on python 3.7 - 3.12.
No API changes.

## 0.6.0
Added support for Unicode 13.

Drops support for python 3.4 & 3.5. Now tested on python 3.6 - 3.8.
No API changes

## 0.5.0
Added support for Unicode 12.

No API changes

## 0.4.0
Added support for Unicode 11.

Added `grapheme.UNICODE_VERSION`.

No other API changes

## 0.3.0
Added a few new functions:

* `grapheme.safe_split_index`, which can find the highest grapheme boundary index in a given string without traversing the full grapheme sequence.
* `grapheme.startswith`, which tests that a given string starts with the same grapheme sequence as a given prefix.
* `grapheme.endswith`, which tests that a given string ends with the same grapheme sequence as a given suffix.

## 0.2.1
Performance improvements

No new functionality, but noticably better performance.

## 0.2.0
* Adds `grapheme.contains`
* Bugfix for empty strings

## 0.1.0
Initial release

Basic support for getting graphemes, grapheme string lengths and grapheme based slicing.
