from grapheme.finder import GraphemeIterator
from grapheme.grapheme_property_group import get_group
from grapheme.incb_property_group import get_group as get_group_incb


def main():
    s = "\u2701\u200d\u2701\u200d\u231a"
    print(list(s))
    it = GraphemeIterator(s)
    nextg = get_group(s[0])
    next_inbc = get_group_incb(s[0])
    print(repr(s[0]), nextg, next_inbc, "->", it.state)
    for i, codepoint in enumerate(it.str_iter):
        nextg = get_group(codepoint)
        next_inbc = get_group_incb(codepoint)
        last_state = it.state
        do_break, it.state = it.fsm(it.state, it.lastg, nextg, next_inbc)
        it.lastg = nextg
        print(repr(s[i]) + repr(codepoint), do_break, last_state, it.lastg, nextg, next_inbc)


if __name__ == "__main__":
    main()
