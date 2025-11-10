"""Signature management for rule updates"""

import time
import hashlib
from typing import Set


class SignatureManager:
    """Manage one-time and global signatures"""
    
    def __init__(self):
        self.used_one_time: Set[str] = set()
        self.global_signature = "GLOBAL_SIG_" + \
            hashlib.md5(str(time.time()).encode()).hexdigest()[:12]
    
    def generate_one_time(self) -> str:
        """
        Generate one-time signature for targeted updates
        
        Returns:
            Unique signature string prefixed with 'sig_'
        """
        timestamp = str(time.time())
        counter = len(self.used_one_time)
        sig = hashlib.md5(f"{timestamp}{counter}".encode()).hexdigest()[:16]
        self.used_one_time.add(sig)
        return f"sig_{sig}"
    
    def get_global_signature(self) -> str:
        """
        Get global signature for broadcasting to all V' nodes
        
        Returns:
            Global signature string prefixed with 'GLOBAL_SIG_'
        """
        return self.global_signature
    
    def is_valid(self, signature: str) -> bool:
        """Check if signature is valid format"""
        return signature.startswith("sig_") or signature.startswith("GLOBAL_SIG_")
