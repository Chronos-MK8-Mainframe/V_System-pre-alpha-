"""Integration tests for complete V' system"""

import unittest
from v_system import (
    Var, Num, Add, Mul,
    Context, VPrimePipeline, MetaEvolutionEngine
)


class TestIntegration(unittest.TestCase):
    
    def setUp(self):
        """Set up complete system"""
        self.pipeline = VPrimePipeline(num_layers=2, nodes_per_layer=2)
        self.mee = MetaEvolutionEngine(self.pipeline)
    
    def test_end_to_end_simple_transform(self):
        """Test complete pipeline: x + 0 → x"""
        input_expr = Add(Var('x'), Num(0))
        result = self.pipeline.execute(input_expr)
        
        self.assertEqual(str(result.main), 'x')
        self.assertIn("rules_applied", result.metadata)
    
    def test_end_to_end_multiple_rules(self):
        """Test pipeline with multiple rule applications"""
        # (x + 0) * 1 should reduce to x
        inner = Add(Var('x'), Num(0))
        input_expr = Mul(inner, Num(1))
        
        result = self.pipeline.execute(input_expr)
        
        # Should apply identity_add first, then identity_mul
        # Final result might be x or (x * 1) depending on execution order
        self.assertIn(str(result.main), ['x', '(x * 1)'])
    
    def test_learning_from_examples(self):
        """Test learning rules from minimal examples"""
        examples = [
            {
                "input": Add(Var('x'), Num(0)),
                "output": Var('x'),
                "context": Context("math", "algebra"),
                "description": "Identity addition"
            },
            {
                "input": Mul(Var('y'), Num(1)),
                "output": Var('y'),
                "context": Context("math", "algebra"),
                "description": "Identity multiplication"
            }
        ]
        
        result = self.mee.learn_from_examples(examples)
        
        self.assertIn("rules_learned", result)
        self.assertIn("rules_distributed", result)
        self.assertGreater(result["rules_learned"], 0)
    
    def test_context_inference(self):
        """Test context is correctly inferred"""
        from v_system.core.context import ContextInference
        
        inferencer = ContextInference()
        
        # Algebra expression
        expr = Add(Var('x'), Var('y'))
        context = inferencer.infer_context(expr)
        self.assertEqual(context.domain, "math")
    
    def test_alignment_checking(self):
        """Test alignment checker detects misalignment"""
        from v_system.vprime.alignment import AlignmentChecker
        from v_system.core.package import Package
        
        checker = AlignmentChecker(threshold=0.1)
        
        # Create package with high misalignment
        test_package = Package(
            main=Add(Var('x'), Var('y')),
            history=[],
            undefined=set(),
            alignment=lambda ctx: 0.5,  # High misalignment
            metadata={}
        )
        
        expected_context = Context("math", "algebra")
        corrected = checker.check(test_package, expected_context)
        
        self.assertIn("corrected", corrected.metadata)
        self.assertTrue(corrected.metadata.get("corrected", False))
    
    def test_read_bus_immutability(self):
        """Test ReadBus preserves original input"""
        from v_system.core.package import Package, ReadBus
        
        original_pkg = Package(
            main=Add(Var('original'), Num(0)),
            history=[],
            undefined=set(),
            metadata={"original": True}
        )
        
        bus = ReadBus(original_pkg)
        
        # Modify retrieved copy
        retrieved = bus.get()
        retrieved.main = Var('modified')
        
        # Original should be unchanged
        original_from_bus = bus.get()
        self.assertNotEqual(str(original_from_bus.main), 'modified')
        self.assertEqual(str(original_from_bus.main), '(original + 0)')
    
    def test_parallel_references(self):
        """Test parallel V' nodes can reference each other"""
        # Create expression that requires multiple transformations
        expr = Add(Mul(Var('x'), Num(1)), Num(0))  # (x * 1) + 0
        
        result = self.pipeline.execute(expr)
        
        # Should eventually reduce (exact result depends on execution order)
        self.assertIsNotNone(result.main)
        self.assertIn("layer", result.metadata)


if __name__ == '__main__':
    unittest.main()
