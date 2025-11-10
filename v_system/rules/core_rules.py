"""Core algebraic rules with actual transforms"""

from typing import List

from v_system.core.rule import Rule
from v_system.core.context import Context
from v_system.core.symbolic_expr import Add, Mul, Num


def create_core_rules() -> List[Rule]:
    """
    Create functional algebraic rules that actually transform expressions
    
    Returns:
        List of core Rule objects with working transformations
    """
    
    # Rule 1: Identity Addition - x + 0 → x
    def identity_add_cond(expr, ctx, refs):
        if expr.op == '+' and len(expr.args) == 2:
            if expr.args[1].op == 0:
                return 1
        return 0
    
    def identity_add_trans(expr):
        return expr.args[0].copy()
    
    # Rule 2: Identity Addition (reversed) - 0 + x → x
    def identity_add_rev_cond(expr, ctx, refs):
        if expr.op == '+' and len(expr.args) == 2:
            if expr.args[0].op == 0:
                return 1
        return 0
    
    def identity_add_rev_trans(expr):
        return expr.args[1].copy()
    
    # Rule 3: Identity Multiplication - x * 1 → x
    def identity_mul_cond(expr, ctx, refs):
        if expr.op == '*' and len(expr.args) == 2:
            if expr.args[1].op == 1:
                return 1
        return 0
    
    def identity_mul_trans(expr):
        return expr.args[0].copy()
    
    # Rule 4: Identity Multiplication (reversed) - 1 * x → x
    def identity_mul_rev_cond(expr, ctx, refs):
        if expr.op == '*' and len(expr.args) == 2:
            if expr.args[0].op == 1:
                return 1
        return 0
    
    def identity_mul_rev_trans(expr):
        return expr.args[1].copy()
    
    # Rule 5: Zero Multiplication - x * 0 → 0 or 0 * x → 0
    def zero_mul_cond(expr, ctx, refs):
        if expr.op == '*' and len(expr.args) == 2:
            if expr.args[0].op == 0 or expr.args[1].op == 0:
                return 1
        return 0
    
    def zero_mul_trans(expr):
        return Num(0)
    
    # Rule 6: Commutative Addition - sort alphabetically
    def comm_add_cond(expr, ctx, refs):
        if expr.op == '+' and len(expr.args) == 2:
            a, b = expr.args
            # Apply if not in alphabetical order
            if str(a.op) > str(b.op):
                return 1
        return 0
    
    def comm_add_trans(expr):
        return Add(expr.args[1], expr.args[0])
    
    # Rule 7: Commutative Multiplication - sort alphabetically
    def comm_mul_cond(expr, ctx, refs):
        if expr.op == '*' and len(expr.args) == 2:
            a, b = expr.args
            if str(a.op) > str(b.op):
                return 1
        return 0
    
    def comm_mul_trans(expr):
        return Mul(expr.args[1], expr.args[0])
    
    math_algebra = Context("math", "algebra")
    
    return [
        Rule("identity_add", identity_add_cond, identity_add_trans,
             math_algebra, priority=10, confidence=1.0, source="core"),
        Rule("identity_add_rev", identity_add_rev_cond, identity_add_rev_trans,
             math_algebra, priority=10, confidence=1.0, source="core"),
        Rule("identity_mul", identity_mul_cond, identity_mul_trans,
             math_algebra, priority=9, confidence=1.0, source="core"),
        Rule("identity_mul_rev", identity_mul_rev_cond, identity_mul_rev_trans,
             math_algebra, priority=9, confidence=1.0, source="core"),
        Rule("zero_mul", zero_mul_cond, zero_mul_trans,
             math_algebra, priority=8, confidence=1.0, source="core"),
        Rule("commutative_add", comm_add_cond, comm_add_trans,
             math_algebra, priority=7, confidence=1.0, source="core"),
        Rule("commutative_mul", comm_mul_cond, comm_mul_trans,
             math_algebra, priority=7, confidence=1.0, source="core"),
    ]
