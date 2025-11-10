"""V' pipeline with series topology"""

from typing import List, Dict, Optional

from v_system.core.symbolic_expr import SymbolicExpression
from v_system.core.package import Package, ReadBus
from v_system.core.context import Context, ContextInference, Reference
from v_system.vprime.node import VPrimeNode
from v_system.vprime.alignment import AlignmentChecker


class VPrimePipeline:
    """V' nodes in series with full execution"""
    
    def __init__(self, num_layers: int, nodes_per_layer: int):
        self.layers: List[List[VPrimeNode]] = []
        self.node_map: Dict[str, VPrimeNode] = {}
        self.alignment_checkers: List[AlignmentChecker] = []
        
        print(f"\n🗂️  Building V' Pipeline: {num_layers} layers × {nodes_per_layer} nodes")
        
        for layer_idx in range(1, num_layers + 1):
            layer = []
            for col_idx in range(nodes_per_layer):
                node_id = f"L{layer_idx}_C{col_idx}"
                node = VPrimeNode(node_id, layer_idx, col_idx)
                layer.append(node)
                self.node_map[node_id] = node
            self.layers.append(layer)
            
            if layer_idx < num_layers:
                self.alignment_checkers.append(AlignmentChecker())
        
        print(f"✅ Pipeline ready with {len(self.node_map)} V' nodes")
    
    def execute(self, input_expr: SymbolicExpression) -> Package:
        """Execute full pipeline end-to-end"""
        
        print(f"\n{'='*60}")
        print(f"🚀 PIPELINE EXECUTION")
        print(f"{'='*60}")
        print(f"Input: {input_expr}")
        
        initial_package = Package(
            main=input_expr,
            history=[],
            undefined=set(),
            metadata={"input": str(input_expr)}
        )
        
        read_bus = ReadBus(initial_package)
        current_packages = [initial_package.copy() for _ in self.layers[0]]
        
        for layer_idx, layer in enumerate(self.layers):
            print(f"\n--- Layer {layer_idx + 1} ---")
            
            new_packages = []
            for col_idx, node in enumerate(layer):
                bias = "default" if layer_idx == 0 else None
                
                refs = []
                if layer_idx > 0:
                    for other_idx, other_pkg in enumerate(current_packages):
                        if other_idx != col_idx:
                            refs.append(Reference(
                                output=other_pkg.main,
                                context=ContextInference().infer_context(other_pkg.main),
                                alignment=other_pkg.alignment,
                                operation_type=other_pkg.metadata.get("operation", "transform"),
                                bias_signature=other_pkg.metadata.get("bias", "default")
                            ))
                
                output_pkg = node.process(current_packages[col_idx], bias, refs, read_bus)
                new_packages.append(output_pkg)
                
                rules_applied = output_pkg.metadata.get("rules_applied", [])
                print(f"  {node.node_id}: {current_packages[col_idx].main} → {output_pkg.main}")
                if rules_applied:
                    print(f"    Rules: {', '.join(rules_applied)}")
            
            if layer_idx < len(self.alignment_checkers):
                checker = self.alignment_checkers[layer_idx]
                expected_context = Context("math", "algebra")
                new_packages = [checker.check(pkg, expected_context) for pkg in new_packages]
            
            if layer_idx < len(self.layers) - 1:
                current_packages = new_packages
            else:
                final_package = self._merge_packages(new_packages)
        
        print(f"\n{'='*60}")
        print(f"✅ COMPLETE - Output: {final_package.main}")
        print(f"{'='*60}")
        
        return final_package
    
    def _merge_packages(self, packages: List[Package]) -> Package:
        """Merge packages (simplified: take first with changes)"""
        for pkg in packages:
            if pkg.metadata.get("rules_applied"):
                return pkg
        return packages[0]
    
    def get_node(self, node_id: str) -> Optional[VPrimeNode]:
        return self.node_map.get(node_id)
    
    def get_all_nodes(self) -> List[VPrimeNode]:
        return list(self.node_map.values())
    
    def broadcast_to_all(self, package) -> Dict:
        """Broadcast to all nodes"""
        results = []
        for node in self.get_all_nodes():
            result = node.receive_rule_package(package)
            results.append({"node_id": node.node_id, "result": result})
        return {
            "nodes_updated": len([r for r in results if r["result"]["status"] == "added"]),
            "total_nodes": len(results),
            "details": results
        }
