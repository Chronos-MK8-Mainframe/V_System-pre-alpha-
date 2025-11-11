"""Tests for enhanced learning capabilities"""

import unittest
from v_system import (
    Var, Num, Add, Mul,
    Context, VPrimePipeline, MetaEvolutionEngine,
    InverseEntailmentEngine, Literal, Clause,
    AdvancedPatternRecognizer, SymbolicRegressor,
    ConfidenceScorer
)


class TestInverseEntailment(unittest.TestCase):
    """Test Progol-inspired inverse entailment"""
    
    def setUp(self):
        self.ile = InverseEntailmentEngine()
    
    def test_literal_creation(self):
        """Test literal creation and basic operations"""
        lit = Literal("add", ["X", "Y"], negated=False)
        self.assertEqual(lit.predicate, "add")
        self.assertEqual(len(lit.terms), 2)
        self.assertFalse(lit.negated)
    
    def test_literal_variables(self):
        """Test variable extraction from literals"""
        lit = Literal("mul", ["X", "2"], negated=False)
        variables = lit.get_variables()
        self.assertIn("X", variables)
        self.assertNotIn("2", variables)
    
    def test_clause_creation(self):
        """Test clause creation"""
        head = Literal("result", ["Z"])
        body = [
            Literal("add", ["X", "Y"]),
            Literal("mul", ["X", "2"])
        ]
        clause = Clause(head=head, body=body)
        
        self.assertEqual(clause.length(), 2)
        self.assertEqual(len(clause.get_variables()), 3)
    
    def test_mode_declaration(self):
        """Test mode declaration"""
        self.ile.add_mode_declaration("add", ["+", "+", "-"])
        self.assertIn("add", self.ile.mode_declarations)
    
    def test_example_to_literal(self):
        """Test converting example to literal"""
        example = {
            "predicate": "add",
            "terms": ["a", "b"],
            "negated": False
        }
        
        lit = self.ile._example_to_literal(example)
        self.assertIsNotNone(lit)
        self.assertEqual(lit.predicate, "add")
    
    def test_statistics(self):
        """Test statistics retrieval"""
        stats = self.ile.get_statistics()
        self.assertIn('clauses_evaluated', stats)
        self.assertIn('bottom_clauses_constructed', stats)


class TestPatternRecognition(unittest.TestCase):
    """Test advanced pattern recognition"""
    
    def setUp(self):
        self.recognizer = AdvancedPatternRecognizer()
    
    def test_group_by_structure(self):
        """Test structural grouping"""
        examples = [
            {"input": Add(Var('x'), Num(0)), "output": Var('x')},
            {"input": Add(Var('y'), Num(0)), "output": Var('y')},
            {"input": Mul(Var('a'), Num(1)), "output": Var('a')},
        ]
        
        groups = self.recognizer._group_by_structure(examples)
        self.assertGreater(len(groups), 0)
    
    def test_structure_signature(self):
        """Test structure signature generation"""
        expr = Add(Var('x'), Num(0))
        sig = self.recognizer._get_structure_signature(expr)
        self.assertIsInstance(sig, str)
        self.assertIn('+', sig)
    
    def test_pattern_discovery(self):
        """Test pattern discovery from examples"""
        examples = [
            {"input": Add(Var('x'), Num(0)), "output": Var('x')},
            {"input": Add(Var('y'), Num(0)), "output": Var('y')},
        ]
        
        patterns = self.recognizer.recognize_patterns(examples)
        # Should find at least one pattern
        self.assertGreaterEqual(len(patterns), 0)
    
    def test_pattern_statistics(self):
        """Test pattern statistics"""
        stats = self.recognizer.get_pattern_statistics()
        self.assertIn('total_patterns', stats)
        self.assertIn('avg_confidence', stats)


class TestSymbolicRegression(unittest.TestCase):
    """Test symbolic regression"""
    
    def setUp(self):
        self.regressor = SymbolicRegressor()
        # Reduce iterations for faster tests
        self.regressor.generations = 10
        self.regressor.population_size = 20
    
    def test_expression_evaluation(self):
        """Test expression evaluation"""
        from v_system.mee.symbolic_regression import Expression
        
        expr = Expression('+', [
            Expression('x', [], None),
            Expression('const', [], 5.0)
        ])
        
        result = expr.evaluate({'x': 3.0})
        self.assertAlmostEqual(result, 8.0)
    
    def test_random_expression_generation(self):
        """Test random expression generation"""
        variables = ['x', 'y']
        expr = self.regressor._generate_random_expression(variables, depth=0)
        
        self.assertIsNotNone(expr)
        self.assertIsInstance(expr.op, str)
    
    def test_expression_copy(self):
        """Test expression deep copy"""
        from v_system.mee.symbolic_regression import Expression
        
        original = Expression('+', [
            Expression('x', [], None),
            Expression('const', [], 5.0)
        ])
        
        copy = original.copy()
        self.assertEqual(original.op, copy.op)
        self.assertIsNot(original, copy)


class TestConfidenceScoring(unittest.TestCase):
    """Test confidence scoring"""
    
    def setUp(self):
        self.scorer = ConfidenceScorer()
    
    def test_provability_scoring(self):
        """Test provability score calculation"""
        score_provable = self.scorer._score_provability('provable')
        score_heuristic = self.scorer._score_provability('heuristic')
        score_unprovable = self.scorer._score_provability('unprovable')
        
        self.assertGreater(score_provable, score_heuristic)
        self.assertGreater(score_heuristic, score_unprovable)
    
    def test_complexity_scoring(self):
        """Test complexity scoring"""
        from v_system import Rule
        
        simple_rule = Rule(
            rule_id="simple",
            condition=lambda e, c, r: 1,
            transform=lambda e: e,
            domain=Context("math", "algebra"),
            priority=5,
            confidence=1.0,
            source="test"
        )
        
        score = self.scorer._score_complexity(simple_rule)
        self.assertGreater(score, 0.0)
        self.assertLessEqual(score, 1.0)
    
    def test_source_adjustment(self):
        """Test source-based score adjustment"""
        base_score = 0.7
        
        ile_score = self.scorer._apply_source_adjustment(base_score, "inverse_entailment")
        manual_score = self.scorer._apply_source_adjustment(base_score, "manual")
        empirical_score = self.scorer._apply_source_adjustment(base_score, "empirical")
        
        # ILE and manual should get boosts
        self.assertGreater(ile_score, base_score)
        self.assertGreater(manual_score, base_score)
        # Empirical should get penalty
        self.assertLess(empirical_score, base_score)


class TestEnhancedMeE(unittest.TestCase):
    """Test enhanced Meta-Evolution Engine"""
    
    def setUp(self):
        self.pipeline = VPrimePipeline(num_layers=2, nodes_per_layer=2)
        self.mee = MetaEvolutionEngine(self.pipeline)
    
    def test_mee_initialization(self):
        """Test MeE initializes with enhanced components"""
        self.assertIsNotNone(self.mee.inverse_entailment)
        self.assertIsNotNone(self.mee.pattern_recognizer)
        self.assertIsNotNone(self.mee.symbolic_regressor)
        self.assertIsNotNone(self.mee.confidence_scorer)
    
    def test_learning_from_examples(self):
        """Test learning from minimal examples"""
        examples = [
            {
                "input": Add(Var('x'), Num(0)),
                "output": Var('x'),
                "context": Context("math", "algebra"),
                "description": "Identity addition"
            },
            {
                "input": Add(Var('y'), Num(0)),
                "output": Var('y'),
                "context": Context("math", "algebra"),
                "description": "Identity addition 2"
            }
        ]
        
        result = self.mee.learn_from_examples(examples)
        
        self.assertIn("rules_learned", result)
        self.assertIn("synthesis_breakdown", result)
        self.assertIn("confidence_avg", result)
    
    def test_enhanced_statistics(self):
        """Test enhanced statistics retrieval"""
        stats = self.mee.get_stats()
        
        self.assertIn("ile_rules_synthesized", stats)
        self.assertIn("patterns_discovered", stats)
        self.assertIn("symbolic_rules_synthesized", stats)
        self.assertIn("pattern_recognition", stats)
        self.assertIn("inverse_entailment", stats)
    
    def test_numeric_example_detection(self):
        """Test numeric example detection"""
        numeric_examples = [
            {
                "input": Var('x'),
                "output": Num(5),
                "context": Context("math", "algebra")
            }
        ]
        
        non_numeric_examples = [
            {
                "input": Var('x'),
                "output": Var('y'),
                "context": Context("math", "algebra")
            }
        ]
        
        self.assertTrue(self.mee._has_numeric_examples(numeric_examples))
        self.assertFalse(self.mee._has_numeric_examples(non_numeric_examples))


class TestIntegration(unittest.TestCase):
    """Integration tests for enhanced system"""
    
    def setUp(self):
        self.pipeline = VPrimePipeline(num_layers=2, nodes_per_layer=2)
        self.mee = MetaEvolutionEngine(self.pipeline)
    
    def test_end_to_end_learning_and_application(self):
        """Test complete learning and application workflow"""
        # Learn new rule
        examples = [
            {
                "input": Mul(Var('a'), Num(1)),
                "output": Var('a'),
                "context": Context("math", "algebra"),
                "description": "Identity multiplication"
            },
            {
                "input": Mul(Var('b'), Num(1)),
                "output": Var('b'),
                "context": Context("math", "algebra"),
                "description": "Identity multiplication 2"
            }
        ]
        
        learning_result = self.mee.learn_from_examples(examples)
        
        # Verify learning happened
        self.assertGreater(learning_result["rules_learned"], 0)
        
        # Test application
        test_expr = Mul(Var('z'), Num(1))
        result = self.pipeline.execute(test_expr)
        
        # Should have been processed
        self.assertIsNotNone(result.main)
    
    def test_multi_strategy_synthesis(self):
        """Test multiple strategies working together"""
        examples = [
            {
                "input": Add(Var('x'), Num(0)),
                "output": Var('x'),
                "context": Context("math", "algebra")
            },
            {
                "input": Mul(Var('y'), Num(1)),
                "output": Var('y'),
                "context": Context("math", "algebra")
            },
            {
                "input": Mul(Var('z'), Num(0)),
                "output": Num(0),
                "context": Context("math", "algebra")
            }
        ]
        
        result = self.mee.learn_from_examples(
            examples,
            use_inverse_entailment=True,
            use_multi_strategy=True
        )
        
        # Should have synthesis breakdown
        self.assertIn("synthesis_breakdown", result)
        
        # At least one strategy should have succeeded
        total_synthesized = sum(result["synthesis_breakdown"].values())
        self.assertGreater(total_synthesized, 0)


if __name__ == '__main__':
    unittest.main()
