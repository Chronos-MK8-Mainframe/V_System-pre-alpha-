"""Package system for data flow"""

from typing import Set, Dict, Any, List, Callable
from dataclasses import dataclass, field
from copy import deepcopy

from v_system.core.symbolic_expr import SymbolicExpression
from v_system.core.context import Context


@dataclass
class Package:
    """Complete computational unit with metadata"""
    main: SymbolicExpression
    history: List[SymbolicExpression] = field(default_factory=list)
    undefined: Set[str] = field(default_factory=set)
    alignment: Callable[[Context], float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if self.alignment is None:
            self.alignment = lambda ctx: 0.0  # Perfect alignment by default
    
    def copy(self):
        """Create deep copy of package"""
        return Package(
            main=self.main.copy(),
            history=[expr.copy() for expr in self.history],
            undefined=self.undefined.copy(),
            alignment=self.alignment,
            metadata=self.metadata.copy()
        )


class ReadBus:
    """Immutable reference to original input"""
    
    def __init__(self, original_package: Package):
        self._original = deepcopy(original_package)
    
    def get(self) -> Package:
        """Get immutable copy of original package"""
        return deepcopy(self._original)
