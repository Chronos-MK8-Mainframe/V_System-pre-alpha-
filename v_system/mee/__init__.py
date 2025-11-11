"""Meta-Evolution Engine with enhanced learning capabilities"""

from v_system.mee.engine import MetaEvolutionEngine
from v_system.mee.contradiction import (
    HeuristicContradictionDetector, ConflictType, ConflictResult
)
from v_system.mee.provability import ProvabilityEngine
from v_system.mee.signatures import SignatureManager
from v_system.mee.package import RulePackage
from v_system.mee.pattern_recognition import (
    AdvancedPatternRecognizer, Pattern
)
from v_system.mee.symbolic_regression import (
    SymbolicRegressor, Expression
)
from v_system.mee.multi_example_synthesis import (
    MultiExampleSynthesizer, SynthesisResult
)
from v_system.mee.confidence_scoring import ConfidenceScorer
from v_system.mee.inverse_entailment import (
    InverseEntailmentEngine, Clause, Literal, ModeDeclaration
)

__all__ = [
    # Core components
    'MetaEvolutionEngine',
    'HeuristicContradictionDetector', 
    'ConflictType', 
    'ConflictResult',
    'ProvabilityEngine',
    'SignatureManager',
    'RulePackage',
    
    # Enhanced learning components
    'AdvancedPatternRecognizer',
    'Pattern',
    'SymbolicRegressor',
    'Expression',
    'MultiExampleSynthesizer',
    'SynthesisResult',
    'ConfidenceScorer',
    
    # Inverse entailment (Progol-inspired)
    'InverseEntailmentEngine',
    'Clause',
    'Literal',
    'ModeDeclaration'
]
