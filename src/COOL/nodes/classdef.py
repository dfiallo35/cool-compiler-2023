from typing import List

from COOL.codegen.mips_visitor import MipsVisitor
from COOL.semantic.visitor import Visitor_Program
from COOL.semantic.visitor import Visitor_Class

from COOL.nodes import Node
from COOL.nodes.feature import Method
from COOL.nodes.feature import Attribute


class Class(Node):
    def __init__(
        self,
        line: int,
        column: dict,
        features: List[Method | Attribute],
        type: str,
        inherits: str = None
    ) -> None:
        self.type = type
        self.inherits = inherits
        self.features = features
        self.methods = [i for i in features if isinstance(i, Method)]
        self.attributes = [i for i in features if isinstance(i, Attribute)]
        self.inherits_instance: Class = None
        super().__init__(line,column)
    
    def codegen(self, mips_visitor: MipsVisitor):
        mips_visitor.visit_class(self)
        for attribute in self.attributes:
            attribute.codegen(mips_visitor)
        for method in self.methods:
            method.codegen(mips_visitor)
        mips_visitor.unvisit_class(self)

    def check(self, visitor:Visitor_Program):
        visitor.visit_class(self)
