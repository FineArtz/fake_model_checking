# utility functions

from typing import List, Set, TypeVar


T = TypeVar('T')


def power_set(s: Set[T]) -> List[Set[T]]:
    l = list(s)
    ret = []
    for i in range(1 << len(l)):
        r = []
        for j in range(len(l)):
            if i & (1 << j):
                r.append(l[j])
        ret.append(set(r))
    return ret
