import bisect
import json
import os
import string
from collections.abc import Callable
from enum import Enum
from typing import TypeVar


class GraphemePropertyGroup(Enum):
    PREPEND = "Prepend"
    CR = "CR"
    LF = "LF"
    CONTROL = "Control"
    EXTEND = "Extend"
    REGIONAL_INDICATOR = "Regional_Indicator"
    SPACING_MARK = "SpacingMark"
    L = "L"
    V = "V"
    T = "T"
    LV = "LV"
    LVT = "LVT"
    ZWJ = "ZWJ"
    EXTENDED_PICTOGRAPHIC = "Extended_Pictographic"

    OTHER = "Other"


COMMON_OTHER_GROUP_CHARS = ""
RANGE_TREE: tuple[list[int], list[tuple[int, int, GraphemePropertyGroup]]] = ([], [])
SINGLE_CHAR_MAPPINGS = dict[int, GraphemePropertyGroup]()


def get_group(char: str) -> GraphemePropertyGroup:
    if char in COMMON_OTHER_GROUP_CHARS:
        return GraphemePropertyGroup.OTHER
    else:
        return get_group_ord(ord(char))


def get_group_ord(char: int) -> GraphemePropertyGroup:
    group = SINGLE_CHAR_MAPPINGS.get(char, None)
    if group:
        return group

    # Find the rightmost interval whose min <= x
    i = bisect.bisect_right(RANGE_TREE[0], char) - 1
    if i >= 0 and RANGE_TREE[1][i][0] <= char <= RANGE_TREE[1][i][1]:
        return RANGE_TREE[1][i][2]
    return GraphemePropertyGroup.OTHER


T = TypeVar("T", bound=Enum, contravariant=True)


def load_file(
    filename: str, enumgroup: type[T]
) -> tuple[dict[int, T], tuple[list[int], list[tuple[int, int, T]]]]:
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        data = json.load(f)

    assert len(data) == len(enumgroup) - 1

    single_char_mappings: dict[int, T] = {}
    for key, value in data.items():
        group = enumgroup(key)
        for char in value["single_chars"]:
            single_char_mappings[char] = group

    raw_ranges: list[tuple[int, int, T]] = []
    # range_list is a list of [(min, max, group)]
    for key, value in data.items():
        for range_ in value["ranges"]:
            min_: int = range_[0]
            max_: int = range_[1]
            group = enumgroup(key)
            if max_ - min_ < 20:
                for i in range(min_, max_ + 1):
                    single_char_mappings[i] = group
                continue
            raw_ranges.append((min_, max_, group))
    raw_ranges.sort(key=lambda key: key[0])
    del data

    return (single_char_mappings, ([a[0] for a in raw_ranges], raw_ranges))


def generate_common(e_get_group_ord: Callable[[int], T], enumgroup: type[T]) -> str:
    common_ascii = string.ascii_letters + string.digits + string.punctuation + " "
    common_other_group_chars = "".join(
        c for c in common_ascii if (e_get_group_ord(ord(c))) == enumgroup("Other")
    )
    return common_other_group_chars


SINGLE_CHAR_MAPPINGS, RANGE_TREE = load_file(
    "data/grapheme_break_property.json", GraphemePropertyGroup
)

COMMON_OTHER_GROUP_CHARS = generate_common(get_group_ord, GraphemePropertyGroup)
