"""
Collectors module for Azure Security Platform V2

Data collectors for various security metrics:
- Secure Score
- Identity (MFA, PIM, Risky Users)
- Devices (Intune compliance)
- Threats (Security alerts)
- Backup (Azure Backup health)
"""
from .secure_score import SecureScoreCollector
from .identity import IdentityCollector
from .devices import DeviceCollector
from .threats import ThreatCollector
from .backup import BackupCollector

__all__ = [
    "SecureScoreCollector",
    "IdentityCollector",
    "DeviceCollector",
    "ThreatCollector",
    "BackupCollector",
]
