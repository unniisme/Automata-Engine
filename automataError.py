
class AutomataError(Exception):

    INVALID_STATE = "Invalid State"
    INVALID_TRANSITION = "Invalid Transition"
    NON_CLOSURE = "Invalid Automata"


    def __init__(self, ercode, defaulter = None):
        self.defaulter = defaulter