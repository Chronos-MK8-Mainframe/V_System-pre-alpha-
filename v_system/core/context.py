"""Context system for domain classification"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field

from v_system.core.symbolic_expr import SymbolicExpression


@dataclass
class Context:
    """Computational context descriptor"""
    domain: str
    subdomain: Optional[str] = None
    features: Dict[str, Any] = field(default_factory=dict)
    
    def similarity(self, other: 'Context') -> float:
        """Compute semantic similarity"""
        if self.domain != other.domain:
            return 0.0
        if self.subdomain == other.subdomain:
            return 1.0
        if self.subdomain and other.subdomain:
            return 0.5
        return 0.7
    
    def __eq__(self, other):
        return self.domain == other.domain and self.subdomain == other.subdomain
    
    def __hash__(self):
        return hash((self.domain, self.subdomain))


@dataclass
class Reference:
    """Read-only reference to parallel V' output"""
    output: SymbolicExpression
    context: Context
    alignment: Callable[[Context], float]
    operation_type: str
    bias_signature: str


@dataclass
class ContextBundle:
    """Complete context for rule evaluation"""
    parallel_outputs: List[SymbolicExpression]
    parallel_contexts: List[Context]
    parallel_operations: List[str]
    original_input: SymbolicExpression
    transformation_history: List[SymbolicExpression]
    current_context: Context
    layer_position: int
    column_position: int


class ContextInference:
    """Infer computational context from expressions"""
    
    def __init__(self):
        # Domain vocabularies
        self.domain_symbols = {
            "math": {"x", "y", "z", "a", "b", "c", "n", "m", "i", "j"},
            "physics": {"v", "t", "F", "m", "a", "E", "p", "h"},
            "calculus": {"dx", "dy", "dt", "integral", "derivative"},
        }
        
        self.domain_operators = {
            "algebra": {"+", "-", "*", "/", "^"},
            "calculus": {"d/dx", "∫", "lim"},
            "logic": {"∧", "∨", "¬", "→"},
        }
    
    def infer_context(self, expr: SymbolicExpression, 
                     history: Optional[List[SymbolicExpression]] = None) -> Context:
        """Infer context from expression features"""
        
        symbols = expr.symbols()
        operators = expr.operators()
        
        # Score each domain
        scores = {}
        
        # Math/Algebra is default
        scores[("math", "algebra")] = 5.0
        
        # Check symbol overlap
        for domain, vocab in self.domain_symbols.items():
            overlap = len(symbols & vocab)
            if overlap > 0:
                scores[(domain, None)] = scores.get((domain, None), 0) + overlap * 2.0
        
        # Check operator signatures
        if "^" in operators or "**" in operators:
            scores[("math", "algebra")] = scores.get(("math", "algebra"), 0) + 3.0
        
        if "/" in operators and "*" in operators:
            scores[("math", "algebra")] = scores.get(("math", "algebra"), 0) + 2.0
        
        # Calculus indicators
        if any(s in str(expr) for s in ["d/dx", "integral", "derivative"]):
            scores[("math", "calculus")] = 10.0
        
        # Use history for context continuity
        if history:
            prev_context = self.infer_context(history[-1])
            scores[(prev_context.domain, prev_context.subdomain)] = \
                scores.get((prev_context.domain, prev_context.subdomain), 0) + 3.0
        
        # Select best
        if not scores:
            return Context("math", "algebra")
        
        best_domain, best_subdomain = max(scores.items(), key=lambda x: x[1])[0]
        return Context(best_domain, best_subdomain)
