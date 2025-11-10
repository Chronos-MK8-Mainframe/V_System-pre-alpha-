"""Tests for V' node and pipeline"""

import unittest
from v_system import Var, Num, Add, Mul, VPrimePipeline


class TestVPrime(unittest.TestCase):
    
    def setUp(self):
        """Create pipeline for testing"""
        self.pipeline = VPrimePipeline(num_layers=2, nodes_per_layer=1)
    
    def test_identity_addition(self):
        """Test x + 0 → x"""
        expr = Add(Var('x'), Num(0))
        result = self.pipeline.execute(expr)
        self.assertEqual(str(result.main), 'x')
    
    def test_identity_addition_reversed(self):
        """Test 0 + y → y"""
        expr = Add(Num(0), Var('y'))
        result = self.pipeline.execute(expr)
        self.assertEqual(str(result.main), 'y')
    
    def test_identity_multiplication(self):
        """Test a * 1 → a"""
        expr = Mul(Var('a'), Num(1))
        result = self.pipeline.execute(expr)
        self.assertEqual(str(result.main), 'a')
    
    def test_identity_multiplication_reversed(self):
        """Test 1 * b → b"""
        expr = Mul(Num(1), Var('b'))
        result = self.pipeline.execute(expr)
        self.assertEqual(str(result.main), 'b')
    
    def test_zero_multiplication(self):
        """Test z * 0 → 0"""
        expr = Mul(Var('z'), Num(0))
        result = self.pipeline.execute(expr)
        self.assertEqual(str(result.main), '0')
    
    def test_zero_multiplication_reversed(self):
        """Test 0 * w → 0"""
        expr = Mul(Num(0), Var('w'))
        result = self.pipeline.execute(expr)
        self.assertEqual(str(result.main), '0')


if __name__ == '__main__':
    unittest.main()
