import extensions
from Modules.Types import *

def validate_input(input:str) -> bool:
    if input.isspace():
        return False
    return True

def compare_input() ->  bool:
    return