"""Advanced confidence scoring for rules"""

from typing import List, Dict
from collections import defaultdict
import math

from v_system.core.rule import Rule
from v_system.core.context import Context


class ConfidenceScorer:
    """Sophisticated confidence scoring for rules"""
    
    def __init__(self):
        self.scoring_history = []
        self.rule_performance = defaultdict(lambda: {'success': 0, 'total': 0})
        
        self.weights = {
            'provability': 0.3,
            'consistency': 0.25,
            'support': 0.2,
            'performance': 0.15,
            'complexity': 0.1
        }
    
    def score_rule(self, rule: Rule, existing_rules: List[Rule],
                   provability: str = "heuristic") -> Dict:
        """Comprehensive confidence scoring for a rule"""
        scores = {}
        
        scores['provability'] = self._score_provability(provability)
        scores['consistency'] = self._score_consistency(rule, existing_rules)
        scores['support'] = self._score_support(rule, existing_rules)
        scores['performance'] = self._score_performance(rule)
        scores['complexity'] = self._score_complexity(rule)
        
        final_score = sum(
            scores[component] * self.weights[component]
            for component in scores
        )
        
        final_score = self._apply_source_adjustment(final_score, rule.source)
        final_score = max(0.0, min(1.0, final_score))
        
        base_score = scores.get('provability', 0.5)
        provability_boost = scores.get('provability', 0.0) - 0.5
        consistency_boost = scores.get('consistency', 0.0) * self.weights['consistency']
        
        result = {
            'final_score': final_score,
            'base_score': base_score,
            'provability_boost': provability_boost,
            'consistency_boost': consistency_boost,
            'component_scores': scores,
            'weights': self.weights
        }
        
        self.scoring_history.append({
            'rule_id': rule.id,
            'score': final_score,
            'breakdown': scores
        })
        
        return result
    
    def _score_provability(self, provability: str) -> float:
        """Score based on provability status"""
        provability_scores = {
            'provable': 1.0,
            'heuristic': 0.7,
            'unprovable': 0.2,
            'unknown': 0.5
        }
        return provability_scores.get(provability, 0.5)
    
    def _score_consistency(self, rule: Rule, existing_rules: List[Rule]) -> float:
        """Score based on consistency with existing rules"""
        if not existing_rules:
            return 0.5
        
        from v_system.mee.contradiction import HeuristicContradictionDetector, ConflictType
        
        detector = HeuristicContradictionDetector()
        
        conflicts = 0
        supports = 0
        neutrals = 0
        
        for existing in existing_rules:
            conflict = detector.detect(rule, existing)
            
            if conflict.exists:
                if conflict.type == ConflictType.DIRECT_NEGATION:
                    conflicts += 1
                elif conflict.type == ConflictType.SPECIAL_GENERAL:
                    supports += 1
                else:
                    neutrals += 1
            else:
                neutrals += 1
        
        total = len(existing_rules)
        
        if conflicts > 0:
            consistency = 0.3 * (1 - conflicts / total)
        else:
            consistency = 0.5 + 0.5 * (supports / total if total > 0 else 0)
        
        return consistency
    
    def _score_support(self, rule: Rule, existing_rules: List[Rule]) -> float:
        """Score based on support from similar rules"""
        if not existing_rules:
            return 0.3
        
        similar_rules = [
            r for r in existing_rules
            if self._are_similar(rule, r)
        ]
        
        if not similar_rules:
            return 0.4
        
        support_score = 0.0
        
        count_support = min(1.0, len(similar_rules) / 5)
        support_score += count_support * 0.4
        
        if similar_rules:
            avg_confidence = sum(r.confidence for r in similar_rules) / len(similar_rules)
            support_score += avg_confidence * 0.4
        
        same_domain = [r for r in similar_rules if r.domain.domain == rule.domain.domain]
        domain_support = len(same_domain) / len(similar_rules) if similar_rules else 0
        support_score += domain_support * 0.2
        
        return min(1.0, support_score)
    
    def _are_similar(self, rule1: Rule, rule2: Rule) -> bool:
        """Check if two rules are similar"""
        if rule1.domain.similarity(rule2.domain) < 0.5:
            return False
        
        id1_words = set(rule1.id.lower().split('_'))
        id2_words = set(rule2.id.lower().split('_'))
        
        if not id1_words or not id2_words:
            return False
        
        overlap = len(id1_words & id2_words)
        similarity = overlap / max(len(id1_words), len(id2_words))
        
        return similarity > 0.3
    
    def _score_performance(self, rule: Rule) -> float:
        """Score based on historical performance"""
        if rule.id not in self.rule_performance:
            return 0.5
        
        perf = self.rule_performance[rule.id]
        
        if perf['total'] == 0:
            return 0.5
        
        success_rate = perf['success'] / perf['total']
        sample_confidence = min(1.0, perf['total'] / 10)
        
        return success_rate * sample_confidence + 0.5 * (1 - sample_confidence)
    
    def _score_complexity(self, rule: Rule) -> float:
        """Score based on rule complexity (simpler = better)"""
        complexity_factors = []
        
        priority_complexity = rule.priority / 10.0
        complexity_factors.append(priority_complexity)
        
        domain_features = len(rule.domain.features) if hasattr(rule.domain, 'features') else 0
        feature_complexity = min(1.0, domain_features / 5)
        complexity_factors.append(feature_complexity)
        
        id_complexity = min(1.0, len(rule.id) / 50)
        complexity_factors.append(id_complexity)
        
        avg_complexity = sum(complexity_factors) / len(complexity_factors)
        complexity_score = math.exp(-avg_complexity * 2)
        
        return complexity_score
    
    def _apply_source_adjustment(self, score: float, source: str) -> float:
        """Adjust score based on rule source"""
        source_adjustments = {
            'derived': 1.1,
            'learned': 0.95,
            'empirical': 0.9,
            'pattern_recognition': 1.0,
            'symbolic_regression': 0.95,
            'synthesized_pattern': 1.0,
            'synthesized_inductive': 0.9,
            'synthesized_analogy': 0.85,
            'simple_extraction': 0.8,
            'inverse_entailment': 1.15,
            'manual': 1.2,
            'core': 1.3
        }
        
        adjustment = source_adjustments.get(source, 1.0)
        return score * adjustment
    
    def update_performance(self, rule_id: str, success: bool):
        """Update performance tracking for a rule"""
        self.rule_performance[rule_id]['total'] += 1
        if success:
            self.rule_performance[rule_id]['success'] += 1
