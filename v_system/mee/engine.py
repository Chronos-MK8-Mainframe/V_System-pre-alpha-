"""Meta-Evolution Engine with Progol-inspired inverse entailment"""

import time
from typing import List, Dict, Optional

from v_system.core.rule import Rule
from v_system.core.context import Context
from v_system.rules.core_rules import create_core_rules
from v_system.mee.contradiction import HeuristicContradictionDetector, ConflictType
from v_system.mee.provability import ProvabilityEngine
from v_system.mee.signatures import SignatureManager
from v_system.mee.package import RulePackage
from v_system.mee.pattern_recognition import AdvancedPatternRecognizer
from v_system.mee.symbolic_regression import SymbolicRegressor
from v_system.mee.multi_example_synthesis import MultiExampleSynthesizer
from v_system.mee.confidence_scoring import ConfidenceScorer
from v_system.mee.inverse_entailment import InverseEntailmentEngine


class MetaEvolutionEngine:
    """Complete MeE with Progol-inspired inverse entailment"""
    
    def __init__(self, v_pipeline):
        self.v_pipeline = v_pipeline
        self.R_global = create_core_rules()
        self.meta_patterns = []
        self.contradiction_detector = HeuristicContradictionDetector()
        self.provability_engine = ProvabilityEngine()
        self.signature_manager = SignatureManager()
        
        # Enhanced learning components
        self.inverse_entailment = InverseEntailmentEngine()
        self.pattern_recognizer = AdvancedPatternRecognizer()
        self.symbolic_regressor = SymbolicRegressor()
        self.multi_example_synthesizer = MultiExampleSynthesizer()
        self.confidence_scorer = ConfidenceScorer()
        
        self.smt_enabled = False
        self.heuristic_failures = 0
        self.complexity_threshold = 100
        
        # Statistics
        self.rules_processed = 0
        self.rules_accepted = 0
        self.rules_rejected = 0
        self.packages_sent = 0
        self.global_broadcasts = 0
        self.patterns_discovered = 0
        self.symbolic_rules_synthesized = 0
        self.ile_rules_synthesized = 0
        
        print(f"\n🧠 MeE initialized with {len(self.R_global)} core rules")
        print("   ✨ Enhanced with:")
        print("      • Inverse Entailment (Progol-inspired)")
        print("      • Pattern Recognition")
        print("      • Symbolic Regression")
        print("      • Multi-Example Synthesis")
    
    def process_candidate_rule(self, candidate: Rule) -> Dict:
        """Process and validate candidate rule"""
        self.rules_processed += 1
        
        print(f"\n{'='*60}")
        print(f"Processing Rule #{self.rules_processed}: {candidate.id}")
        print(f"{'='*60}")
        
        # Phase 1: Contradiction detection
        print("Phase 1: Contradiction Detection...")
        resolution = self._resolve_contradictions(candidate)
        
        if resolution["status"] == "reject":
            self.rules_rejected += 1
            self.heuristic_failures += 1
            print(f"❌ REJECTED: {resolution['reason']}")
            return resolution
        
        if resolution["status"] == "replaced":
            print(f"🔄 Replaced existing rule: {resolution.get('replaced_id')}")
        
        # Phase 2: Provability
        print("Phase 2: Provability Analysis...")
        provability = self.provability_engine.analyze(candidate, self.R_global)
        print(f"   Result: {provability}")
        
        if provability == "unprovable":
            self.rules_rejected += 1
            self.heuristic_failures += 1
            print(f"❌ REJECTED: Cannot establish validity")
            return {"status": "rejected", "reason": "unprovable", "rule_id": candidate.id}
        
        # Phase 3: Enhanced confidence scoring
        print("Phase 3: Confidence Scoring...")
        confidence_analysis = self.confidence_scorer.score_rule(
            candidate, self.R_global, provability
        )
        candidate.confidence = confidence_analysis['final_score']
        candidate.source = "derived" if provability == "provable" else "empirical"
        
        print(f"   Base: {confidence_analysis['base_score']:.2f}")
        print(f"   Final: {candidate.confidence:.2f}")
        
        # Phase 4: Meta-patterns
        print("Phase 4: Meta-Pattern Extraction...")
        pattern_result = self._extract_meta_patterns(candidate)
        if pattern_result["new_pattern"]:
            print(f"   ✨ New pattern: {pattern_result['pattern_type']}")
            self.patterns_discovered += 1
        
        self.R_global.append(candidate)
        self.rules_accepted += 1
        
        print(f"✅ ACCEPTED: {candidate.id} (conf={candidate.confidence:.2f})")
        
        return {
            "status": "accepted",
            "provability": provability,
            "confidence": candidate.confidence,
            "confidence_analysis": confidence_analysis,
            "rule_id": candidate.id,
            "meta_pattern": pattern_result
        }
    
    def learn_from_examples(self, examples: List[Dict], 
                           use_inverse_entailment: bool = True,
                           use_multi_strategy: bool = True) -> Dict:
        """
        🧠 ENHANCED LEARNING with Progol's inverse entailment
        
        Strategy Priority:
        0. Inverse Entailment (Progol) - Best for logical rules
        1. Pattern Recognition - Good for algebraic patterns  
        2. Symbolic Regression - Good for numeric rules
        3. Multi-Example Synthesis - Good for diverse approaches
        4. Simple Extraction - Fallback
        """
        print(f"\n{'='*60}")
        print(f"📚 ENHANCED LEARNING FROM {len(examples)} EXAMPLES")
        print(f"{'='*60}")
        
        if len(examples) < 2:
            print("⚠️  Need at least 2 examples for learning")
            return {"rules_learned": 0, "error": "insufficient_examples"}
        
        learned_rules = []
        synthesis_stats = {
            'inverse_entailment': 0,
            'pattern_based': 0,
            'symbolic_regression': 0,
            'inductive': 0,
            'analogy': 0,
            'simple_extraction': 0
        }
        
        context = examples[0].get("context", Context("math", "algebra"))
        
        # Strategy 0: INVERSE ENTAILMENT (Progol)
        if use_inverse_entailment and len(examples) >= 2:
            print(f"\n🧠 Strategy 0: Inverse Entailment (Progol-inspired)")
            print("   This is the GOLD STANDARD for logical rule learning")
            
            positive = [ex for ex in examples if ex.get('label') != 'negative']
            negative = [ex for ex in examples if ex.get('label') == 'negative']
            
            from v_system.mee.inverse_entailment import Clause
            background_clauses = []
            
            try:
                learned_clause = self.inverse_entailment.learn_clause(
                    positive_examples=positive,
                    negative_examples=negative,
                    background=background_clauses
                )
                
                if learned_clause:
                    ile_rule = self.inverse_entailment.clause_to_rule(learned_clause, context)
                    result = self.process_candidate_rule(ile_rule)
                    
                    if result["status"] == "accepted":
                        learned_rules.append(ile_rule)
                        synthesis_stats['inverse_entailment'] += 1
                        self.ile_rules_synthesized += 1
                        print(f"   ✅ ILE rule: {ile_rule.id}")
                        print(f"      ⭐ PROVABLY CORRECT by construction!")
                else:
                    print(f"   ℹ️  ILE couldn't find suitable clause")
            
            except Exception as e:
                print(f"   ⚠️  ILE error: {e}")
        
        # Strategy 1: Pattern Recognition
        print(f"\n🔍 Strategy 1: Pattern Recognition")
        patterns = self.pattern_recognizer.recognize_patterns(examples)
        print(f"   Found {len(patterns)} patterns")
        
        for pattern in patterns:
            rule = self._create_rule_from_pattern(pattern, context)
            if rule:
                result = self.process_candidate_rule(rule)
                if result["status"] == "accepted":
                    learned_rules.append(rule)
                    synthesis_stats['pattern_based'] += 1
                    print(f"   ✅ Pattern rule: {rule.id}")
        
        # Strategy 2: Symbolic Regression
        print(f"\n🧮 Strategy 2: Symbolic Regression")
        if self._has_numeric_examples(examples):
            symbolic_result = self.symbolic_regressor.synthesize_rule(examples, context)
            if symbolic_result:
                expr, fitness = symbolic_result
                rule = self._create_rule_from_expression(expr, fitness, context)
                if rule:
                    result = self.process_candidate_rule(rule)
                    if result["status"] == "accepted":
                        learned_rules.append(rule)
                        synthesis_stats['symbolic_regression'] += 1
                        self.symbolic_rules_synthesized += 1
                        print(f"   ✅ Symbolic rule: {rule.id}")
        else:
            print("   ⏭️  Skipped (non-numeric examples)")
        
        # Strategy 3: Multi-Example Synthesis
        if use_multi_strategy and len(examples) >= 3:
            print(f"\n🎯 Strategy 3: Multi-Example Synthesis")
            synthesis_results = self.multi_example_synthesizer.synthesize(examples, context)
            print(f"   Generated {len(synthesis_results)} candidate rules")
            
            for synth_result in synthesis_results[:3]:
                if synth_result.rule:
                    result = self.process_candidate_rule(synth_result.rule)
                    if result["status"] == "accepted":
                        learned_rules.append(synth_result.rule)
                        synthesis_stats[synth_result.synthesis_method] += 1
                        print(f"   ✅ {synth_result.synthesis_method}: {synth_result.rule.id}")
        
        # Strategy 4: Simple extraction (fallback)
        if not learned_rules:
            print(f"\n🔧 Fallback: Simple Rule Extraction")
            simple_rules = self._simple_rule_extraction(examples, context)
            for rule in simple_rules:
                result = self.process_candidate_rule(rule)
                if result["status"] == "accepted":
                    learned_rules.append(rule)
                    synthesis_stats['simple_extraction'] += 1
                    print(f"   ✅ Simple rule: {rule.id}")
        
        # Distribute learned rules
        print(f"\n📤 Distributing {len(learned_rules)} learned rules...")
        distribution_count = 0
        
        for rule in learned_rules:
            target_nodes = self._determine_target_nodes(examples)
            
            if not target_nodes:
                result = self.broadcast_global_rule(rule, operation="add")
                distribution_count += result.get("nodes_updated", 0)
            else:
                result = self.send_to_specific_nodes(rule, target_nodes, operation="add")
                distribution_count += result.get("successful", 0)
        
        print(f"  ✅ Distributed to {distribution_count} nodes")
        
        avg_confidence = (sum(r.confidence for r in learned_rules) / len(learned_rules)
                         if learned_rules else 0.0)
        
        pattern_stats = self.pattern_recognizer.get_pattern_statistics()
        ile_stats = self.inverse_entailment.get_statistics()
        
        return {
            "rules_learned": len(learned_rules),
            "rules_distributed": distribution_count,
            "confidence_avg": avg_confidence,
            "synthesis_breakdown": synthesis_stats,
            "patterns_discovered": len(patterns),
            "pattern_statistics": pattern_stats,
            "inverse_entailment_stats": ile_stats,
            "examples_processed": len(examples)
        }
    
    def _has_numeric_examples(self, examples: List[Dict]) -> bool:
        """Check if examples contain numeric transformations"""
        for example in examples:
            if hasattr(example.get('output'), 'value'):
                try:
                    float(example['output'].value)
                    return True
                except:
                    pass
        return False
    
    def _create_rule_from_pattern(self, pattern, context: Context) -> Optional[Rule]:
        """Create rule from discovered pattern"""
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
        
        return Rule(
            rule_id=rule_id,
            condition=make_condition(pattern),
            transform=make_transform(pattern),
            domain=context,
            priority=7,
            confidence=pattern.confidence,
            source="pattern_recognition"
        )
    
    def _create_rule_from_expression(self, expr, fitness: float,
                                    context: Context) -> Optional[Rule]:
        """Create rule from symbolic expression"""
        rule_id = f"symbolic_{int(time.time() * 1000) % 10000}"
        
        confidence = max(0.5, 1.0 - min(1.0, fitness))
        
        return Rule(
            rule_id=rule_id,
            condition=lambda ex, ctx, refs: 1,
            transform=lambda ex: expr,
            domain=context,
            priority=7,
            confidence=confidence,
            source="symbolic_regression"
        )
    
    def _simple_rule_extraction(self, examples: List[Dict], 
                               context: Context) -> List[Rule]:
        """Simple rule extraction as fallback"""
        rules = []
        
        for i, example in enumerate(examples[:3]):
            rule_id = f"simple_{i}_{int(time.time() * 1000) % 10000}"
            
            input_expr = example["input"]
            output_expr = example["output"]
            
            def make_condition(inp):
                def condition(expr, ctx, refs):
                    return 1 if self._similar_structure(expr, inp) else 0
                return condition
            
            def make_transform(outp):
                def transform(expr):
                    return outp
                return transform
            
            rule = Rule(
                rule_id=rule_id,
                condition=make_condition(input_expr),
                transform=make_transform(output_expr),
                domain=context,
                priority=6,
                confidence=0.5 + (len(examples) / 20),
                source="simple_extraction"
            )
            
            rules.append(rule)
        
        return rules
    
    def _similar_structure(self, expr1, expr2) -> bool:
        """Check if two expressions have similar structure"""
        if not hasattr(expr1, 'op') or not hasattr(expr2, 'op'):
            return False
        return expr1.op == expr2.op
    
    def _determine_target_nodes(self, examples: List[Dict]) -> List[str]:
        """Determine target nodes from examples"""
        target_nodes = []
        
        for example in examples:
            if "target_node_id" in example:
                target_nodes.append(example["target_node_id"])
            elif "target_layer" in example:
                layer_idx = example["target_layer"] - 1
                if 0 <= layer_idx < len(self.v_pipeline.layers):
                    layer = self.v_pipeline.layers[layer_idx]
                    target_nodes.extend([node.node_id for node in layer])
        
        return list(set(target_nodes))
    
    def _resolve_contradictions(self, candidate: Rule) -> Dict:
        """Check for contradictions with existing rules"""
        for existing in self.R_global:
            conflict = self.contradiction_detector.detect(candidate, existing)
            
            if not conflict.exists:
                continue
            
            print(f"   ⚠️  Conflict with {existing.id}: {conflict.description}")
            
            if conflict.type == ConflictType.DIRECT_NEGATION:
                if candidate.confidence > existing.confidence:
                    self.R_global.remove(existing)
                    print(f"   🔄 Replaced {existing.id}")
                    return {"status": "replaced", "replaced_id": existing.id}
                else:
                    return {"status": "reject", "reason": f"contradicts {existing.id}"}
            
            elif conflict.type == ConflictType.CONTEXT_OVERLAP:
                candidate.domain = Context(
                    domain=candidate.domain.domain,
                    subdomain=f"restricted_{candidate.id[:10]}",
                    features={**candidate.domain.features, "restricted": True}
                )
                print(f"   📝 Contextualized rule")
                return {"status": "contextualized"}
        
        return {"status": "no_conflict"}
    
    def _extract_meta_patterns(self, rule: Rule) -> Dict:
        """Extract meta-patterns from rules"""
        rule_type = self._classify_rule_type(rule)
        
        for pattern in self.meta_patterns:
            if pattern["type"] == rule_type and pattern["domain"] == rule.domain.domain:
                pattern["count"] += 1
                return {
                    "new_pattern": False,
                    "pattern_type": rule_type,
                    "pattern_count": pattern["count"]
                }
        
        new_pattern = {
            "type": rule_type,
            "domain": rule.domain.domain,
            "count": 1,
            "discovered_at": time.time()
        }
        self.meta_patterns.append(new_pattern)
        return {
            "new_pattern": True,
            "pattern_type": rule_type,
            "pattern_count": 1
        }
    
    def _classify_rule_type(self, rule: Rule) -> str:
        """Classify rule by type"""
        id_lower = rule.id.lower()
        patterns = {
            "ile": "inverse_entailment",
            "pattern": "recognized_pattern",
            "symbolic": "symbolic_regression",
            "synth": "synthesized",
            "commutative": "commutative_pattern",
            "associative": "associative_pattern",
            "distributive": "distributive_pattern",
            "identity": "identity_pattern",
        }
        for keyword, pattern_type in patterns.items():
            if keyword in id_lower:
                return pattern_type
        return "general_transform"
    
    def broadcast_global_rule(self, rule: Rule, operation: str = "add") -> Dict:
        """🌐 Global broadcast to all V' nodes"""
        print(f"\n🌐 GLOBAL BROADCAST: {rule.id}")
        
        package = RulePackage(
            signature=self.signature_manager.get_global_signature(),
            target_node_ids=None,
            target_context=rule.domain,
            rule=rule,
            operation=operation,
            priority=rule.priority
        )
        
        result = self.v_pipeline.broadcast_to_all(package)
        self.packages_sent += result["total_nodes"]
        self.global_broadcasts += 1
        
        print(f"   📡 Updated: {result['nodes_updated']}/{result['total_nodes']} nodes")
        return result
    
    def send_to_specific_nodes(self, rule: Rule, target_node_ids: List[str],
                               operation: str = "add") -> Dict:
        """🎯 Targeted update to specific V' nodes"""
        print(f"\n🎯 TARGETED UPDATE: {rule.id}")
        
        results = []
        for node_id in target_node_ids:
            node = self.v_pipeline.get_node(node_id)
            if not node:
                results.append({"node_id": node_id, "result": {"status": "not_found"}})
                continue
            
            package = RulePackage(
                signature=self.signature_manager.generate_one_time(),
                target_node_ids=[node_id],
                target_context=rule.domain,
                rule=rule,
                operation=operation,
                priority=rule.priority
            )
            
            result = node.receive_rule_package(package)
            results.append({"node_id": node_id, "result": result})
            self.packages_sent += 1
        
        successful = len([r for r in results if r["result"]["status"] in ["added", "modified"]])
        return {"successful": successful, "total": len(results), "details": results}
    
    def get_stats(self) -> Dict:
        """Get comprehensive system statistics"""
        pattern_stats = self.pattern_recognizer.get_pattern_statistics()
        ile_stats = self.inverse_entailment.get_statistics()
        
        return {
            "global_rules": len(self.R_global),
            "rules_processed": self.rules_processed,
            "rules_accepted": self.rules_accepted,
            "rules_rejected": self.rules_rejected,
            "acceptance_rate": (self.rules_accepted / self.rules_processed * 100)
                               if self.rules_processed > 0 else 0,
            "packages_sent": self.packages_sent,
            "global_broadcasts": self.global_broadcasts,
            "meta_patterns": len(self.meta_patterns),
            "patterns_discovered": self.patterns_discovered,
            "symbolic_rules_synthesized": self.symbolic_rules_synthesized,
            "ile_rules_synthesized": self.ile_rules_synthesized,
            "smt_enabled": self.smt_enabled,
            "pattern_recognition": pattern_stats,
            "inverse_entailment": ile_stats
        }
