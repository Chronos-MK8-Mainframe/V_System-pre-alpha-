"""Alignment checking system"""

import time
from typing import List, Dict

from v_system.core.package import Package
from v_system.core.context import Context, ContextInference


class AlignmentChecker:
    """Validates contextual consistency at layer boundaries"""
    
    def __init__(self, threshold: float = 0.15):
        self.threshold = threshold
        self.misalignment_log: List[Dict] = []
    
    def check(self, package: Package, expected_context: Context) -> Package:
        """Verify alignment and apply corrections if needed"""
        
        actual_context = ContextInference().infer_context(
            package.main, package.history
        )
        
        # Compute contextual distance
        if actual_context.domain != expected_context.domain:
            delta = 1.0
        elif actual_context.subdomain != expected_context.subdomain:
            delta = 0.5
        else:
            delta = 0.0
        
        if abs(delta) > self.threshold:
            def correction_function(ctx: Context) -> float:
                if ctx == expected_context:
                    return 0.0
                return delta * (1.0 - ctx.similarity(expected_context))
            
            self.misalignment_log.append({
                "timestamp": time.time(),
                "delta": delta,
                "expected": expected_context,
                "actual": actual_context
            })
            
            return Package(
                main=package.main,
                history=package.history,
                undefined=package.undefined,
                alignment=correction_function,
                metadata={**package.metadata, "corrected": True, "delta": delta}
            )
        else:
            return Package(
                main=package.main,
                history=package.history,
                undefined=package.undefined,
                alignment=lambda ctx: 0.0,
                metadata=package.metadata
            )
