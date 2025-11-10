"""Provability engine"""

from typing import List

from v_system.core.rule import Rule


class ProvabilityEngine:
    """Determine if rules are provable from existing rules"""
    
    def analyze(self, candidate: Rule, existing_rules: List[Rule]) -> str:
        """
        Analyze provability of candidate rule
        
        Returns:
            'provable': Can be derived from existing rules
            'heuristic': Consistent but not provably derivable
            'unprovable': Contradicts or cannot be validated
        """
        if self._is_derivable(candidate, existing_rules):
            return "provable"
        if self._is_consistent(candidate, existing_rules):
            return "heuristic"
        return "unprovable"
    
    def _is_derivable(self, candidate: Rule, existing: List[Rule]) -> bool:
        """
        Check if candidate can be derived from existing rules
        
        Simple heuristic: check if prerequisite rule types exist
        """
        candidate_type = self._get_rule_type(candidate.id)
        existing_types = {self._get_rule_type(r.id) for r in existing}
        
        # Distributive requires commutative and associative
        if candidate_type == "distributive":
            return "commutative" in existing_types and "associative" in existing_types
        
        # Add more derivation rules here
        
        return False
    
    def _is_consistent(self, candidate: Rule, existing: List[Rule]) -> bool:
        """Check if candidate is consistent with existing rules"""
        from v_system.mee.contradiction import HeuristicContradictionDetector, ConflictType
        
        detector = HeuristicContradictionDetector()
        for rule in existing:
            conflict = detector.detect(candidate, rule)
            if conflict.exists and conflict.type == ConflictType.DIRECT_NEGATION:
                return False
        return True
    
    def _get_rule_type(self, rule_id: str) -> str:
        """Extract rule type from ID"""
        id_lower = rule_id.lower()
        for rule_type in ["commutative", "associative", "distributive",
                         "identity", "inverse", "zero"]:
            if rule_type in id_lower:
                return rule_type
        return "general"
