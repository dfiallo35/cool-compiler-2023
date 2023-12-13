from typing import List

from COOL.codegen.mips_visitor import MipsVisitor
from COOL.semantic.visitor import Visitor_Program, Visitor_Class

from COOL.nodes import Node
from COOL.nodes.classdef import Class


class Program(Node):
    def __init__(self, classes: List[Class]) -> None:
        self.visitor = Visitor_Program()
        self.classes = classes

    def codegen(self, mips_visitor: MipsVisitor) -> str:   
        mips_visitor.visit_program(self)     
        for _class in self.classes:
            _class.codegen(mips_visitor)
        mips_visitor.unvisit_program(self)

    def check(self):
        try:
            self.visitor.visit_program(self)

            for class_ in self.classes:
                if class_:
                    if class_.inherits and class_.inherits in self.visitor.types.keys() and not  class_.inherits in self.visitor.basic_types.keys():
                        class_.inherits_instance = self.visitor.types[class_.inherits] 
            
            for _class in self.classes:
                if _class:
                    _class.check(self.visitor)

            for _class in self.classes:
                class_visitor =  Visitor_Class( scope= {
                    'type': _class.type, 
                    'inherits': _class.inherits, 
                    'features': _class.features_dict, 
                    'methods': _class.methods_dict, 
                    'attributes': _class.attributes_dict, 
                    'inherits_instance': _class.inherits_instance, 
                    'line': _class.line, 
                    'column': _class.column,
                    'lineage': _class.lineage,
                    'all_types':self.visitor.types,
                    'inheritance_tree':self.visitor.tree,
                    'basic_types':self.visitor.basic_types,
                    'type': _class.type
                    })
                for feature in _class.features:
                    feature.check(class_visitor)

        except Exception as e:
            return [e]
        