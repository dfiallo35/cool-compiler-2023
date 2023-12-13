

class Instruction:
    def __init__(self, opcode, *args):
        self.args = args
        self.opcode = opcode

    def __str__(self):
        return f"{INDENT}{self.opcode} {' '.join(map(str, self.args))}"
    
    def __repr__(self):
        return str(self)

class Label:
    def __init__(self, name, indent: str=""):
        self.name = name
        self.indent = indent

    def __str__(self):
        return f"{self.indent}{self.name}:"
    
    def __repr__(self):
        return str(self)

class Comment:
    def __init__(self, comment, indent: str="    "):
        self.comment = comment
        self.indent = indent

    def __str__(self):
        return f"{self.indent}# {self.comment}"
    
    def __repr__(self):
        return str(self)

class Data:
    def __init__(self, name, type, *args):
        self.name = name
        self.type = type
        self.args = args

    def __str__(self):
        return f"{self.name}:  {self.type} {', '.join(self.args)}"
    
    def __repr__(self):
        return str(self)

class Section:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return f".{self.name}"
    
    def __repr__(self):
        return str(self)

WORD = 4

NULL = "null"

TRUE = "true"

FALSE = "false"

NEWLINE = "\\n"

INDENT = "    "

INHERIANCE = {
    "Object": None,
    "IO": "Object",
    "Int": "Object",
    "String": "Object",
    "Bool": "Object",
}

CLASS_METHODS = {
    "Object":{
        "abort": "Object",
        "type_name": "String",
        "copy": "SELF_TYPE",
    },
    "IO": {
        "out_string": "SELF_TYPE",
        "out_int": "SELF_TYPE",
        "in_string": "String",
        "in_int": "Int",
    },
    "String": {
        "length": "Int",
        "concat": "String",
        "substr": "String",
    },
    "Int":{},
    "Bool":{}
}

CLASS_VARS = {
    "Object":{},
    "IO":{},
    "String":{},
    "Int":{},
    "Bool":{}
}
