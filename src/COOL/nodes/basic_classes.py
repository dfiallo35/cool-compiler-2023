from typing import List
from COOL.nodes.feature import Method, Formal, Attribute


class BasicObject:
    def __init__(self, features:list = [], type:str = 'Object', inherits:str = None, lineage:list = []) -> None:
        self.features:list = [
            Method(line=0, column=0, id='abort', type='Object', expr=None, formals=[]),
            Method(line=0, column=0, id='type_name', type='String', expr=None, formals=[]),
            Method(line=0, column=0, id='copy', type='SELF_TYPE', expr=None, formals=[])
        ] + features
        self.inherits: str = inherits
        self.lineage = lineage
        self.type: str = type
        self.methods = [i for i in self.features if isinstance(i, Method)]
        self.attributes = [i for i in self.features if isinstance(i, Attribute)]
        self.methods_dict = {i.id:i for i in self.features if isinstance(i, Method)}
        self.attributes_dict = {i.id:i for i in self.features if isinstance(i, Attribute)}


    def check(self, visitor):
        return self.type


class BasicIO(BasicObject):
    def __init__(self) -> None:
        features:list = [
            Method(line=0, column=0, id='out_string', type='IO', expr=None, formals=[Formal(line=0, column=0, id='x', type='String')]),
            Method(line=0, column=0, id='out_int', type='IO', expr=None, formals=[Formal(line=0, column=0, id='x', type='Int')]),
            Method(line=0, column=0, id='in_string', type='String', expr=None, formals=[]),
            Method(line=0, column=0, id='in_int', type='Int', expr=None, formals=[])
        ]
        self.inherits: str = 'Object'
        self.type: str = 'IO'
        self.lineage = ['Object']
        super().__init__(features, self.type, self.inherits, self.lineage)


class BasicString(BasicObject):
    def __init__(self) -> None:
        features:list = [
                Method(line=0, column=0, id='length', type='Int', expr=None, formals=[]),
                Method(line=0, column=0, id='concat', type='String', expr=None, formals=[Formal(line=0, column=0, id='s', type='String')]),
                Method(line=0, column=0, id='substr', type='String', expr=None, formals=[Formal(line=0, column=0, id='i', type='Int'),Formal(line=0, column=0, id='l', type='Int')])
        ]
        self.lineage = ['Object']
        self.inherits: str = 'Object'
        self.type: str = 'String'
        super().__init__(features, self.type, self.inherits, self.lineage)

class BasicBool(BasicObject):
    def __init__(self) -> None:
        features:list = []
        self.inherits: str = 'Object'
        self.type: str = 'Bool'
        self.lineage = ['Object']

        super().__init__(features, self.type, self.inherits, self.lineage)


class BasicInt(BasicObject):
    def __init__(self) -> None:
        features:list = []
        self.inherits: str = 'Object'
        self.type: str = 'Int'
        self.lineage = ['Object']
        super().__init__(features, self.type, self.inherits, self.lineage)

