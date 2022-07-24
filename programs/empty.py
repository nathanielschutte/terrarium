

from .src import program

class EmptyProgram(program.Program):
    
    def __init__(self, width, height, options) -> None:
        super().__init__(width, height, options)
    