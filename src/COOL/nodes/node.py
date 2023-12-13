from abc import ABC
from abc import abstractmethod
from typing import Any

from COOL.codegen.mips_visitor import MipsVisitor


class Node(ABC):
    '''
    Base class for tokens.
    '''
    line: int
    column: int

    def __init__(self, line: int, column: int) -> None:
        self.line = line
        self.column = column

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.codegen(*args, **kwds)

    @abstractmethod
    def codegen(self, mips_visitor: MipsVisitor):
        pass

    @abstractmethod
    def check(self):
        pass

    def get_return(self, mips_visitor: MipsVisitor) -> str:
        pass

    def first_elem(self):
        return self.column

