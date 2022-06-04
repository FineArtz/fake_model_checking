from dfs import check
from ltl_parser import AST
from reader import read_BM, read_TS, write_ans
from transform import AST_to_GNBA, GNBA_to_NBA, NBA_product_TS, partial_ts


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
        write_ans(int(acc))

    for (s, ltl) in ltl_state:
        ast = AST(f'!({ltl})')
        ts_ = partial_ts(ts, ast, ap)
        ts_.I = [s]
        gnba = AST_to_GNBA(ast)
        nba = GNBA_to_NBA(gnba)
        prod = NBA_product_TS(nba, ts_)
        acc = check(prod, nba)
        write_ans(int(acc))
