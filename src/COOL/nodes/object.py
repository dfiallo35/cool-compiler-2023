from typing import Any
from COOL.codegen.mips_visitor import MipsVisitor

from COOL.nodes import Node

from COOL.codegen.utils import Instruction
from COOL.codegen.utils import Comment
from COOL.codegen.utils import Label
from COOL.codegen.utils import Data
from COOL.codegen.utils import TRUE
from COOL.codegen.utils import FALSE


class Object(Node):
    def __init__(self, line: int, column: dict, value: Any) -> None:
        self.value = value
        super().__init__(line, column)

    def check(self,visitor):
        return 'Object'


class Interger(Object):
    def __init__(self, line: int, column: dict, value: Any) -> None:
        super().__init__(line, column, value)
    
    def codegen(self, mips_visitor: MipsVisitor):
        obj = [
            *mips_visitor.allocate_object(
                8,
                "Int",
                [
                    Instruction("li", mips_visitor.rt, self.value),
                ]
            ),
        ]
        return obj

    def check(self,visitor):
        return 'Int'

    def get_return(self, mips_visitor: MipsVisitor) -> str:
        return "Int"
    


class String(Object):
    def __init__(self, line: int, column: dict, value: Any) -> None:
        super().__init__(line, column, value)
    
    def codegen(self, mips_visitor: MipsVisitor):
        str_name = "str_" + str(len(mips_visitor.data_secction))
        data = [
            Data(str_name, ".asciiz", f"\"{self.value}\"")
        ]
        mips_visitor.add_data(data)
        obj = [
            *mips_visitor.allocate_object(
                8,
                "String",
                [
                    Instruction("la", mips_visitor.rt, str_name),
                ]
            ),
        ]
        return obj
    
    def check(self,visitor):
        return 'String'
    
    def get_return(self, mips_visitor: MipsVisitor) -> str:
        return "String"


class Boolean(Object):
    def __init__(self, line: int, column: dict, value: Any) -> None:
        super().__init__(line, column, value)
    
    def codegen(self, mips_visitor: MipsVisitor):
        obj = [
            *mips_visitor.allocate_object(
                8,
                "Bool",
                [
                    Instruction("la", "$t0", TRUE if self.value else FALSE),
                ]
            ),
        ]
        return obj

    def check(self,visitor):
        return 'Bool'
    
    def get_return(self, mips_visitor: MipsVisitor) -> str:
        return "Bool"
