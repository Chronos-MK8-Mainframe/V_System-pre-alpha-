"""Meta-Evolution Engine components"""

from v_system.mee.engine import MetaEvolutionEngine
from v_system.mee.contradiction import (
    HeuristicContradictionDetector, ConflictType, ConflictResult
)
from v_system.mee.provability import ProvabilityEngine
from v_system.mee.signatures import SignatureManager
from v_system.mee.package import RulePackage

__all__ = [
    'MetaEvolutionEngine',
    'HeuristicContradictionDetector', 'ConflictType', 'ConflictResult',
    'ProvabilityEngine',
    'SignatureManager',
    'RulePackage'
]
