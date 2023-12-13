from sly import Parser
from sly.yacc import YaccProduction
from typing import List

from COOL.error import Error
from COOL.coollexer import CoolLexer
from COOL.tokens import Token

from COOL.nodes.operators import Add
from COOL.nodes.operators import Sub
from COOL.nodes.operators import Times
from COOL.nodes.operators import Div
from COOL.nodes.operators import Less
from COOL.nodes.operators import LessEqual
from COOL.nodes.operators import Equal
from COOL.nodes.operators import Not
from COOL.nodes.operators import Bitwise

from COOL.nodes.program import Program
from COOL.nodes.classdef import Class
from COOL.nodes.feature import Attribute
from COOL.nodes.feature import AttributeDeclaration
from COOL.nodes.feature import AttributeInicialization
from COOL.nodes.feature import Formal
from COOL.nodes.feature import Method
from COOL.nodes.feature import ExecuteMethod
from COOL.nodes.variable import GetVariable
from COOL.nodes.variable import Initialization
from COOL.nodes.variable import Declaration
from COOL.nodes.variable import Assign
from COOL.nodes.object import Interger
from COOL.nodes.object import String
from COOL.nodes.object import Boolean
from COOL.nodes.expr import If
from COOL.nodes.expr import CodeBlock
from COOL.nodes.expr import While
from COOL.nodes.expr import Let
from COOL.nodes.expr import Case
from COOL.nodes.expr import New
from COOL.nodes.expr import Isvoid
from COOL.nodes.expr import Dispatch
from COOL.nodes.expr import Case_expr


# TODO: fix and check precedence
class CoolParser(Parser):
    tokens = CoolLexer.tokens
    # debugfile = 'parser.out'

    def __init__(self):
        self.errors = []
        super().__init__()
    
    precedence = (
       ('right', 'ASSIGN'),
       ('nonassoc', 'NOT'),
       ('nonassoc', 'EQUAL', 'LESS', 'LESSEQUAL'),
       ('left', 'PLUS', 'MINUS'),
       ('left', 'TIMES', 'DIVIDE'),
       ('right', 'ISVOID'),
       ('left', 'BITWISE'),
       ('nonassoc', '@'),
       ('nonassoc', 'NUMBER'),
       ('nonassoc', '(',')'),
       ('left', '.'),
    )

    def _get_column_from_production(self, p: YaccProduction):
        column = {
            name[0]: token.column
            for name, token in zip(p._namemap.items(), p._slice)
            if isinstance(token, Token)
        }              
        return column

    @_('program')
    def start(self, p: YaccProduction):
        return Program(classes=p.program)

    @_('classdef ";"')
    def program(self, p: YaccProduction):
        return [p.classdef]
    
    @_('classdef ";" program')
    def program(self, p: YaccProduction):
        return [p.classdef] + p.program

    @_('CLASS TYPE "{" features "}"')
    def classdef(self, p: YaccProduction):
        return Class(
            line=p.lineno,
            column=self._get_column_from_production(p),
            type=p.TYPE,
            features=p.features
        )

    @_('CLASS TYPE INHERITS TYPE "{" features "}"')
    def classdef(self, p: YaccProduction):
        return Class(
            line=p.lineno,
            column=self._get_column_from_production(p),
            features=p.features,
            type=p.TYPE0,
            inherits=p.TYPE1
        )

    @_('feature ";" features')
    def features(self, p: YaccProduction):
        return [p.feature] + p.features

    @_('')
    def features(self, p: YaccProduction):
        return []
    
    @_('ID ":" TYPE ASSIGN expr')
    def feature(self, p: YaccProduction):
        return AttributeInicialization(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE,
            expr=p.expr
        )
    
    @_('ID ":" TYPE')
    def feature(self, p: YaccProduction):
        return AttributeDeclaration(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE
        )

    @_('ID "(" formals ")" ":" TYPE "{" expr "}"')
    def feature(self, p: YaccProduction):
        return Method(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE,
            formals=p.formals,
            expr=p.expr
        )
    
    @_('ID "(" ")" ":" TYPE "{" expr "}"')
    def feature(self, p: YaccProduction):
        return Method(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE,
            formals=[],
            expr=p.expr
        )

    @_('formal "," formals')
    def formals(self, p: YaccProduction):
        return [p.formal] + p.formals
    
    @_('formal')
    def formals(self, p: YaccProduction):
        return [p.formal]

    @_('ID ":" TYPE')
    def formal(self, p: YaccProduction):
        return Formal(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE
        )
    
    @_('NEW TYPE')
    def expr(self, p: YaccProduction):
        return New(
            line=p.lineno,
            column=self._get_column_from_production(p),
            type=p.TYPE
        )
    
    @_('expr "," exprs')
    def exprs(self, p: YaccProduction):
        return [p.expr] + p.exprs
    
    @_('expr')
    def exprs(self, p: YaccProduction):
        return [p.expr]

    @_('ID ASSIGN expr')
    def expr(self, p: YaccProduction):
        return Assign(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            expr=p.expr
        )
    
    @_('expr "." ID "(" exprs ")"')
    def expr(self, p: YaccProduction):
        return Dispatch(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
            id=p.ID,
            exprs=p.exprs
        )
    
    @_('expr "." ID "(" ")"')
    def expr(self, p: YaccProduction):
        return Dispatch(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
            id=p.ID,
            exprs=[]
        )

    @_('expr "@" TYPE "." ID "(" exprs ")"')
    def expr(self, p: YaccProduction):
        return Dispatch(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
            id=p.ID,
            type=p.TYPE,
            exprs=p.exprs
        )
    
    @_('expr "@" TYPE "." ID "(" ")"')
    def expr(self, p: YaccProduction):
        return Dispatch(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
            id=p.ID,
            type=p.TYPE,
            exprs=[]
        )
    
    @_('ID "(" exprs ")"')
    def expr(self, p: YaccProduction):
        return ExecuteMethod(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            exprs=p.exprs
        )
    
    @_('ID "(" ")"')
    def expr(self, p: YaccProduction):
        return ExecuteMethod(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            exprs=[]
        )

    @_('IF expr THEN expr ELSE expr FI')
    def expr(self, p: YaccProduction):
        return If(
            line=p.lineno,
            column=self._get_column_from_production(p),
            if_expr=p.expr0,
            then_expr=p.expr1,
            else_expr=p.expr2
        )

    @_('WHILE expr LOOP expr POOL')
    def expr(self, p: YaccProduction):
        return While(
            line=p.lineno,
            column=self._get_column_from_production(p),
            while_expr=p.expr0,
            loop_expr=p.expr1
        )

    @_('"{" nested_expr "}"')
    def expr(self, p: YaccProduction):
        return CodeBlock(
            line=p.lineno,
            column=self._get_column_from_production(p),
            exprs=p.nested_expr)

    @_('expr ";" nested_expr')
    def nested_expr(self, p: YaccProduction):
        return [p.expr] + p.nested_expr
    
    @_('expr ";"')
    def nested_expr(self, p: YaccProduction):
        return [p.expr]

    @_('LET let_list IN expr')
    def expr(self, p: YaccProduction):
        return Let(
            line=p.lineno,
            column=self._get_column_from_production(p),
            let_list=p.let_list,
            expr=p.expr
        )

    @_('let_expr "," let_list')
    def let_list(self, p: YaccProduction):
        return [p.let_expr] + p.let_list
    
    @_('let_expr')
    def let_list(self, p: YaccProduction):
        return [p.let_expr]

    @_('ID ":" TYPE ASSIGN expr')
    def let_expr(self, p: YaccProduction):
        return Initialization(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE,
            expr=p.expr
        )

    @_('ID ":" TYPE')
    def let_expr(self, p: YaccProduction):
        return Declaration(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE
        )

    @_('CASE expr OF cases ESAC')
    def expr(self, p: YaccProduction):
        return Case(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
            cases=p.cases
        )   

    @_('case ";" cases')
    def cases(self, p: YaccProduction):
        return [p.case] + p.cases

    @_('case ";"')
    def cases(self, p: YaccProduction):
        return [p.case]

    @_('ID ":" TYPE DARROW expr')
    def case(self, p: YaccProduction):
        return Case_expr(
            line=p.lineno,
            column=self._get_column_from_production(p),
            id=p.ID,
            type=p.TYPE,
            expr=p.expr
        )

    @_('ISVOID expr')
    def expr(self, p: YaccProduction):
        return Isvoid(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr
        )

    @_('expr PLUS expr')
    def expr(self, p: YaccProduction):
        return Add(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )

    @_('expr MINUS expr')
    def expr(self, p: YaccProduction):
        return Sub(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )

    @_('expr TIMES expr')
    def expr(self, p: YaccProduction):
        return Times(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )

    @_('expr DIVIDE expr')
    def expr(self, p: YaccProduction):
        return Div(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )

    @_('expr LESS expr')
    def expr(self, p: YaccProduction):
        return Less(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )

    @_('expr LESSEQUAL expr')
    def expr(self, p: YaccProduction):
        return LessEqual(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )
    
    @_('expr EQUAL expr')
    def expr(self, p: YaccProduction):
        return Equal(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr1=p.expr0,
            expr2=p.expr1
        )

    @_('NOT expr')
    def expr(self, p: YaccProduction):
        return Not(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
        )
    
    @_('BITWISE expr')
    def expr(self, p: YaccProduction):
        return Bitwise(
            line=p.lineno,
            column=self._get_column_from_production(p),
            expr=p.expr,
        )

    @_('NUMBER')
    def expr(self, p: YaccProduction):
        return Interger(line=p.lineno, column=self._get_column_from_production(p), value=p.NUMBER)
    
    @_('STRING')
    def expr(self, p: YaccProduction):
        return String(line=p.lineno, column=self._get_column_from_production(p), value=p.STRING)
    
    @_('"(" expr ")"')
    def expr(self, p: YaccProduction):
        return p.expr
    
    @_('ID')
    def expr(self, p: YaccProduction):
        return GetVariable(line=p.lineno, column=self._get_column_from_production(p), id=p.ID)
    
    @_('TRUE')
    def expr(self, p: YaccProduction):
        return Boolean(line=p.lineno, column=self._get_column_from_production(p), value=True)

    @_('FALSE')
    def expr(self, p: YaccProduction):
        return Boolean(line=p.lineno, column=self._get_column_from_production(p), value=False)

    def error(self, p: Token):
        rename = CoolLexer.rename
        if p:
            if isinstance(p.value, str) and p.value.lower() in rename:
                self.errors.append(
                    Error.error(
                        line=p.lineno,
                        column=p.column,
                        error_type="SyntacticError",
                        message=f"ERROR at or near {rename[p.value.lower()]}"
                    )
                )
            else:
                self.errors.append(
                    Error.error(
                        line=p.lineno,
                        column=p.column,
                        error_type="SyntacticError",
                        message=f"ERROR at or near \"{p.value}\""
                    )
                )
        else:
            self.errors.append(
                    Error.error(
                    line=0,
                    column=0,
                    error_type="SyntacticError",
                    message=f"ERROR at or near EOF"
                )
            )
    
    def parse(self, tokens: List[Token]):
        return super().parse((t for t in tokens)), self.errors


