from abc import abstractmethod

from COOL.nodes import Node

from COOL.codegen.utils import Instruction
from COOL.codegen.utils import Comment
from COOL.codegen.utils import Label
from COOL.codegen.mips_visitor import MipsVisitor


class UnaryOperator(Node):
    def __init__(self, line: int, column: dict, expr: Node, possibles_types:list, return_type:str, symbol:str) -> None:
        self.expr: Node = expr
        self.possibles_types = possibles_types
        self.return_type = return_type
        self.symbol = symbol
        super().__init__(line, column)

    def first_elem(self):
        return self.expr

    def codegen(self, mips_visitor: MipsVisitor) -> str:
        expr = self.expr.codegen(mips_visitor)
        operation = self.operation(mips_visitor)
        result = [
            *expr,
            Instruction("lw", "$t0", "4($t0)"),
            *operation
        ]
        return result

    @abstractmethod
    def operation(self, mips_visitor: MipsVisitor) -> str:
        pass

    def check(self, visitor):
        return visitor.visit_unary_operator(self)


class Operator(Node):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node, possibles_types:list, return_type:str, symbol:str) -> None:
        self.expr1: Node = expr1
        self.expr2: Node = expr2
        self.possibles_types = possibles_types
        self.return_type = return_type
        self.symbol = symbol
        super().__init__(line, column)

    def first_elem(self):
        return self.expr1

    def codegen(self, mips_visitor: MipsVisitor) -> str:
        expr1 = self.expr1.codegen(mips_visitor)
        mips_visitor.set_offset(4)
        expr2 = self.expr2.codegen(mips_visitor)
        mips_visitor.unset_offset(4)
        operation = self.operation(mips_visitor)
        result =[
            *expr1,
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *expr2,
            # get the value from the object instance
            Instruction("lw", "$t1", "4($t0)"),
            Instruction("lw", "$t0", "0($sp)"),
            Instruction("lw", "$t0", "4($t0)"),
            *mips_visitor.deallocate_stack(4),
            *operation
        ]
        return result

    @abstractmethod
    def operation(self, mips_visitor: MipsVisitor) -> str:
        pass

    def check(self,visitor):
        return visitor.visit_operator(self)

class Add(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:
        super().__init__(line, column, expr1, expr2, ['Int'],'Int', '+')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("add", "$t0", "$t0", "$t1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Int",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class Sub(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:
        super().__init__(line, column, expr1, expr2, ['Int'],'Int', '-')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("sub", "$t0", "$t0", "$t1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Int",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class Div(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:
        super().__init__(line, column, expr1, expr2, ['Int'],'Int', '/')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("div", "$t0", "$t0", "$t1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Int",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class Times(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:
        self.possibles_types = ['Int']
        self.return_type = 'Int'
        super().__init__(line, column, expr1, expr2, ['Int'],'Int', '*')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("mul", "$t0", "$t0", "$t1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Int",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class Less(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:
        self.possibles_types = ['Int']
        self.return_type = 'Bool'
        super().__init__(line, column, expr1, expr2, ['Int'],'Bool', '<')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("slt", "$t0", "$t0", "$t1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", f"0({mips_visitor.rsp})"),
            Instruction("jal", "set_bool"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Bool",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class LessEqual(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:

        super().__init__(line, column, expr1, expr2, ['Int'],'Bool', '<=')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("slt", "$t2", "$t0", "$t1"),
            Instruction("seq", "$t3", "$t0", "$t1"),
            Instruction("or", "$t0", "$t2", "$t3"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", f"0({mips_visitor.rsp})"),
            Instruction("jal", "set_bool"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Bool",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class Equal(Operator):
    def __init__(self, line: int, column: dict, expr1: Node, expr2: Node) -> None:
        
        super().__init__(line, column, expr1, expr2, ['All'],'Bool', '=')

    def codegen(self, mips_visitor: MipsVisitor) -> str:
        expr1 = self.expr1.codegen(mips_visitor)
        mips_visitor.set_offset(4)
        expr2 = self.expr2.codegen(mips_visitor)
        mips_visitor.unset_offset(4)
        result =[
            *expr1,
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *expr2,
            Instruction("lw", "$t1", "0($sp)"),
            *mips_visitor.deallocate_stack(4),
            *mips_visitor.allocate_stack(8),
            Instruction("sw", "$t0", "0($sp)"),
            Instruction("sw", "$t1", "4($sp)"),
            Instruction("jal", "compare"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            Instruction("jal", "set_bool"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Bool",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return result

    def operation(self, mips_visitor: MipsVisitor):
        pass


class Not(UnaryOperator):
    def __init__(self, line: int, column: dict, expr: Node) -> None:
        super().__init__(line, column, expr, ['Bool'],'Bool', 'not')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("lb", "$t0", "0($t0)"),
            Instruction("xori", "$t0", "$t0", "1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", f"0({mips_visitor.rsp})"),
            Instruction("jal", "set_bool"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Bool",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj


class Bitwise(UnaryOperator):
    def __init__(self, line: int, column: dict, expr: Node) -> None:
        super().__init__(line, column, expr, ['Int'],'Int', '~')

    def operation(self, mips_visitor: MipsVisitor):
        obj = [
            Instruction("xor", "$t0", "$t0", "-1"),
            *mips_visitor.allocate_stack(4),
            Instruction("sw", "$t0", "0($sp)"),
            *mips_visitor.allocate_object(8, "Int",
                    [Instruction("lw", mips_visitor.rt, "0($sp)")]
            ),
            *mips_visitor.deallocate_stack(4),
        ]
        return obj
