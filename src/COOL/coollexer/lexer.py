import re
from typing import Tuple
from typing import List
from sly import Lexer
from sly.lex import Token as SlyToken

from COOL.tokens import Token
from COOL.error import Error


class CoolLexer(Lexer):
    def __init__(self):
        super().__init__()
        self.index = 0
        self.errors = []

    tokens = {
        # Symbols
        "NUMBER", "STRING", "TYPE", "ID", 
        # Arithmetic Operators
        "PLUS", "MINUS", "TIMES", "DIVIDE", "LESS", "LESSEQUAL", "EQUAL", "NOT", "BITWISE", "ASSIGN", "DARROW",
        # Reserved words
        'CLASS', "INHERITS", "IF", "THEN", "ELSE", "FI", "WHILE", "LOOP", "POOL", "LET", "IN", "CASE", "OF", "ESAC", "NEW", "ISVOID", "TRUE", "FALSE",
    }
    literals = {"(", ")", "{", "}", ";", ":", ",", ".", "@"}
    keywords = {
        'class', 'inherits', 'if', 'then', 'else', 'fi', 'while', 'loop', 'pool', 'let', 'in', 'case', 'of', 'esac', 'new', 'isvoid', 
    }
    special_keywords = {'true', 'false'}
    rename = {
        "=>": "DARROW", "<-": "ASSIGN",
        "class": "CLASS", "inherits": "INHERITS", "if": "IF", "then": "THEN", "else": "ELSE", "fi": "FI", "while": "WHILE", "loop": "LOOP", "pool": "POOL", "let": "LET", "in": "IN", "case": "CASE", "of": "OF", "esac": "ESAC", "new": "NEW", "isvoid": "ISVOID",
    }

    ignore = " \t"
    ignore_comment = r'--.*'
    
    ignore_comment_multiline = r'\(\*'
    def ignore_comment_multiline(self, t):
        nested_comments = 1
        while True:
            text = self.text[self.index:]
            newline = re.match(r'\n+', text)
            if newline:
                self.lineno += newline.group().count("\n")
                self.index += newline.end()
            elif re.match(r'\(\*', text):
                nested_comments += 1
                self.index += 2
            elif re.match(r'\*\)', text):
                nested_comments -= 1
                self.index += 2
                if nested_comments == 0:
                    break
            else:
                self.index += 1
                if self.index >= len(self.text):
                    self.errors.append(
                        Error.error(
                            line=self.lineno,
                            column=self.find_column(self.text, self.index),
                            error_type="LexicographicError",
                            message="EOF in comment"
                        )
                    )
                    break
    
    # Newline
    newline = r'\n+'
    def newline(self, t):
        self.lineno += t.value.count("\n")

    # Arithmetic Operators
    PLUS = r"\+"
    MINUS = r"-"
    TIMES = r"\*"
    DIVIDE = r"/"
    ASSIGN = r"<-"
    LESSEQUAL = r"<="
    LESS = r"<"
    DARROW = r"=>"
    EQUAL = r"="
    NOT = r"not"
    BITWISE= r"~"

    # Symbols
    TYPE = r'[A-Z][a-zA-Z0-9_]*'
    def TYPE(self, t):
        if t.value.lower() in self.keywords:
            t.type = t.value.upper()
        elif t.value.lower() in self.special_keywords:
            t.type = t.value.upper()
        return t

    ID = r'[a-z][a-zA-Z0-9_]*'
    def ID(self, t):
        if t.value.lower() in self.keywords:
            t.type = t.value.upper()
        elif t.value.lower() in self.special_keywords:
            t.type = t.value.upper()
        return t

    NUMBER = r'\d+'
    def NUMBER(self, t):
        t.value = int(t.value)
        return t
    
    STRING = r'\"'
    def STRING(self, t):
        string = ""
        while True:
            text = self.text[self.index:]
            if re.match(r'\\"', text):
                self.index += 2
                #FIX
                string += "\""
            elif re.match(r'\\', text) and re.match(r'\n', text[1:]):
                self.index += 2
                self.lineno += 1
                string += "\\\n"
            elif re.match(r'"', text):
                self.index += 1
                t.value = string
                return t
            else:
                if self.index >= len(self.text):
                    self.errors.append(
                        Error.error(
                            line=self.lineno,
                            column=self.find_column(self.text, self.index),
                            error_type="LexicographicError",
                            message="EOF in string constant"
                        )
                    )
                    break
                elif self.text[self.index] == "\n":
                    self.errors.append(
                        Error.error(
                            line=self.lineno,
                            column=self.find_column(self.text, self.index),
                            error_type="LexicographicError",
                            message="Unterminated string constant"
                        )
                    )
                    self.lineno += 1
                    self.index += 1
                    break
                elif '\x00' == text[0]:
                    string += text[0]
                    self.errors.append(
                        Error.error(
                            line=self.lineno,
                            column=self.find_column(self.text, self.index),
                            error_type="LexicographicError",
                            message="String contains null character"
                        )
                    )
                    self.index += 1
                else:
                    self.index += 1
                    string += text[0]

    # Error handling rule
    def error(self, t: SlyToken):
        self.index += 1
        self.errors.append(
            Error.error(
                line=self.lineno,
                column=self.find_column(self.text, t.index),
                error_type="LexicographicError",
                message=f"Error \"{t.value[0]}\""
            )
        )

    def find_column(self, text: str, index: int):
        last_cr = text.rfind('\n', 0, index)
        tabs = text.count('\t', last_cr, index)
        if last_cr < 0:
            last_cr = 0
        column = (index - last_cr) + tabs * 3
        return column if column > 0 else 1
    
    def generate_token(self, token: SlyToken, text: str):
        new_token = Token()
        new_token.column = self.find_column(text, token.index)
        new_token.type = token.type
        new_token.value = token.value
        new_token.lineno = token.lineno
        new_token.index = token.index
        new_token.end = token.end
        return new_token

    def tokenize(self, text: str) -> Tuple[List[Token], List[Error]]:
        return [self.generate_token(t, text) for t in super().tokenize(text)], self.errors
