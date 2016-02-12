from __future__ import print_function, unicode_literals

import re

def get_records(lines, pattern_coro_pairs):
    """
    generateor that will match lines against patterns and if they match send the match
     objects to coroutines that return some structured record.
    Args:
        lines: iterator of log lines
        pattern_coro_pairs: list of tuples in style [(re_pattern, coro), (...)...]

    Returns: a generator of records
    """
    #compile the patterns for speed
    pairs = [(re.compile(pat), co()) for pat, co in pattern_coro_pairs]

    for _, coro in pairs:  # prime the coroutines
        next(coro)

    for line in lines:
        for pat, coro in pairs:
            match = pat.search(line)
            if match:
                yield coro.send(match)
    for _, coro in pairs:
        coro.close()