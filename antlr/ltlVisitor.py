# Generated from .\antlr\ltl.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .ltlParser import ltlParser
else:
    from ltlParser import ltlParser

'''
Auto-generated by ANTLR4. Please check ltl.g4 for grammar details.
'''


# This class defines a complete generic visitor for a parse tree produced by ltlParser.

class ltlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ltlParser#unaryExpr.
    def visitUnaryExpr(self, ctx:ltlParser.UnaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ltlParser#parFormula.
    def visitParFormula(self, ctx:ltlParser.ParFormulaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ltlParser#binaryExpr.
    def visitBinaryExpr(self, ctx:ltlParser.BinaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ltlParser#ap.
    def visitAp(self, ctx:ltlParser.ApContext):
        return self.visitChildren(ctx)



del ltlParser