# parser for LTL formula using antlr tree

from typing import FrozenSet, Set
from antlr4 import *

from antlr.ltlParser import ltlParser
from antlr.ltlLexer import ltlLexer
from antlr.ltlVisitor import ltlVisitor
from ltl_node import *
from structure import StrMap


class ASTBuilder(ltlVisitor):

    def visitParFormula(self, ctx: ltlParser.ParFormulaContext) -> Node:
        return self.visit(ctx.child)

    def visitAp(self, ctx: ltlParser.ApContext) -> Node:
        return APNode(ap=ctx.getText())

    def visitUnaryExpr(self, ctx: ltlParser.UnaryExprContext) -> Node:
        op = OP_DICT.get(ctx.op.text, None)
        if isinstance(op, UNARY_OP):
            if op == UNARY_OP.AWS: # G a === !(true U !a)
                return get_neg(BinaryNode(
                    op=BINARY_OP.UTL, 
                    opr1=TRUE_NODE, 
                    opr2=get_neg(self.visit(ctx.child))
                ))
            elif op == UNARY_OP.EVE: # F a === true U a
                return BinaryNode(op=BINARY_OP.UTL, opr1=TRUE_NODE, opr2=self.visit(ctx.child))
            elif op == UNARY_OP.NOT: # prevent !(!a)
                return get_neg(self.visit(ctx.child))
            else: # no transform for NXT
                return UnaryNode(op=op, opr=self.visit(ctx.child))
        else:
            raise ValueError(f'Unexpected unary op: {ctx.op.text}')

    def visitBinaryExpr(self, ctx: ltlParser.BinaryExprContext) -> Node:
        op = OP_DICT.get(ctx.op.text)
        if isinstance(op, BINARY_OP):
            if op == BINARY_OP.OR: # a or b === !(!a and !b)
                return get_neg(
                    BinaryNode(op=BINARY_OP.AND, 
                        opr1=get_neg(self.visit(ctx.lhs)),
                        opr2=get_neg(self.visit(ctx.rhs))
                    )
                )
            elif op == BINARY_OP.IMP: # a -> b === !(a and !b)
                return get_neg(BinaryNode(
                    op=BINARY_OP.AND, 
                    opr1=self.visit(ctx.lhs),
                    opr2=get_neg(self.visit(ctx.rhs))
                ))
            else: # no transform for AND or UTL
                return BinaryNode(op=op, opr1=self.visit(ctx.lhs), opr2=self.visit(ctx.rhs))
        else:
            raise ValueError(f'Unexpected binary op: {ctx.op.text}')
        

class AST:
    # The abstract syntax tree of the given LTL formula

    def __init__(self, ltl: str) -> None:
        self.root: Node = None
        self.closure: FrozenSet[Node] = None
        self.contains_true: bool = False
        self.AP = StrMap()
        self._build(ltl)

    def _build(self, ltl: str) -> None:
        input_stream = InputStream(ltl)
        lexer = ltlLexer(input_stream)
        tokens = CommonTokenStream(lexer)
        parser = ltlParser(tokens)
        tree = parser.formula()
        self.root = ASTBuilder().visit(tree)
        self._set_ap(self.root)
        self.closure = self.get_closure()
        self.contains_true = (TRUE_NODE in self.closure)

    def _set_ap(self, cur_node: Node) -> None:
        assert cur_node is not None
        if isinstance(cur_node, UnaryNode):
            self._set_ap(cur_node.oprand)
        elif isinstance(cur_node, BinaryNode):
            self._set_ap(cur_node.oprand1)
            self._set_ap(cur_node.oprand2)
        elif isinstance(cur_node, APNode):
            self.AP.add(cur_node.ap)

    def __str__(self) -> str:
        return str(self.root)

    def _polish(self) -> str:
        return ' '.join(self.root._polish())

    def _middle(self) -> str:
        return ' '.join(self.root._middle())
    
    def _check_operator(self, cur_node: Node) -> bool:
        # an AST should only contain NOT, NEXT, AND, and UNTIL
        assert cur_node is not None
        if isinstance(cur_node, LiteralNode) or isinstance(cur_node, APNode):
            return True
        if isinstance(cur_node, UnaryNode):
            if cur_node.op == UNARY_OP.NOT:
                if isinstance(cur_node.oprand, UnaryNode) and cur_node.oprand.op == UNARY_OP.NOT:
                    print('Double negation.')
                    return False
                return self._check_operator(cur_node.oprand)
            elif cur_node.op == UNARY_OP.NXT:
                return self._check_operator(cur_node.oprand)
            else:
                print('Unexpected operator:', cur_node.op_str)
                return False
        if isinstance(cur_node, BinaryNode):
            if cur_node.op == BINARY_OP.AND or cur_node.op == BINARY_OP.UTL:
                return self._check_operator(cur_node.oprand1) and self._check_operator(cur_node.oprand2)
            else:
                print('Unexpected operator:', cur_node.op_str)
                return False

    def get_closure(self) -> FrozenSet[Node]:
        if self.closure is not None:
            return self.closure
        subs = set(self.root._sub())
        negs = []
        for sub in subs:
            negs.append(get_neg(sub))
        return frozenset(subs.union(set(negs)))
    
    def _check_consistency(self, sub: Set[Node]) -> bool:
        if self.contains_true and TRUE_NODE not in sub:
            return False
        for n in sub:
            if get_neg(n) in sub:
                return False
            if isinstance(n, BinaryNode) and n.op == BINARY_OP.AND:
                if not(n.oprand1 in sub and n.oprand2 in sub):
                    return False
        l = list(sub)
        for i in range(len(l)):
            for j in range(i + 1, len(l)):
                b = BinaryNode(op=BINARY_OP.AND, opr1=l[i], opr2=l[j])
                if b in self.closure and b not in sub:
                    return False
        return True

    def _check_local_consistency(self, sub: Set[Node]) -> bool:
        for n in self.closure:
            if isinstance(n, BinaryNode) and n.op == BINARY_OP.UTL:
                if n.oprand2 in sub and n not in sub:
                    return False
                if n in sub and n.oprand2 not in sub and n.oprand1 not in sub:
                    return False
        return True

    def is_elementary(self, sub: Set[Node]) -> bool:
        # the generation has guaranteed maximality
        return self._check_consistency(sub) and self._check_local_consistency(sub)

    def get_elementary_sets(self) -> List[FrozenSet[Node]]:
        pos = []
        neg = []
        vis = set()
        # one and only one of A and !A is in the elementary set
        # due to maximality
        # first devide all elements in the closure into two sets
        for s in self.closure:
            if s in vis:
                assert get_neg(s) in vis
                continue
            pos.append(s)
            neg.append(get_neg(s))
            vis.add(s)
            vis.add(get_neg(s))

        ret = []
        for i in range(1 << len(pos)): 
            # enumerate for 2 ** (size(closure) / 2) possibilities
            sub = set()
            for j in range(len(pos)):
                if i & (1 << j):
                    sub.add(pos[j])
                else:
                    sub.add(neg[j])
            if self.is_elementary(sub):
                ret.append(frozenset(sub))
        return ret

    def check_next(self, b: Set[Node], bb: Set[Node]) -> bool:
        for n in self.closure:
            if isinstance(n, UnaryNode) and n.op == UNARY_OP.NXT:
                if n in b and n.oprand not in bb:
                    return False
                if n.oprand in bb and n not in b:
                    return False
        return True

    def check_until(self, b: Set[Node], bb: Set[Node]) -> bool:
        for n in self.closure:
            if isinstance(n, BinaryNode) and n.op == BINARY_OP.UTL:
                p1 = n.oprand1
                p2 = n.oprand2
                flag1 = n in b
                flag2 = (p2 in b) or ((p1 in b) and (n in bb))
                if flag1 ^ flag2:
                    return False
        return True
                