"""V' node implementation"""

from typing import List, Optional, Dict
import time

from v_system.core.symbolic_expr import SymbolicExpression
from v_system.core.context import Context, ContextInference, Reference, ContextBundle
from v_system.core.rule import Rule
from v_system.core.package import Package, ReadBus
from v_system.rules.core_rules import create_core_rules


class VPrimeNode:
    """V' node with complete processing pipeline"""
    
    def __init__(self, node_id: str, layer_index: int, column_index: int):
        self.node_id = node_id
        self.layer_index = layer_index
        self.column_index = column_index
        self.R_local = create_core_rules()
        self.update_log = []
        self.context_inferencer = ContextInference()
        self.application_log = []
    
    def process(self, P_input: Package, bias_initial: Optional[str],
                refs: List[Reference], read_bus: ReadBus) -> Package:
        """
        Main V' processing pipeline (7 phases from spec)
        
        Phase 1: Context Inference
        Phase 2: Bias Determination
        Phase 3: Rule Filtering by Context
        Phase 4: Alignment Verification
        Phase 5: Context Building
        Phase 6: Rule Application
        Phase 7: Output Package Construction
        """
        
        # Phase 1: Context Inference
        context_active = self.context_inferencer.infer_context(
            P_input.main, P_input.history
        )
        
        # Phase 2: Bias Determination
        if self.layer_index == 1:
            bias_active = bias_initial
        else:
            bias_active = self._derive_bias_from_references(refs, context_active)
        
        # Phase 3: Rule Filtering by Context
        R_applicable = self._filter_rules_by_context(
            self.R_local, context_active, threshold=0.7
        )
        
        # Phase 4: Alignment Verification
        delta_alignment = P_input.alignment(context_active)
        
        if abs(delta_alignment) > 0.15:
            P_working = Package(
                main=P_input.main.copy(),
                history=P_input.history.copy(),
                undefined=P_input.undefined.copy(),
                alignment=P_input.alignment,
                metadata={**P_input.metadata, "corrected": True}
            )
        else:
            P_working = P_input
        
        # Phase 5: Context Building
        context_bundle = ContextBundle(
            parallel_outputs=[ref.output for ref in refs],
            parallel_contexts=[ref.context for ref in refs],
            parallel_operations=[ref.operation_type for ref in refs],
            original_input=read_bus.get().main,
            transformation_history=P_working.history,
            current_context=context_active,
            layer_position=self.layer_index,
            column_position=self.column_index
        )
        
        # Phase 6: Rule Application
        f_output = P_working.main.copy()
        U_output = P_working.undefined.copy()
        rules_applied = []
        
        for rule in R_applicable:
            applicability = rule.is_applicable(f_output, context_bundle, refs)
            
            if applicability == 1:  # Applicable
                f_before = str(f_output)
                f_output = rule.apply(f_output)
                f_after = str(f_output)
                
                if f_before != f_after:  # Transformation occurred
                    rules_applied.append(rule.id)
                    self.application_log.append({
                        "rule_id": rule.id,
                        "before": f_before,
                        "after": f_after,
                        "timestamp": time.time()
                    })
            
            elif applicability == -1:  # Undefined
                U_output.add(f"undefined_in_{rule.id}")
        
        # Phase 7: Output Package Construction
        history_output = P_working.history + [P_working.main]
        
        return Package(
            main=f_output,
            history=history_output,
            undefined=U_output,
            alignment=lambda ctx: 0.0,
            metadata={
                "node_id": self.node_id,
                "context": context_active.domain,
                "bias": bias_active,
                "rules_applied": rules_applied,
                "layer": self.layer_index
            }
        )
    
    def _derive_bias_from_references(self, refs: List[Reference], 
                                     context: Context) -> str:
        """Derive bias from parallel V' activity"""
        if not refs:
            return "default"
        
        active_ops = {ref.operation_type for ref in refs}
        all_ops = {"simplify", "factor", "expand", "combine"}
        uncovered = all_ops - active_ops
        
        return list(uncovered)[0] if uncovered else "refine"
    
    def _filter_rules_by_context(self, rules: List[Rule], context: Context,
                                 threshold: float) -> List[Rule]:
        """Filter rules by context similarity"""
        filtered = []
        
        for rule in rules:
            similarity = rule.domain.similarity(context)
            if similarity >= threshold:
                filtered.append(rule)
        
        filtered.sort(key=lambda r: (r.priority, r.confidence), reverse=True)
        return filtered
    
    def receive_rule_package(self, package) -> Dict:
        """Receive rule updates from MeE"""
        if not self._validate_signature(package.signature):
            return {"status": "rejected", "reason": "invalid_signature"}
        
        if package.operation == "add":
            self.R_local.append(package.rule)
            self.update_log.append({
                "timestamp": package.timestamp,
                "operation": "add",
                "rule_id": package.rule.id
            })
            return {"status": "added", "rule_id": package.rule.id}
        
        return {"status": "unknown_operation"}
    
    def _validate_signature(self, signature: str) -> bool:
        return signature.startswith("sig_") or signature.startswith("GLOBAL_")
    
    def __repr__(self):
        return f"V'[{self.node_id}](rules={len(self.R_local)})"
