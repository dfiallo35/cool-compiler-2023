from COOL.codegen.mips_visitor import MipsVisitor

class Codegen:
    @classmethod
    def codegen(cls, program) -> str:
        mips_visitor = MipsVisitor()
        program.codegen(mips_visitor)
        return mips_visitor.generate_mips()
