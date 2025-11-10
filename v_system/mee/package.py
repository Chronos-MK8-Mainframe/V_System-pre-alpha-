"""Rule package for distribution"""

import time
from typing import Optional, List, Dict
from dataclasses import dataclass, field

from v_system.core.rule import Rule
from v_system.core.context import Context


@dataclass
class RulePackage:
    """
    Package for delivering rule updates to V' nodes
    
    Attributes:
        signature: Authentication signature (one-time or global)
        target_node_ids: List of target node IDs (None = broadcast to all)
        target_context: Context for which rule is applicable
        rule: The rule to be distributed
        operation: Type of operation ("add", "modify", "delete")
        priority: Priority level for the operation
        timestamp: Time of package creation
        target_rule_id: ID of rule to modify/delete (for modify/delete ops)
        source: Source of the package ("mee", "admin", etc.)
        metadata: Additional metadata
    """
    signature: str
    target_node_ids: Optional[List[str]]
    target_context: Context
    rule: Rule
    operation: str  # "add", "modify", "delete"
    priority: int = 5
    timestamp: float = field(default_factory=time.time)
    target_rule_id: Optional[str] = None
    source: str = "mee"
    metadata: Dict = field(default_factory=dict)
    
    def is_broadcast(self) -> bool:
        """Check if this is a broadcast package"""
        return self.target_node_ids is None
    
    def is_targeted(self) -> bool:
        """Check if this is a targeted package"""
        return self.target_node_ids is not None and len(self.target_node_ids) > 0
