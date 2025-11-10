"""Meta-Evolution Engine core"""

import time
from typing import List, Dict

from v_system.core.rule import Rule
from v_system.core.context import Context
from v_system.rules.core_rules import create_core_rules
from v_system.mee.contradiction import HeuristicContradictionDetector, ConflictType
from v_system.mee.provability import ProvabilityEngine
from v_system.mee.signatures import SignatureManager
from v_system.mee.package import RulePackage


class MetaEvolutionEngine:
    """Complete MeE with rule management and learning"""
    
    def __init__(self, v_pipeline):
        self.v_pipeline = v_pipeline
        self.R_global = create_core_rules()
        self.meta_patterns = []
        self.contradiction_detector = HeuristicContradictionDetector()
        self.provability_engine = ProvabilityEngine()
        self.signature_manager = SignatureManager()
        
        self.smt_enabled = False
        self.heuristic_failures = 0
        self.complexity_threshold = 100
        
        self.rules_processed = 0
        self.rules_accepted = 0
        self.rules_rejected = 0
        self.packages_sent = 0
        self.global_broadcasts = 0
        
        print(f"\n🧠 MeE initialized with {len(self.R_global)} core rules")
    
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
        
        candidate.confidence = 1.0 if provability == "provable" else 0.5
        candidate.source = "derived" if provability == "provable" else "empirical"
        
        # Phase 3: Meta-patterns
        print("Phase 3: Meta-Pattern Extraction...")
        pattern_result = self._extract_meta_patterns(candidate)
        if pattern_result["new_pattern"]:
            print(f"   ✨ New pattern: {pattern_result['pattern_type']}")
        
        self.R_global.append(candidate)
        self.rules_accepted += 1
        
        print(f"✅ ACCEPTED: {candidate.id} (conf={candidate.confidence:.2f})")
        
        return {
            "status": "accepted",
            "provability": provability,
            "confidence": candidate.confidence,
            "rule_id": candidate.id,
            "meta_pattern": pattern_result
        }
    
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
                # Contextualize the rule
                candidate.domain = Context(
                    domain=candidate.domain.domain,
                    subdomain=f"restricted_{candidate.id[:10]}",
                    features={**candidate.domain.features, "restricted": True}
                )
                print(f"   📝 Contextualized rule")
                return {"status": "contextualized"}
            
            elif conflict.type == ConflictType.SPECIAL_GENERAL:
                # Merge rules
                print(f"   🔀 Rules can be merged")
                return {"status": "mergeable"}
        
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
            "commutative": "commutative_pattern",
            "associative": "associative_pattern",
            "distributive": "distributive_pattern",
            "identity": "identity_pattern",
            "inverse": "inverse_pattern",
            "zero": "zero_pattern"
        }
        for keyword, pattern_type in patterns.items():
            if keyword in id_lower:
                return pattern_type
        return "general_transform"
    
    def learn_from_examples(self, examples: List[Dict]) -> Dict:
        """
        Learn rules from minimal training data (3-10 examples)
        
        Args:
            examples: List of dicts with 'input', 'output', 'context', etc.
        
        Returns:
            Dict with learning statistics
        """
        print(f"\n{'='*60}")
        print(f"📚 LEARNING FROM {len(examples)} EXAMPLES")
        print(f"{'='*60}")
        
        learned_rules = []
        
        for i, example in enumerate(examples):
            input_expr = example["input"]
            output_expr = example["output"]
            context = example.get("context", Context("math", "algebra"))
            
            print(f"\nExample {i+1}: {input_expr} → {output_expr}")
            
            # Simple pattern extraction (can be enhanced)
            rule_id = f"learned_rule_{i}_{int(time.time() * 1000) % 10000}"
            
            # Capture the input/output in closures
            def make_condition(inp, outp):
                def condition(expr, ctx, refs):
                    # Match structure
                    if expr.op == inp.op and len(expr.args) == len(inp.args):
                        return 1
                    return 0
                return condition
            
            def make_transform(inp, outp):
                def transform(expr):
                    # Apply learned transformation
                    return outp.copy()
                return transform
            
            learned_rule = Rule(
                rule_id=rule_id,
                condition=make_condition(input_expr, output_expr),
                transform=make_transform(input_expr, output_expr),
                domain=context,
                priority=8,
                confidence=0.5 + (len(examples) / 20),  # More examples = higher confidence
                source="learned"
            )
            
            # Process through MeE
            result = self.process_candidate_rule(learned_rule)
            
            if result["status"] == "accepted":
                learned_rules.append(learned_rule)
                print(f"  ✅ Learned: {rule_id}")
            else:
                print(f"  ❌ Rejected: {result.get('reason', 'unknown')}")
        
        # Distribute learned rules to V' nodes
        print(f"\n📤 Distributing learned rules...")
        
        distribution_count = 0
        for rule in learned_rules:
            # Determine target nodes based on examples
            target_nodes = []
            for example in examples:
                if "target_node_id" in example:
                    target_nodes.append(example["target_node_id"])
                elif "target_layer" in example:
                    layer_idx = example["target_layer"] - 1
                    if 0 <= layer_idx < len(self.v_pipeline.layers):
                        layer = self.v_pipeline.layers[layer_idx]
                        target_nodes.extend([node.node_id for node in layer])
            
            if not target_nodes:
                # Default: broadcast to all
                result = self.broadcast_global_rule(rule, operation="add")
                distribution_count += result.get("nodes_updated", 0)
            else:
                # Remove duplicates
                target_nodes = list(set(target_nodes))
                result = self.send_to_specific_nodes(rule, target_nodes, operation="add")
                distribution_count += result.get("successful", 0)
        
        print(f"  ✅ Distributed to {distribution_count} nodes")
        
        return {
            "rules_learned": len(learned_rules),
            "rules_distributed": distribution_count,
            "confidence_avg": sum(r.confidence for r in learned_rules) / len(learned_rules)
                              if learned_rules else 0.0
        }
    
    def broadcast_global_rule(self, rule: Rule, operation: str = "add") -> Dict:
        """🌐 Global broadcast to all V' nodes"""
        print(f"\n🌐 GLOBAL BROADCAST: {rule.id} to ALL V' nodes")
        
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
        
        print(f"   📡 Broadcast complete: {result['nodes_updated']}/{result['total_nodes']} nodes updated")
        return result
    
    def send_to_specific_nodes(self, rule: Rule, target_node_ids: List[str],
                               operation: str = "add") -> Dict:
        """🎯 Targeted update to specific V' nodes"""
        print(f"\n🎯 TARGETED UPDATE: {rule.id} to {len(target_node_ids)} nodes")
        
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
            
            status_icon = "✅" if result["status"] in ["added", "modified"] else "❌"
            print(f"   {status_icon} {node_id}: {result['status']}")
        
        successful = len([r for r in results if r["result"]["status"] in ["added", "modified"]])
        return {"successful": successful, "total": len(results), "details": results}
    
    def send_to_layer(self, rule: Rule, layer_index: int, operation: str = "add") -> Dict:
        """📊 Layer-wide update to all nodes in a specific layer"""
        if layer_index < 0 or layer_index >= len(self.v_pipeline.layers):
            return {"status": "error", "reason": "layer_not_found"}
        
        layer_nodes = self.v_pipeline.layers[layer_index]
        print(f"\n📊 LAYER UPDATE: {rule.id} to Layer {layer_index + 1} ({len(layer_nodes)} nodes)")
        
        target_ids = [node.node_id for node in layer_nodes]
        return self.send_to_specific_nodes(rule, target_ids, operation)
    
    def enable_smt_when_needed(self) -> bool:
        """Enable SMT solver based on system complexity"""
        if self.smt_enabled:
            return False
        
        reasons = []
        if len(self.R_global) > 50:
            reasons.append(f"Rule count ({len(self.R_global)}) > 50")
        if self.heuristic_failures > 10:
            reasons.append(f"Heuristic failures ({self.heuristic_failures}) > 10")
        
        complexity = self._estimate_complexity()
        if complexity > self.complexity_threshold:
            reasons.append(f"Complexity ({complexity:.1f}) > {self.complexity_threshold}")
        
        if reasons:
            self.smt_enabled = True
            print(f"\n🔧 SMT SOLVER ENABLED: {'; '.join(reasons)}")
            return True
        return False
    
    def _estimate_complexity(self) -> float:
        """Estimate system complexity"""
        if not self.R_global:
            return 0.0
        rule_count = len(self.R_global)
        domain_diversity = len(set(r.domain.domain for r in self.R_global))
        avg_priority = sum(r.priority for r in self.R_global) / rule_count
        return rule_count * 0.5 + domain_diversity * 10 + avg_priority * 2
    
    def get_stats(self) -> Dict:
        """Get system statistics"""
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
            "smt_enabled": self.smt_enabled,
            "heuristic_failures": self.heuristic_failures,
            "system_complexity": self._estimate_complexity()
        }
