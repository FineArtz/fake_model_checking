# nested DFS

from typing import Hashable, List, Set, Tuple, TypeVar
from structure import NBA, TS


T = TypeVar('T', bound=Hashable)
U = TypeVar('U', bound=Hashable)


def check(ts: TS[Tuple[U, int]], nba: NBA[Tuple[T, int]]) -> bool:
    R: Set[Tuple[U, int]] = set()
    U: List[Tuple[U, int]] = []
    I = set(ts.I)
    cycle = False

    def post(s: Tuple[U, int]) -> Set[Tuple[U, int]]:
        P = set()
        for a in range(ts.action_set.num_str):
            t = ts.trans_map.get((s, a), [])
            P.update(t)
        return P

    def cycle_check(s: Tuple[U, int]) -> bool:
        nonlocal cycle
        T: set[Tuple[U, int]] = {s}
        V: list[Tuple[U, int]] = [s]
        while True:
            ss = V[-1]
            P = post(ss)
            PP = P - T
            if s in P:
                cycle = True
            elif PP:
                sss = next(iter(PP))
                V.append(sss)
                T.add(sss)
            else:
                V.pop()
            if len(V) == 0 or cycle:
                break
        return cycle

    def reachable_cycle(s: Tuple[U, int]) -> None:
        nonlocal cycle
        U.append(s)
        R.add(s)
        while True:
            ss = U[-1]
            P = post(ss)
            PP = P - R
            if PP:
                sss = next(iter(PP))
                U.append(sss)
                R.add(sss)
            else:
                U.pop()
                for f in nba.F:
                    if ss[1] == nba.state_map[f]:
                        cycle = cycle_check(ss)
            if len(U) == 0 or cycle:
                break

    II = I - R
    while II and not cycle:
        s = next(iter(II))
        reachable_cycle(s)
        II = I - R
    
    return not cycle
