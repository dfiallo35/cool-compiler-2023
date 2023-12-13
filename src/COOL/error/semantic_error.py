

class SemError(Exception):
    def __init__(self, line:int, column:int, type:str, message:str ) -> None:

        self.message = f"({line}, {column}) - {type}: {message}"

        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message