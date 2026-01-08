import bisect
from enum import Enum
from functools import lru_cache

from grapheme.grapheme_property_group import generate_common, load_file


class InCBPropertyGroup(Enum):
    CONSONANT = "InCBConsonant"
    EXTEND = "InCBExtend"
    LINKER = "InCBLinker"

    OTHER = "Other"


COMMON_OTHER_GROUP_CHARS = ""
RANGE_TREE: tuple[list[int], list[tuple[int, int, InCBPropertyGroup]]] = ([], [])
SINGLE_CHAR_MAPPINGS = dict[int, InCBPropertyGroup]()


def get_group(char):
    if char in COMMON_OTHER_GROUP_CHARS:
        return InCBPropertyGroup.OTHER
    return get_group_ord(ord(char))


@lru_cache(128)
def get_group_ord(char):
    group = SINGLE_CHAR_MAPPINGS.get(char, None)
    if group:
        return group

    # Find the rightmost interval whose min <= x
    i = bisect.bisect_right(RANGE_TREE[0], char) - 1
    if i >= 0 and RANGE_TREE[1][i][0] <= char <= RANGE_TREE[1][i][1]:
        return RANGE_TREE[1][i][2]
    return InCBPropertyGroup.OTHER


SINGLE_CHAR_MAPPINGS, RANGE_TREE = load_file("data/derived_core_property.json", InCBPropertyGroup)

COMMON_OTHER_GROUP_CHARS = generate_common(get_group_ord, InCBPropertyGroup)
