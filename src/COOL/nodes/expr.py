from typing import List

from COOL.nodes import Node
from COOL.semantic.visitor import Visitor_Class


class Dispatch(Node):
    def __init__(self, line: int, column: int, expr: Node, id: str, type: str = None, exprs: List[Node] = None):
        self.expr: Node = expr
        self.id: str = id
        self.type: str = type
        self.exprs: List[Node] = exprs
        super().__init__(line, column)

    def check(self, visitor:Visitor_Class):
        return visitor.visit_dispatch(self)

    def codegen(self):
        raise NotImplementedError()


class CodeBlock(Node):
    def __init__(self, line: int, column: int, exprs: List[Node]):
        self.exprs: List[Node] = exprs
        super().__init__(line, column)

    def check(self,visitor:Visitor_Class):
        return visitor.visit_code_block(self)

    def codegen(self):
        raise NotImplementedError()

class If(Node):
    def __init__(self, line: int, column: int, if_expr: Node, then_expr: Node, else_expr: Node):
        self.if_expr: Node = if_expr
        self.then_expr: Node = then_expr
        self.else_expr: Node = else_expr
        super().__init__(line, column)

    def check(self, visitor):
        return visitor.visit_conditionals(self)
    def codegen(self):
        raise NotImplementedError()


class While(Node):
    def __init__(self, line: int, column: int, while_expr: Node, loop_expr: Node):
        self.while_expr: Node = while_expr
        self.loop_expr: Node = loop_expr
        super().__init__(line, column)

    def check(self, visitor):
        return visitor.visit_loops(self)
    
    def codegen(self):
        raise NotImplementedError()


class Let(Node):
    def __init__(self, line: int, column: int, let_list: List[Node], expr: Node):
        self.let_list: List[Node] = let_list
        self.expr: Node = expr
        super().__init__(line, column)

    def check(self, visitor):
        return visitor.visit_let(self)

    def codegen(self):
        raise NotImplementedError()


class Case(Node):
    def __init__(self, line: int, column: int, expr: Node, cases: List[Node]):
        self.expr: Node = expr
        self.cases: List[Node] = cases
        super().__init__(line, column)

    def check(self, visitor):
        return visitor.visit_case(self)
    
    def codegen(self):
        raise NotImplementedError()

class Case_expr(Node):
    def __init__(self, line: int, column: int, id:str, type:str, expr:Node) -> None:
        self.id = id
        self.type = type
        self.expr = expr
        super().__init__(line, column)

    def check(self, visitor):
        return visitor.visit_case_expr(self)
    
    def codegen(self):
        raise NotImplementedError()

class New(Node):
    def __init__(self, line: int, column: int, type: str):
        self.type: str = type
        super().__init__(line, column)

    def check(self,visitor:Visitor_Class):
        return visitor.visit_new(self)

    def codegen(self):
        raise NotImplementedError()


class Isvoid(Node):
    def __init__(self, line: int, column: int, expr: Node):
        self.expr: Node = expr
        super().__init__(line, column)

    def check(self, visitor):
        return visitor.visit_isvoid(self)

    def codegen(self):
        raise NotImplementedError()
    
# class Self(Node):
#     def __init__(self, line: int, column: int):
#         super().__init__(line, column)

#     def check(self, visitor):
#         return visitor.visit_self(self)

    def codegen(self):
        raise NotImplementedError()
