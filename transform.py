# transform functions including
# AST -> GNBA
# GNBA -> NBA
# NBA * TS
from typing import FrozenSet

from structure import *
from ltl_parser import *


T = TypeVar('T', bound=Hashable)
U = TypeVar('U', bound=Hashable)


def AST_to_GNBA(ast: AST) -> GNBA[Set[Node]]:
    Q = ast.get_elementary_sets()
    Q0 = [b for b in Q if ast.root in b]
    F = []
    APSet = frozenset([APNode(a) for a in ast.AP.str_to_id.keys()])
    for n in ast.closure:
        if isinstance(n, BinaryNode) and n.op == BINARY_OP.UTL:
            p2 = n.oprand2
            f = [b for b in Q if not (n in b and p2 not in b)]
            F.append(f)
    gnba = GNBA[FrozenSet[Node]](Q=Q, Q0=Q0, F=F)
    for b in gnba.Q: 
        # calculate transition function
        A: FrozenSet[APNode] = b & APSet # note that A can be empty set
        A = tuple(ast.AP.str_to_id[n.ap] for n in A)
        for bb in gnba.Q:
            if ast.check_next(b, bb) and ast.check_until(b, bb):
                gnba.add_trans(b, A, bb)
    return gnba


def GNBA_to_NBA(gnba: GNBA[T]) -> NBA[Tuple[T, int]]:
    fnum = len(gnba.F)
    if fnum == 0: 
        # accept all infinite fun
        Q = [(q, 0) for q in gnba.Q]
        Q0 = [(q0, 0) for q0 in gnba.Q0]
        nba = NBA[Tuple[T, int]](Q=Q, Q0=Q0, F=Q)
        nba.aug_map = gnba.state_map
        for (q, a), qq in gnba.trans.items():
            for q_ in qq:
                nba.add_trans((q, 0), a, (q_, 0))
    else:
        Q = [(q, i) for q in gnba.Q for i in range(fnum)]
        Q0 = [(q0, 0) for q0 in gnba.Q0]
        F = [(f, 0) for f in gnba.F[0]]
        nba = NBA[Tuple[T, int]](Q=Q, Q0=Q0, F=F)
        nba.aug_map = gnba.state_map
        for (q, a), qq in gnba.trans.items():
            for j in range(fnum):
                for q_ in qq:
                    if q in gnba.F[j]:
                        nba.add_trans((q, j), a, (q_, (j + 1) % fnum))
                    else:
                        nba.add_trans((q, j), a, (q_, j))
    nba.simplify()
    return nba


def NBA_product_TS(nba: NBA[T], ts: TS[U]) -> TS[Tuple[U, int]]:
    prod = TS[Tuple[U, int]]()
    for (s, a, t) in ts.trans:
        for q in nba.Q:
            pp = nba.get(q, tuple(ts.AP[t]))
            for p in pp:
                prod.add_trans((s, nba.state_map[q]), a, (t, nba.state_map[p]))
                # print(f'({s}, {nba.state_map[q]}) --- {a} --> ({t}, {nba.state_map[p]})')
    for s in ts.I:
        ql: List[T] = []
        for q0 in nba.Q0:
            qq = nba.get(q0, tuple(ts.AP[s]))
            ql.extend(qq)
        for q in ql:
            prod.I.append((s, nba.state_map[q]))
    prod.action_set = ts.action_set
    return prod


def partial_ts(ts: TS[T], ast: AST, ap: StrMap) -> TS[T]:
    # remove irrelevant AP from ts
    ts_ = TS[T]()
    ts_.num_states = ts.num_states
    ts_.action_set = ts.action_set
    ts_.I = ts.I
    ts_.trans = ts.trans
    ts_.trans_map = ts.trans_map
    for s, l in ts.AP.items():
        l_: Set[int] = set()
        for ll in l:
            ll_ = ast.AP.str_to_id.get(ap.id_to_str[ll], None)
            if ll_ is not None:
                l_.add(ll_)
        ts_.AP[s] = l_
    return ts_
