import sys
module = "./src/"
sys.path.append(module)


from src.COOL.nodes.program import *
from src.COOL.nodes.feature import Method, Attribute


a = Attribute(1, 54, type='object', id='a')
b = Attribute(2, 65, type='String', id='b')
c = Attribute(3, 234, type='A', id='c')
d = Attribute(4, 32, type='Int', id='d')
ma = Method(5, 45, type='object', id='al', formals=[], expr=None)
mb = Method(6, 67, type='A', id='b', formals=[], expr=None)
mc = Method(7, 8, type='object', id='cd', formals=[], expr=None)

classa = Class(1, 34, [a, ma, mc], "A")
classb = Class(10, 34, [b, c], "B", "A")
classc = Class(100, 4, [], "C", "B")
classd = Class(1000, 34, [], "D", "A")

prog = Program(classes=[classa, classb, classc, classd])

# prog.check()
