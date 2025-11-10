"""
V' System - Modular Implementation
Symbolic reasoning system with precision-first learning
"""

__version__ = "1.0.0"

from v_system.core.symbolic_expr import SymbolicExpression, Var, Num, Add, Mul, Sub, Div
from v_system.core.context import Context, ContextInference, Reference, ContextBundle
from v_system.core.rule import Rule
from v_system.core.package import Package, ReadBus

from v_system.vprime.node import VPrimeNode
from v_system.vprime.pipeline import VPrimePipeline
from v_system.vprime.alignment import AlignmentChecker

from v_system.mee.engine import MetaEvolutionEngine
from v_system.mee.contradiction import HeuristicContradictionDetector, ConflictType, ConflictResult
from v_system.mee.provability import ProvabilityEngine
from v_system.mee.signatures import SignatureManager
from v_system.mee.package import RulePackage

from v_system.rules.core_rules import create_core_rules

__all__ = [
    # Core
    'SymbolicExpression', 'Var', 'Num', 'Add', 'Mul', 'Sub', 'Div',
    'Context', 'ContextInference', 'Reference', 'ContextBundle',
    'Rule', 'Package', 'ReadBus',
    
    # V' System
    'VPrimeNode', 'VPrimePipeline', 'AlignmentChecker',
    
    # MeE
    'MetaEvolutionEngine', 'HeuristicContradictionDetector',
    'ProvabilityEngine', 'SignatureManager', 'RulePackage',
    'ConflictType', 'ConflictResult',
    
    # Rules
    'create_core_rules',
]
