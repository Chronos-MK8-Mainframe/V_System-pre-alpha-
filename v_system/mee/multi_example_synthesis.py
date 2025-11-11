"""Multi-example rule synthesis with multiple strategies"""

from typing import List, Dict, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import time

from v_system.core.rule import Rule
from v_system.core.context import Context
from v_system.mee.pattern_recognition import AdvancedPatternRecognizer, Pattern


@dataclass
class SynthesisResult:
    """Result of multi-example synthesis"""
    rule: Optional[Rule]
    confidence: float
    pattern: Optional[Pattern]
    coverage: float
    consistency: float
    generalization_score: float
    synthesis_method: str
    metadata: Dict


class MultiExampleSynthesizer:
    """Synthesize rules from multiple examples using various strategies"""
    
    def __init__(self):
        self.pattern_recognizer = AdvancedPatternRecognizer()
        self.min_examples = 2
        self.min_confidence = 0.5
        self.min_coverage = 0.7
        
    def synthesize(self, examples: List[Dict], context: Context) -> List[SynthesisResult]:
        """Synthesize rules from multiple examples"""
        if len(examples) < self.min_examples:
            return []
        
        results = []
        
        pattern_results = self._pattern_based_synthesis(examples, context)
        results.extend(pattern_results)
        
        inductive_results = self._inductive_synthesis(examples, context)
        results.extend(inductive_results)
        
        analogy_results = self._analogy_based_synthesis(examples, context)
        results.extend(analogy_results)
        
        results = self._filter_and_rank(results, examples)
        
        return results
    
    def _pattern_based_synthesis(self, examples: List[Dict], 
                                 context: Context) -> List[SynthesisResult]:
        """Synthesize rules based on recognized patterns"""
        results = []
        patterns = self.pattern_recognizer.recognize_patterns(examples)
        
        for pattern in patterns:
            rule = self._pattern_to_rule(pattern, context)
            
            if rule:
                coverage = self._calculate_coverage(rule, examples)
                consistency = self._calculate_consistency(rule, pattern.examples)
                generalization = pattern.confidence
                
                result = SynthesisResult(
                    rule=rule,
                    confidence=pattern.confidence,
                    pattern=pattern,
                    coverage=coverage,
                    consistency=consistency,
                    generalization_score=generalization,
                    synthesis_method='pattern_based',
                    metadata={
                        'pattern_type': pattern.pattern_type,
                        'pattern_frequency': pattern.frequency
                    }
                )
                results.append(result)
        
        return results
    
    def _inductive_synthesis(self, examples: List[Dict],
                            context: Context) -> List[SynthesisResult]:
        """Synthesize rules using inductive learning"""
        results = []
        groups = self._group_similar_examples(examples)
        
        for group_id, group_examples in groups.items():
            if len(group_examples) < 2:
                continue
            
            common_transform = self._find_common_transformation(group_examples)
            
            if common_transform:
                rule = self._create_rule_from_transform(
                    common_transform, group_examples, context
                )
                
                if rule:
                    coverage = len(group_examples) / len(examples)
                    consistency = self._calculate_consistency(rule, group_examples)
                    generalization = self._estimate_generalization(rule, examples)
                    
                    result = SynthesisResult(
                        rule=rule,
                        confidence=consistency * 0.8,
                        pattern=None,
                        coverage=coverage,
                        consistency=consistency,
                        generalization_score=generalization,
                        synthesis_method='inductive',
                        metadata={
                            'group_size': len(group_examples),
                            'transform_type': common_transform['type']
                        }
                    )
                    results.append(result)
        
        return results
    
    def _analogy_based_synthesis(self, examples: List[Dict],
                                 context: Context) -> List[SynthesisResult]:
        """Synthesize rules using analogical reasoning"""
        results = []
        analogies = self._find_analogies(examples)
        
        for analogy in analogies:
            source_ex, target_ex, mapping = analogy
            
            rule = self._transfer_by_analogy(source_ex, target_ex, mapping, context)
            
            if rule:
                coverage = self._calculate_coverage(rule, examples)
                consistency = self._test_analogy_consistency(rule, analogy, examples)
                generalization = self._estimate_generalization(rule, examples)
                
                if consistency > 0.5:
                    result = SynthesisResult(
                        rule=rule,
                        confidence=consistency * 0.7,
                        pattern=None,
                        coverage=coverage,
                        consistency=consistency,
                        generalization_score=generalization,
                        synthesis_method='analogy',
                        metadata={
                            'analogy_strength': mapping['strength'],
                            'source_example': str(source_ex['input']),
                            'target_example': str(target_ex['input'])
                        }
                    )
                    results.append(result)
        
        return results
    
    def _pattern_to_rule(self, pattern: Pattern, context: Context) -> Optional[Rule]:
        """Convert pattern to rule"""
        rule_id = f"pattern_{pattern.pattern_type}_{int(time.time() * 1000) % 10000}"
        
        def make_condition(p):
            def condition(expr, ctx, refs):
                return 1 if p.matches(expr) else 0
            return condition
        
        def make_transform(p):
            def transform(expr):
                if p.examples:
                    return p.examples[0]['output']
                return expr
            return transform
        
        rule = Rule(
            rule_id=rule_id,
            condition=make_condition(pattern),
            transform=make_transform(pattern),
            domain=context,
            priority=7,
            confidence=pattern.confidence,
            source="synthesized_pattern"
        )
        
        return rule
    
    def _group_similar_examples(self, examples: List[Dict]) -> Dict[str, List[Dict]]:
        """Group examples by structural similarity"""
        groups = defaultdict(list)
        
        for example in examples:
            signature = self._get_example_signature(example)
            groups[signature].append(example)
        
        return dict(groups)
    
    def _get_example_signature(self, example: Dict) -> str:
        """Get signature for example grouping"""
        input_sig = self._get_structure(example['input'])
        output_sig = self._get_structure(example['output'])
        return f"{input_sig}->{output_sig}"
    
    def _get_structure(self, expr) -> str:
        """Get structure representation of expression"""
        if not hasattr(expr, 'op'):
            return 'ATOM'
        
        if not hasattr(expr, 'args') or not expr.args:
            return str(expr.op)
        
        arg_structures = [self._get_structure(arg) for arg in expr.args]
        return f"{expr.op}({','.join(arg_structures)})"
    
    def _find_common_transformation(self, examples: List[Dict]) -> Optional[Dict]:
        """Find common transformation across examples"""
        if not examples:
            return None
        
        transform_types = []
        for example in examples:
            transform_type = self._classify_transformation(example)
            transform_types.append(transform_type)
        
        if not transform_types:
            return None
        
        most_common = max(set(transform_types), key=transform_types.count)
        frequency = transform_types.count(most_common) / len(transform_types)
        
        if frequency < 0.7:
            return None
        
        return {
            'type': most_common,
            'frequency': frequency,
            'examples': examples
        }
    
    def _classify_transformation(self, example: Dict) -> str:
        """Classify type of transformation in example"""
        input_expr = example['input']
        output_expr = example['output']
        
        input_ops = self._extract_operations(input_expr)
        output_ops = self._extract_operations(output_expr)
        
        if output_ops != input_ops:
            return 'operation_change'
        
        input_depth = self._get_depth(input_expr)
        output_depth = self._get_depth(output_expr)
        
        if output_depth > input_depth:
            return 'expansion'
        elif output_depth < input_depth:
            return 'reduction'
        else:
            return 'restructuring'
    
    def _extract_operations(self, expr) -> Set[str]:
        """Extract all operations in expression"""
        ops = set()
        
        if hasattr(expr, 'op'):
            ops.add(str(expr.op))
        
        if hasattr(expr, 'args'):
            for arg in expr.args:
                ops.update(self._extract_operations(arg))
        
        return ops
    
    def _get_depth(self, expr) -> int:
        """Get depth of expression tree"""
        if not hasattr(expr, 'args') or not expr.args:
            return 1
        return 1 + max(self._get_depth(arg) for arg in expr.args)
    
    def _create_rule_from_transform(self, transform: Dict, examples: List[Dict],
                                   context: Context) -> Optional[Rule]:
        """Create rule from transformation description"""
        rule_id = f"synth_{transform['type']}_{int(time.time() * 1000) % 10000}"
        
        def condition(expr, ctx, refs):
            return 1 if self._matches_transform_pattern(expr, transform) else 0
        
        def transform_func(expr):
            return self._apply_transform_pattern(expr, transform)
        
        rule = Rule(
            rule_id=rule_id,
            condition=condition,
            transform=transform_func,
            domain=context,
            priority=6,
            confidence=transform['frequency'],
            source="synthesized_inductive"
        )
        
        return rule
    
    def _matches_transform_pattern(self, expr, transform: Dict) -> bool:
        """Check if expression matches transform pattern"""
        return True
    
    def _apply_transform_pattern(self, expr, transform: Dict):
        """Apply transformation pattern to expression"""
        return expr
    
    def _find_analogies(self, examples: List[Dict]) -> List[Tuple]:
        """Find analogous example pairs"""
        analogies = []
        
        for i, ex1 in enumerate(examples):
            for ex2 in examples[i+1:]:
                mapping = self._find_analogy_mapping(ex1, ex2)
                if mapping and mapping['strength'] > 0.6:
                    analogies.append((ex1, ex2, mapping))
        
        return analogies
    
    def _find_analogy_mapping(self, ex1: Dict, ex2: Dict) -> Optional[Dict]:
        """Find mapping between two examples"""
        input_similarity = self._structural_similarity(ex1['input'], ex2['input'])
        output_similarity = self._structural_similarity(ex1['output'], ex2['output'])
        
        if input_similarity > 0.5 and output_similarity > 0.5:
            return {
                'strength': (input_similarity + output_similarity) / 2,
                'input_mapping': {},
                'output_mapping': {}
            }
        
        return None
    
    def _structural_similarity(self, expr1, expr2) -> float:
        """Calculate structural similarity between expressions"""
        if not hasattr(expr1, 'op') or not hasattr(expr2, 'op'):
            return 0.0
        
        if expr1.op != expr2.op:
            return 0.0
        
        if not hasattr(expr1, 'args') or not hasattr(expr2, 'args'):
            return 1.0
        
        if len(expr1.args) != len(expr2.args):
            return 0.5
        
        arg_similarities = [
            self._structural_similarity(a1, a2)
            for a1, a2 in zip(expr1.args, expr2.args)
        ]
        
        return sum(arg_similarities) / len(arg_similarities) if arg_similarities else 0.0
    
    def _transfer_by_analogy(self, source: Dict, target: Dict, mapping: Dict,
                            context: Context) -> Optional[Rule]:
        """Create rule by transferring pattern via analogy"""
        rule_id = f"analogy_{int(time.time() * 1000) % 10000}"
        
        def condition(expr, ctx, refs):
            return 1 if self._structural_similarity(expr, source['input']) > 0.7 else 0
        
        def transform(expr):
            return target['output']
        
        rule = Rule(
            rule_id=rule_id,
            condition=condition,
            transform=transform,
            domain=context,
            priority=6,
            confidence=mapping['strength'] * 0.8,
            source="synthesized_analogy"
        )
        
        return rule
    
    def _test_analogy_consistency(self, rule: Rule, analogy: Tuple,
                                  examples: List[Dict]) -> float:
        """Test consistency of analogy-based rule"""
        source, target, mapping = analogy
        correct = 0
        total = 0
        
        for example in examples:
            total += 1
            if self._structural_similarity(example['output'], target['output']) > 0.5:
                correct += 1
        
        return correct / total if total > 0 else 0.0
    
    def _calculate_coverage(self, rule: Rule, examples: List[Dict]) -> float:
        """Calculate what percentage of examples the rule covers"""
        covered = 0
        for example in examples:
            try:
                if rule.condition(example['input'], rule.domain, []):
                    covered += 1
            except:
                pass
        
        return covered / len(examples) if examples else 0.0
    
    def _calculate_consistency(self, rule: Rule, examples: List[Dict]) -> float:
        """Calculate how consistently the rule produces correct outputs"""
        correct = 0
        applicable = 0
        
        for example in examples:
            try:
                if rule.condition(example['input'], rule.domain, []):
                    applicable += 1
                    correct += 1
            except:
                pass
        
        return correct / applicable if applicable > 0 else 0.0
    
    def _estimate_generalization(self, rule: Rule, examples: List[Dict]) -> float:
        """Estimate how well rule generalizes"""
        coverage = self._calculate_coverage(rule, examples)
        consistency = self._calculate_consistency(rule, examples)
        
        return (coverage + consistency) / 2
    
    def _filter_and_rank(self, results: List[SynthesisResult],
                        examples: List[Dict]) -> List[SynthesisResult]:
        """Filter and rank synthesis results"""
        filtered = [
            r for r in results
            if r.confidence >= self.min_confidence and r.coverage >= self.min_coverage
        ]
        
        def score(result: SynthesisResult) -> float:
            return (
                result.confidence * 0.4 +
                result.coverage * 0.3 +
                result.consistency * 0.2 +
                result.generalization_score * 0.1
            )
        
        filtered.sort(key=score, reverse=True)
        
        return filtered
