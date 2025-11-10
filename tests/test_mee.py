"""Tests for Meta-Evolution Engine"""

import unittest
from v_system import (
    Context, Rule, VPrimePipeline, MetaEvolutionEngine
)


class TestMeE(unittest.TestCase):
    
    def setUp(self):
        """Create MeE for testing"""
        self.pipeline = VPrimePipeline(num_layers=2, nodes_per_layer=2)
        self.mee = MetaEvolutionEngine(self.pipeline)
    
    def test_mee_initialization(self):
        """Test MeE initializes with core rules"""
        self.assertGreater(len(self.mee.R_global), 0)
        self.assertEqual(self.mee.rules_processed, 0)
        self.assertEqual(self.mee.rules_accepted, 0)
    
    def test_process_candidate_rule_accepts_valid(self):
        """Test MeE accepts valid candidate rule"""
        candidate = Rule(
            rule_id="test_rule",
            condition=lambda expr, ctx, refs: 0,
            transform=lambda expr: expr,
            domain=Context("math", "algebra"),
            priority=5,
            confidence=0.8,
            source="test"
        )
        
        result = self.mee.process_candidate_rule(candidate)
        self.assertEqual(result["status"], "accepted")
        self.assertIn("rule_id", result)
    
    def test_broadcast_global_rule(self):
        """Test global broadcast to all nodes"""
        test_rule = Rule(
            rule_id="broadcast_test",
            condition=lambda expr, ctx, refs: 0,
            transform=lambda expr: expr,
            domain=Context("math", "algebra"),
            priority=10,
            confidence=1.0,
            source="test"
        )
        
        result = self.mee.broadcast_global_rule(test_rule)
        self.assertIn("nodes_updated", result)
        self.assertIn("total_nodes", result)
        self.assertEqual(result["total_nodes"], 4)  # 2 layers × 2 nodes
    
    def test_send_to_specific_nodes(self):
        """Test targeted update to specific nodes"""
        test_rule = Rule(
            rule_id="targeted_test",
            condition=lambda expr, ctx, refs: 0,
            transform=lambda expr: expr,
            domain=Context("math", "algebra"),
            priority=8,
            confidence=0.9,
            source="test"
        )
        
        result = self.mee.send_to_specific_nodes(test_rule, ["L1_C0", "L2_C1"])
        self.assertIn("successful", result)
        self.assertEqual(result["total"], 2)
    
    def test_get_stats(self):
        """Test statistics retrieval"""
        stats = self.mee.get_stats()
        self.assertIn("global_rules", stats)
        self.assertIn("rules_processed", stats)
        self.assertIn("acceptance_rate", stats)
        self.assertIn("smt_enabled", stats)


if __name__ == '__main__':
    unittest.main()
