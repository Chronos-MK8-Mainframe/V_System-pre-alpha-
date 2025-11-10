"""Contradiction detection"""

from enum import Enum
from dataclasses import dataclass

from v_system.core.rule import Rule
from v_system.core.context import Context


class ConflictType(Enum):
    DIRECT_NEGATION = "direct_negation"
    CONTEXT_OVERLAP = "context_overlap"
    SPECIAL_GENERAL = "special_general"
    NONE = "none"


@dataclass
class ConflictResult:
    exists: bool
    type: ConflictType
    description: str = ""
    overlap_score: float = 0.0


class HeuristicContradictionDetector:
    """Fast heuristic-based contradiction detection"""
    
    def __init__(self):
        self.inverse_pairs = {
            ("expand", "factor"), ("simplify", "complicate"),
            ("differentiate", "integrate"), ("add", "subtract"),
            ("multiply", "divide")
        }
        self.failure_count = 0
    
    def detect(self, rule1: Rule, rule2: Rule) -> ConflictResult:
        """Detect contradictions between rules"""
        
        # Check 1: Inverse operations
        if self._are_inverse_operations(rule1.id, rule2.id):
            if self._contexts_overlap(rule1.domain, rule2.domain):
                return ConflictResult(
                    exists=True,
                    type=ConflictType.DIRECT_NEGATION,
                    description=f"Rules {rule1.id} and {rule2.id} are inverse operations"
                )
        
        # Check 2: Context overlap with priority conflict
        context_similarity = rule1.domain.similarity(rule2.domain)
        if context_similarity > 0.7:
            if self._have_priority_conflict(rule1, rule2):
                return ConflictResult(
                    exists=True,
                    type=ConflictType.CONTEXT_OVERLAP,
                    description="Rules conflict in overlapping context",
                    overlap_score=context_similarity
                )
        
        # Check 3: Special-general relationship
        if self._is_special_case(rule1.id, rule2.id):
            return ConflictResult(
                exists=True,
                type=ConflictType.SPECIAL_GENERAL,
                description=f"{rule1.id} may be special case of {rule2.id}"
            )
        
        return ConflictResult(False, ConflictType.NONE)
    
    def _are_inverse_operations(self, id1: str, id2: str) -> bool:
        """Check if rule IDs indicate inverse operations"""
        id1_lower, id2_lower = id1.lower(), id2.lower()
        for op1, op2 in self.inverse_pairs:
            if (op1 in id1_lower and op2 in id2_lower) or \
               (op2 in id1_lower and op1 in id2_lower):
                return True
        return False
    
    def _contexts_overlap(self, ctx1: Context, ctx2: Context) -> bool:
        """Check if contexts overlap significantly"""
        return ctx1.similarity(ctx2) > 0.5
    
    def _have_priority_conflict(self, rule1: Rule, rule2: Rule) -> bool:
        """Check if rules have same priority (potential conflict)"""
        return rule1.priority == rule2.priority and rule1.id != rule2.id
    
    def _is_special_case(self, id1: str, id2: str) -> bool:
        """Check if one rule is a special case of another"""
        return "specific" in id1.lower() and "general" in id2.lower()
