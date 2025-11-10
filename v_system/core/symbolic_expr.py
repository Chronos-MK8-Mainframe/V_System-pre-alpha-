"""Symbolic expression AST representation"""

from typing import Set


class SymbolicExpression:
    """AST representation of mathematical expressions"""               #all of this is experimental not final I'm working on final version but i have my boards now so it might be late
    
    def __init__(self, op: str, *args):
        self.op = op
        self.args = args
    
    def __repr__(self):
        if not self.args:
            return str(self.op)
        if len(self.args) == 1:
            return f"{self.op}({self.args[0]})"
        return f"({self.args[0]} {self.op} {self.args[1]})"
    
    def __eq__(self, other):
        if not isinstance(other, SymbolicExpression):
            return False
        return self.op == other.op and self.args == other.args
    
    def symbols(self) -> Set[str]:
        """Extract all symbols"""
        if not self.args:
            if isinstance(self.op, str) and self.op.isalpha():
                return {self.op}
            return set()
        result = set()
        for arg in self.args:
            if isinstance(arg, SymbolicExpression):
                result |= arg.symbols()
        return result
    
    def operators(self) -> Set[str]:
        """Extract all operators"""
        result = {self.op} if self.args else set()
        for arg in self.args:
            if isinstance(arg, SymbolicExpression):
                result |= arg.operators()
        return result
    
    def copy(self):
        """Deep copy of expression"""
        return SymbolicExpression(
            self.op, 
            *[arg.copy() if isinstance(arg, SymbolicExpression) else arg 
              for arg in self.args]
        )


# Helper construction functions
def Var(name: str) -> SymbolicExpression:
    """Create a variable"""
    return SymbolicExpression(name)


def Num(val: float) -> SymbolicExpression:
    """Create a numeric constant"""
    return SymbolicExpression(val)


def Add(a: SymbolicExpression, b: SymbolicExpression) -> SymbolicExpression:
    """Create addition expression"""
    return SymbolicExpression('+', a, b)


def Mul(a: SymbolicExpression, b: SymbolicExpression) -> SymbolicExpression:
    """Create multiplication expression"""
    return SymbolicExpression('*', a, b)


def Sub(a: SymbolicExpression, b: SymbolicExpression) -> SymbolicExpression:
    """Create subtraction expression"""
    return SymbolicExpression('-', a, b)


def Div(a: SymbolicExpression, b: SymbolicExpression) -> SymbolicExpression:
    """Create division expression"""
    return SymbolicExpression('/', a, b)
