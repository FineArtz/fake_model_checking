# parse from file

from typing import List

from structure import *

DEFAULT_TS_FILE = 'TS.txt'
DEFAULT_BM_FILE = 'benchmark.txt'


def read_int(s: str) -> List[int]:
    return list(map(int, s.strip().split(' ')))


def read_TS(file: str = DEFAULT_TS_FILE) -> Tuple[TS[int], StrMap]:
    print(f"TS input file: {file}")
    ts = TS[int]()
    apset = StrMap() 
    with open(file, 'r') as f:
        S, T = read_int(f.readline())
        ts.num_states = S
        s0 = read_int(f.readline())
        ts.I.extend(s0)
        acts = f.readline().strip().split(' ')
        for a in acts:
            ts.add_action(a)
        aps = f.readline().strip().split(' ')
        for ap in aps:
            apset.add(ap)
        # read transitions
        for _ in range(T):
            x, a, y = f.readline().strip().split(' ')
            ts.add_trans(int(x), a, int(y))
        # read AP of states
        for i in range(S):
            aps = read_int(f.readline())
            if aps[0] == -1:
                assert len(aps) == 1
                ts.AP[i] = set()
            else:
                ts.AP[i] = set(aps)
    return ts, apset
        

def read_BM(file: str = DEFAULT_BM_FILE) -> Tuple[List[str], List[Tuple[int, str]]]:
    print(f"Benchmark input file: {file}")
    ltl_all: List[str] = []
    ltl_state: List[Tuple[int, str]] = []
    with open(file, 'r') as f:
        A, B = read_int(f.readline())
        for _ in range(A):
            ltl_all.append(f.readline().strip())
        for _ in range(B):
            s, l = f.readline().strip().split(' ', maxsplit=1)
            ltl_state.append((int(s), l))
    return ltl_all, ltl_state
