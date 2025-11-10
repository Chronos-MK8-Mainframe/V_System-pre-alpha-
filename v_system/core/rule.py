"""Rule system with ternary logic"""

from typing import Callable, List
from v_system.core.symbolic_expr import SymbolicExpression
from v_system.core.context import Context, ContextBundle, Reference


class Rule:
    """Conditional transformation with three-valued logic"""
    
    def __init__(self, 
                 rule_id: str,
                 condition: Callable[[SymbolicExpression, ContextBundle, List[Reference]], int],
                 transform: Callable[[SymbolicExpression], SymbolicExpression],
                 domain: Context,
                 priority: int,
                 confidence: float = 1.0,
                 source: str = "hardcoded"):
        self.id = rule_id
        self.condition = condition
        self.transform = transform
        self.domain = domain
        self.priority = priority
        self.confidence = confidence
        self.source = source
        self.application_count = 0
        self.success_count = 0
    
    def is_applicable(self, expr: SymbolicExpression,
                     context_bundle: ContextBundle,
                     refs: List[Reference]) -> int:
        """
        Check if rule applies to expression
        Returns: 1=applicable, 0=not applicable, -1=undefined
        """
        try:
            return self.condition(expr, context_bundle, refs)
        except Exception:
            return -1
    
    def apply(self, expr: SymbolicExpression) -> SymbolicExpression:
        """Apply transformation to expression"""
        self.application_count += 1
        try:
            result = self.transform(expr)
            self.success_count += 1
            return result
        except Exception:
            return expr
    
    def copy(self):
        """Create a copy of this rule"""
        return Rule(
            self.id, self.condition, self.transform,
            self.domain, self.priority, self.confidence, self.source
        )
    
    def __repr__(self):
        return f"Rule({self.id}, pri={self.priority}, conf={self.confidence:.2f})"
