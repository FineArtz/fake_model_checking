# node to represent LTL formula

from __future__ import annotations
from enum import Enum
from typing import List


class UNARY_OP(Enum):
    NOT = 0    
    NXT = 1
    AWS = 2
    EVE = 3


class BINARY_OP(Enum):
    AND = 0
    OR = 1
    IMP = 2
    UTL = 3


OP_DICT = {
    '!': UNARY_OP.NOT,
    'X': UNARY_OP.NXT,
    'G': UNARY_OP.AWS,
    'F': UNARY_OP.EVE,
    '/\\': BINARY_OP.AND,
    '\\/': BINARY_OP.OR,
    '->': BINARY_OP.IMP,
    'U': BINARY_OP.UTL,
}


INV_OP_DICT = {
    UNARY_OP.NOT: '!',
    UNARY_OP.NXT: 'X',
    UNARY_OP.AWS: 'G',
    UNARY_OP.EVE: 'F',
    BINARY_OP.AND: '/\\',
    BINARY_OP.OR: '\\/',
    BINARY_OP.IMP: '->',
    BINARY_OP.UTL: 'U',
}


def is_commutable(o: BINARY_OP) -> bool:
    return o == BINARY_OP.AND or o == BINARY_OP.OR

    
class Node:
    # interface

    def _polish(self) -> List[str]:
        # return the Polish notation
        return []

    def _middle(self) -> List[str]:
        # return the middle notation
        return []

    def __hash__(self) -> int:
        # detemine the formula by its Polish notation and middle notation
        return tuple(self._polish() + self._middle()).__hash__()

    def __eq__(self, __o: object) -> bool:
        return self.__hash__() == __o.__hash__()

    def __str__(self) -> str:
        return ''

    def _sub(self) -> List[Node]:
        # return all sub-formula
        return []


class LiteralNode(Node):

    def __init__(self, literal: bool) -> None:
        self.literal = literal

    def _polish(self) -> List[str]:
        return [str(self.literal)]

    def _middle(self) -> List[str]:
        return [str(self.literal)]

    def __str__(self) -> str:
        return str(self.literal)

    def _sub(self) -> List[Node]:
        return [self]


class APNode(Node):

    def __init__(self, ap: str) -> None:
        self.ap = ap

    def _polish(self) -> List[str]:
        return [self.ap]

    def _middle(self) -> List[str]:
        return [self.ap]

    def __str__(self) -> str:
        return self.ap

    def _sub(self) -> List[Node]:
        return [self]


class UnaryNode(Node):

    def __init__(self, op: UNARY_OP, opr: Node = None) -> None:
        self.op = op
        self.op_str = INV_OP_DICT[op]
        self.oprand = opr

    def _polish(self) -> List[str]:
        return [self.op_str] + self.oprand._polish()

    def _middle(self) -> List[str]:
        return [self.op_str] + self.oprand._middle()

    def __str__(self) -> str:
        return f'{self.op_str}({str(self.oprand)})'

    def _sub(self) -> List[Node]:
        return self.oprand._sub() + [self]


class BinaryNode(Node):

    def __init__(self, op: BINARY_OP, opr1: Node = None, opr2: Node = None) -> None:
        self.op = op
        self.op_str = INV_OP_DICT[op]
        self.oprand1 = opr1
        self.oprand2 = opr2
        if is_commutable(op) and hash(self.oprand1) > hash(self.oprand2):
            self.oprand1 = opr2
            self.oprand2 = opr1

    def _polish(self) -> List[str]:
        return [self.op_str] + self.oprand1._polish() + self.oprand2._polish()

    def _middle(self) -> List[str]:
        return self.oprand1._middle() + [self.op_str] + self.oprand2._middle()    

    def __str__(self) -> str:
        return f'({str(self.oprand1)}) {self.op_str} ({self.oprand2})'

    def _sub(self) -> List[Node]:
        return self.oprand1._sub() + self.oprand2._sub() + [self]
     

TRUE_NODE = LiteralNode(True)
FALSE_NODE = LiteralNode(False)


def get_neg(n: Node) -> Node:
    if isinstance(n, LiteralNode):
        if n == TRUE_NODE:
            return LiteralNode(False)
        else:
            return LiteralNode(True)
    if isinstance(n, UnaryNode) and n.op == UNARY_OP.NOT:
        return n.oprand
    return UnaryNode(op=UNARY_OP.NOT, opr=n)
