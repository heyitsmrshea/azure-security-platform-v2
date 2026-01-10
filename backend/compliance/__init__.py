"""
Compliance Framework Mapping Module

Maps security findings to compliance frameworks:
- CIS Azure Foundations Benchmark v2
- NIST 800-53
- SOC 2
- ISO 27001
"""
from .mapper import ComplianceMapper

__all__ = ["ComplianceMapper"]
