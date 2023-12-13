import os
from pathlib import Path
import sys
module = "./src/"
sys.path.append(module)

from src.COOL import CoolLexer
from src.COOL import CoolParser
from src.COOL import Semantic
from src.COOL import Codegen
from src.COOL.utils import load_file


def check_errors(errors):
    if errors:
        for error in errors:
            print(error)
        

def test_errors(cls, out):
    for _cl, _out in zip(cls, out):
        loaded_file = load_file(_cl)
        # with open(_out, "r") as f:
        #     expected = f.readlines()
        
        lexer = CoolLexer()
        
        print(f"Testing {Path(_cl).name}:")
        print("Expected:")
        # for line in expected:
        #     print(f"{line.strip()}")
        
        print("Got:")
        tokens, errors = lexer.tokenize(loaded_file)
        # check_errors(errors)

        parser = CoolParser()
        ast, errors = parser.parse(tokens)
        check_errors(errors)

        # errors = Semantic.check(ast)
        # check_errors(errors)
        print()

def test_codegen(cls, out, inp):
    for _cl, _out, _inp in zip(cls, out, inp):
        loaded_file = load_file(_cl)
        
        print(f"Testing {Path(_cl).name}:\n")
        
        lexer = CoolLexer()
        tokens, errors = lexer.tokenize(loaded_file)

        parser = CoolParser()
        ast, errors = parser.parse(tokens)

        errors = Semantic.check(ast)

        mips_script = Codegen.codegen(ast)
        print(mips_script)
        break


def test_codegen_file(file):
    loaded_file = load_file(file)
    print(f"Testing {Path(file).name}:\n")
    
    lexer = CoolLexer()
    tokens, errors = lexer.tokenize(loaded_file)
    check_errors(errors)

    parser = CoolParser()
    ast, errors = parser.parse(tokens)
    check_errors(errors)

    errors = Semantic.check(ast)
    check_errors(errors)

    mips_script = Codegen.codegen(ast)
    # print(mips_script)
    output_file = file[:-2] + "mips"
    with open(output_file, "w") as f:
        f.write(mips_script)



if __name__ == "__main__":
    # Testing lexer, parser and semantic
    # folder = "./tests/semantic/"
    # files = sorted([os.path.join(folder, f) for f in os.listdir(folder)])
    # cls = [f for f in files if f.endswith(".cl")]
    # out = [f[:-3] + "_error.txt" for f in cls]
    # test_errors(cls, out)


    # Testing codegen
    # folder = "./tests/codegen/"
    # files = sorted([os.path.join(folder, f) for f in os.listdir(folder)])
    # cls = [f for f in files if f.endswith(".cl")]
    # out = [f[:-3] + "_output.txt" for f in cls]
    # inp = [f[:-3] + "_input.txt" for f in cls]
    # test_codegen(cls, out, inp)

    # Testing one file

    # TODO:
    # file = "./tests/codegen/arith.cl"
    # file = "./tests/codegen/book_list.cl"
    # file = "./tests/codegen/hairyscary.cl"
    

    # OK:
    # file = "./tests/codegen/list.cl"
    # file = "./tests/codegen/io.cl"
    # file = "./tests/codegen/complex.cl"
    # file = "./tests/codegen/print-cool.cl"
    # file = "./tests/codegen/new_complex.cl"
    # file = "./tests/codegen/hello_world.cl"
    # file = "./tests/codegen/fib.cl"
    # file = "./tests/codegen/sort-list.cl"
    # file = "./tests/codegen/primes.cl"
    # file = "./tests/codegen/atoi.cl"
    # file = "./tests/codegen/cells.cl"
    # file = "./tests/codegen/palindrome.cl"


    # CHECK:
    # file = "./tests/codegen/graph.cl"
    file = "./tests/codegen/life.cl"
    

    test_codegen_file(file)
