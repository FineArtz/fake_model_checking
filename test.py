from antlr4 import *
from antlr.ltlLexer import ltlLexer
from antlr.ltlParser import ltlParser
from antlr.ltlVisitor import ltlVisitor

from ltl_node import *
from ltl_parser import *
from structure import *
from transform import *


class KeyVisitor(ltlVisitor):

    def visitFormula(self, ctx: ltlParser.FormulaContext):
        print(ctx.getText())
        return super().visitFormula(ctx)

def check_grammar():
    input_stream = InputStream('c U (true /\\ (!b))')
    lexer = ltlLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = ltlParser(stream)
    tree = parser.formula()
    print(tree.toStringTree(recog=parser))
    visitor = KeyVisitor()
    visitor.visit(tree)
    

def check_ast():
    ltl = '!(G(a->((!b) U (a /\\ b))))'
    ast = AST(ltl)
    print(ast)
    print('Polish:', ast._polish())
    print('Middle:', ast._middle())
    print('Check operator transform:', ast._check_operator(ast.root))

    clos = ast.get_closure()
    print('Closure:')
    print(len(ast.closure))
    for clo in clos:
        print(clo)

    print('Elementary set:')
    t = TRUE_NODE
    a = APNode('a')
    b = APNode('b')
    p1 = BinaryNode(BINARY_OP.AND, a, b)
    p2 = BinaryNode(BINARY_OP.UTL, get_neg(b), p1)
    p3 = get_neg(BinaryNode(BINARY_OP.AND, a, get_neg(p2)))
    p4 = BinaryNode(BINARY_OP.UTL, t, get_neg(p3))
    subs = set([t, a, b, p1, p2, p3, p4])
    elems = ast.get_elementary_sets()
    print(len(elems))
    for elem in elems:
        print('\t'.join([str(n) for n in elem]))


def check_gnba():
    # s = 'a U ((!a) /\\ b)' # an example from Lecture Note 11
    s = '!(G(a->((!b) U (a /\\ b))))'
    ast = AST(s)
    print(ast)

    gnba = AST_to_GNBA(ast)
    gnba.print()


def check_nba():
    # s = '!(G(a->((!b) U (a /\\ b))))'
    # ast = AST(s)
    # print(ast)
    # gnba = AST_to_GNBA(ast)
    # gnba.print()
    Q = [0, 1, 2]
    Q0 = [0]
    F = [[1], [2]]
    gnba = GNBA[int](Q=Q, Q0=Q0, F=F) # an example from Exercise 5
    gnba.add_trans(0, [0], 1)
    gnba.add_trans(1, [1], 1)
    gnba.add_trans(1, [1], 0)
    gnba.add_trans(1, [1], 2)
    gnba.add_trans(2, [1], 0)
    gnba.print()
    nba = GNBA_to_NBA(gnba)
    nba.print()


def check_prod():
    # an example from Lecture Note 8
    ts = TS()
    ts.num_states = 4
    ts.I.append(0)
    ts.AP[0] = set()
    ts.AP[1] = {1}
    ts.AP[2] = {0}
    ts.AP[3] = {0, 1}
    ts.add_action('0')
    ts.add_trans(0, 0, 1)
    ts.add_trans(1, 0, 2)
    ts.add_trans(2, 0, 3)
    ts.add_trans(3, 0, 0)

    Q = [0, 1, 2]
    Q0 = [0]
    F = [2]
    nba = NBA[int](Q=Q, Q0=Q0, F=F)
    nba.add_trans(0, (), 0)
    nba.add_trans(0, (0,), 2)
    nba.add_trans(0, (1,), 1)
    nba.add_trans(1, (1,), 1)
    nba.add_trans(1, (0, ), 0)

    prod = NBA_product_TS(nba, ts)
    print(prod.I)
    print(prod.AP)
    print(prod.trans)


if __name__ == '__main__':
    # check_grammar()
    # check_ast()
    # check_gnba()
    # check_nba()
    check_prod()
