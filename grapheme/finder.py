from collections.abc import Iterator
from enum import Enum

from grapheme.grapheme_property_group import GraphemePropertyGroup as GCB  # noqa: N814
from grapheme.grapheme_property_group import get_group
from grapheme.incb_property_group import InCBPropertyGroup as InCBGroup
from grapheme.incb_property_group import get_group as get_group_incb


class BreakPossibility(Enum):
    CERTAIN = "certain"
    POSSIBLE = "possible"
    NO_BREAK = "nobreak"


def get_break_possibility(a, b) -> BreakPossibility:
    # Probably most common, included as short circuit before checking all else
    if a is GCB.OTHER and b is GCB.OTHER:
        return BreakPossibility.CERTAIN

    assert isinstance(a, GCB)
    assert isinstance(b, GCB)

    # Only break if preceeded by an uneven number of REGIONAL_INDICATORS
    # sot (RI RI)* RI × RI
    # [^RI] (RI RI) * RI × RI
    if a is GCB.REGIONAL_INDICATOR and b is GCB.REGIONAL_INDICATOR:
        return BreakPossibility.POSSIBLE

    # (Control | CR | LF) ÷
    #  ÷ (Control | CR | LF)
    if a in [GCB.CONTROL, GCB.CR, GCB.LF] or b in [
        GCB.CONTROL,
        GCB.CR,
        GCB.LF,
    ]:
        # CR × LF
        if a is GCB.CR and b is GCB.LF:
            return BreakPossibility.NO_BREAK
        else:
            return BreakPossibility.CERTAIN

    # L × (L | V | LV | LVT)
    if a is GCB.L and b in [GCB.L, GCB.V, GCB.LV, GCB.LVT]:
        return BreakPossibility.NO_BREAK

    # (LV | V) × (V | T)
    if a in [GCB.LV, GCB.V] and b in [GCB.V, GCB.T]:
        return BreakPossibility.NO_BREAK

    # (LVT | T)    ×    T
    if a in [GCB.LVT, GCB.T] and b is GCB.T:
        return BreakPossibility.NO_BREAK

    # × (Extend | ZWJ)
    # × SpacingMark
    # Prepend ×
    if b in [GCB.EXTEND, GCB.ZWJ, GCB.SPACING_MARK] or a is GCB.PREPEND:
        return BreakPossibility.NO_BREAK

    # \p{Extended_Pictographic} Extend* ZWJ × \p{Extended_Pictographic}
    if a is GCB.ZWJ and b is GCB.EXTENDED_PICTOGRAPHIC:
        return BreakPossibility.POSSIBLE

    # everything else, assumes all other rules are included above
    return BreakPossibility.CERTAIN


def get_break_possibility_incb(a, b) -> BreakPossibility:
    # Probably most common, included as short circuit before checking all else
    if a is InCBGroup.OTHER and b is InCBGroup.OTHER:
        return BreakPossibility.CERTAIN

    if a in [InCBGroup.LINKER, InCBGroup.EXTEND] and b is InCBGroup.CONSONANT:
        return BreakPossibility.NO_BREAK

    if a in [InCBGroup.LINKER, InCBGroup.EXTEND, InCBGroup.CONSONANT] and b is InCBGroup.LINKER:
        return BreakPossibility.NO_BREAK

    assert isinstance(a, InCBGroup)
    assert isinstance(b, InCBGroup)

    # everything else, assumes all other rules are included above
    return BreakPossibility.POSSIBLE


def get_last_certain_break_index(string, index) -> int:
    if index >= len(string):
        return len(string)

    prev = get_group(string[index])
    prev_incb = get_group_incb(string[index])
    while True:
        if index <= 0:
            return 0
        index -= 1
        cur = get_group(string[index])
        cur_incb = get_group_incb(string[index])
        if (
            get_break_possibility(cur, prev) == BreakPossibility.CERTAIN
            and get_break_possibility_incb(cur_incb, prev_incb) != BreakPossibility.NO_BREAK
        ):
            return index + 1
        prev = cur
        prev_incb = cur_incb


class UState(Enum):
    DEFAULT = 0  # No special case
    GB9c_Consonant = 10
    GB9c_Linker = 11
    GB11_Picto = 20
    GB12_First = 30
    GB12_Second = 31


class GraphemeIterator:
    def __init__(self, string: str) -> None:
        self.str_iter = iter(string)
        self.buffer: str = ""
        self.lastg = None
        self.state = UState.DEFAULT
        try:
            self.buffer = next(self.str_iter)
        except StopIteration:
            self.buffer = ""
        else:
            lastg = get_group(self.buffer)
            self.lastg = lastg
            if lastg is GCB.EXTENDED_PICTOGRAPHIC:
                self.state = UState.GB11_Picto
            elif lastg is GCB.REGIONAL_INDICATOR:
                self.state = UState.GB12_First
            else:
                lastincb = get_group_incb(self.buffer)
                if lastincb is InCBGroup.CONSONANT:
                    self.state = UState.GB9c_Consonant

    def __iter__(self) -> Iterator[str]:
        return self

    def __next__(self) -> str:
        for codepoint in self.str_iter:
            nextg = get_group(codepoint)
            next_inbc = get_group_incb(codepoint)

            # Default: break between clusters
            do_break, self.state = GraphemeIterator.fsm(self.state, self.lastg, nextg, next_inbc)
            self.lastg = nextg
            if do_break is True:
                return self._break(codepoint)
            self.buffer += codepoint  # type: ignore

        if self.buffer:
            # GB2  Any ÷ eot
            # Break at the end of text, unless the text is empty.
            return self._break("")
        raise StopIteration()

    @staticmethod
    def fsm(state, lastg, nextg, next_inbc) -> tuple[bool, UState]:
        do_break = True
        match (state, lastg, nextg, next_inbc):
            # First the most common
            case (_, GCB.OTHER, GCB.OTHER, InCBGroup.OTHER):
                # GB999     Any ÷ Any
                # Otherwise, break everywhere
                state = UState.DEFAULT
            case (_, GCB.CR, GCB.LF, _):
                # GB3       CR	×	LF
                do_break = False
                state = UState.DEFAULT
            case (_, GCB.CR | GCB.LF | GCB.CONTROL, _, InCBGroup.CONSONANT):
                # Special case mix GB3 + GB9c Consonant
                do_break = True
                state = UState.GB9c_Consonant
            case (_, GCB.CR | GCB.LF | GCB.CONTROL, _, _):
                # GB4       (Control | CR | LF)	÷	 Any
                do_break = True
                state = UState.DEFAULT
            case (_, _, GCB.CR | GCB.LF | GCB.CONTROL, _):
                # GB5       Any	÷	(Control | CR | LF)
                state = UState.DEFAULT
            case (_, GCB.L, GCB.L | GCB.V | GCB.LV | GCB.LVT, _):
                # GB6       L	×	(L | V | LV | LVT)
                do_break = False
                state = UState.DEFAULT
            case (_, GCB.LV | GCB.V, GCB.V | GCB.T, _):
                # GB7       (LV | V)	×	(V | T)
                do_break = False
                state = UState.DEFAULT
            case (_, GCB.LVT | GCB.T, GCB.T, _):
                # GB8       (LVT | T)	×	T
                do_break = False
                state = UState.DEFAULT
            case (_, _, GCB.SPACING_MARK, _):
                # GB9a      Any	×	SpacingMark
                do_break = False
                state = UState.DEFAULT
            case (_, GCB.PREPEND, _, _):
                # GB9b      Prepend	×	Any
                do_break = False
                state = UState.DEFAULT
            # GB9c	        Consonant [ Extend Linker ]* Linker [ Extend Linker ]* × Consonant
            case (UState.GB9c_Linker, _, _, InCBGroup.CONSONANT):
                state = UState.GB9c_Consonant
                do_break = False
            case (UState.GB9c_Consonant | UState.GB9c_Linker, _, _, InCBGroup.EXTEND):
                # unchanged state
                do_break = False
            case (UState.GB9c_Consonant | UState.GB9c_Linker, _, _, InCBGroup.LINKER):
                state = UState.GB9c_Linker
                do_break = False
            case (_, _, _, InCBGroup.CONSONANT):  # generic state last
                # Consonant
                state = UState.GB9c_Consonant
                # do not change do_break
            # GB11:         \p{Extended_Pictographic} Extend* ZWJ × \p{Extended_Pictographic}
            case (UState.GB11_Picto, _, GCB.EXTEND | GCB.ZWJ, _):
                # Extend + ( Extend* + ) ZWJ
                do_break = False
                # unchanged state
            case (UState.GB11_Picto, GCB.ZWJ, GCB.EXTENDED_PICTOGRAPHIC, _):
                # ZWJ + Extended_Pictographic
                do_break = False
                # unchanged state
            case (_, GCB.EXTENDED_PICTOGRAPHIC, GCB.ZWJ | GCB.EXTEND, _):  # generic state
                # Extended_Pictographic + ( Extend* + ) ZWJ
                state = UState.GB11_Picto
                do_break = False
            # GB12	        sot (RI RI)* RI	×	RI
            # GB13	        [^RI] (RI RI)* RI	×	RI
            case (UState.GB12_First, GCB.REGIONAL_INDICATOR, GCB.REGIONAL_INDICATOR, _):
                do_break = False
                state = UState.GB12_Second
            case (UState.GB12_Second, GCB.REGIONAL_INDICATOR, GCB.REGIONAL_INDICATOR, _):
                do_break = True
                state = UState.GB12_First
            case (_, _, GCB.REGIONAL_INDICATOR, _):  # generic state always last
                do_break = True
                state = UState.GB12_First
            case (_, _, GCB.EXTEND | GCB.ZWJ, _):  # generic state always last
                # GB9       Any	×	(Extend | ZWJ)
                do_break = False
                # unchanged state
                # state = UState.DEFAULT
            case _:
                # GB999	    Any	÷	Any
                do_break = True
                state = UState.DEFAULT
        return do_break, state

    def _break(self, new: str) -> str:
        """Return the current buffer, start with a new one"""
        old_buffer = self.buffer
        self.buffer = new
        return old_buffer
