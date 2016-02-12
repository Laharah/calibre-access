from __future__ import unicode_literals

from pytest import raises

import utilities

def test_get_records():
    lines = "paaaaatern patern no_match".split()
    pat = r'pa+tern'
    def coro():
        while True:
            s = yield 'a match'

    gr = utilities.get_records(lines, [(pat, coro)])
    assert list(gr) == ['a match'] *2

    pat2 = r'^no_ma\w*$'
    def coro2():
        while True:
            s = yield
            yield 'another match: {}'.format(s.string)

    gr = utilities.get_records(lines, [(pat, coro), (pat2, coro2)])
    assert list(gr) == (['a match'] *2) + ['another match: no_match']

