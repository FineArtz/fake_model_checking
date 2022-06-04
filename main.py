from queue import Queue
from typing import  Set, Tuple
from dfs import check

from ltl_parser import AST
from reader import read_BM, read_TS
from transform import AST_to_GNBA, GNBA_to_NBA, NBA_product_TS, partial_ts


qu = Queue()
vis: Set[int] = set()


def is_finite(x: Tuple[int, int]) -> None:
    global flag
    if flag:
        return
    xx = x[1]
    for yy in nba.F:
        if xx == nba.state_map[yy]:
            flag = True
            return


def dfs(x: Tuple[int, int]) -> None:
    global flag
    if x in vis or flag:
        return
    is_finite(x)
    vis.add(x)
    if x in edge:
        for y in edge[x]:
            dfs(y)


if __name__ == '__main__':
    ts, ap = read_TS()
    ltl_all, ltl_state = read_BM()
    
    for ltl in ltl_all:
        ast = AST(f'!({ltl})')
        ts_ = partial_ts(ts, ast, ap)
        gnba = AST_to_GNBA(ast)
        nba = GNBA_to_NBA(gnba)
        prod = NBA_product_TS(nba, ts_)
        edge = prod.trans_map
        acc = check(prod, nba)
        print(int(acc))

    for (s, ltl) in ltl_state:
        ast = AST(f'!({ltl})')
        ts_ = partial_ts(ts, ast, ap)
        ts_.I = [s]
        # for (s, a), t in ts_.trans_map.items():
        #     print(f'{s} --- {a} --> {t}')
        # print(s, ast)
        # ele = ast.get_elementary_sets()
        # for e in ele:
        #     print([str(n) for n in list(e)])
        gnba = AST_to_GNBA(ast)
        nba = GNBA_to_NBA(gnba)
        # nba.print()
        prod = NBA_product_TS(nba, ts_)
        # print(prod.I)
        # for (s, a), t in prod.trans_map.items():
        #     print(f'{s} --- {a} --> {t}')
        # print(prod.trans_map)
        # edge = prod.trans_map
        acc = check(prod, nba)
        print(int(acc))

    # nba.num_states = 4
    # nba.num_str = 3
    # nba.add_trans(0, (), 0)
    # nba.add_trans(0, (0,), 0)
    # nba.add_trans(0, (0, 2), 0)
    # nba.add_trans(0, (0, 1, 2), 0)
    # nba.add_trans(0, (1, 2), 0)
    # nba.add_trans(0, (2,), 0)
    # nba.add_trans(0, (1,), 1)
    # nba.add_trans(0, (0, 1), 1)
    # nba.add_trans(1, (1,), 1)
    # nba.add_trans(1, (), 1)
    # nba.add_trans(1, (1, 2), 1)
    # nba.add_trans(1, (2,), 1)
    # nba.add_trans(1, (0,), 2)
    # nba.add_trans(1, (0, 1), 2)
    # nba.add_trans(1, (0, 2), 2)
    # nba.add_trans(1, (0, 1, 2), 2)
    # nba.add_trans(2, (2,), 1)
    # nba.add_trans(2, (1, 2), 1)
    # nba.add_trans(2, (), 2)
    # nba.add_trans(2, (0, 2), 2)
    # nba.add_trans(2, (0, 1, 2), 2)
    # nba.add_trans(2, (0,), 3)
    # nba.add_trans(2, (1,), 3)
    # nba.add_trans(2, (0, 1), 3)
    # nba.Q0 = 0
    # nba.F.append(3)

    # edge = NBA_product_TS(nba, ts)
    
    # for s in ts.I:
    #     print(f"dfs state {get_id(s, nba.Q0)}")
    #     dfs(get_id(s, nba.Q0))
    # print(flag)
