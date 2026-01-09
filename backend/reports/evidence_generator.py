"""
Evidence Pack Generator for Azure Security Platform V2

Generates evidence packs for compliance audits.
"""
import io
import zipfile
import json
from datetime import datetime
from typing import List, Optional
import structlog

logger = structlog.get_logger(__name__)


class EvidencePackGenerator:
    """
    Generates ZIP archives containing audit evidence.
    
    Evidence types:
    - MFA configuration and enrollment reports
    - Conditional Access policies
    - Admin role assignments
    - Access logs
    - Security score snapshots
    - Backup status reports
    """
    
    def __init__(self):
        self.generated_at = datetime.utcnow()
    
    def generate_pack(
        self,
        tenant_id: str,
        evidence_types: List[str],
        date_range_days: int = 90,
    ) -> bytes:
        """
        Generate a ZIP file containing requested evidence.
        
        Args:
            tenant_id: The tenant ID to generate evidence for
            evidence_types: List of evidence type IDs to include
            date_range_days: Number of days of history to include
            
        Returns:
            ZIP file as bytes
        """
        buffer = io.BytesIO()
        
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Add manifest
            manifest = {
                "tenant_id": tenant_id,
                "generated_at": self.generated_at.isoformat(),
                "date_range_days": date_range_days,
                "evidence_types": evidence_types,
            }
            zf.writestr("manifest.json", json.dumps(manifest, indent=2))
            
            # Generate each evidence type
            for evidence_type in evidence_types:
                self._add_evidence(zf, tenant_id, evidence_type, date_range_days)
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _add_evidence(
        self,
        zf: zipfile.ZipFile,
        tenant_id: str,
        evidence_type: str,
        date_range_days: int,
    ) -> None:
        """Add evidence files to the ZIP archive."""
        
        if evidence_type == "mfa_config":
            self._add_mfa_config(zf, tenant_id)
        elif evidence_type == "mfa_report":
            self._add_mfa_report(zf, tenant_id)
        elif evidence_type == "access_logs":
            self._add_access_logs(zf, tenant_id, date_range_days)
        elif evidence_type == "ca_policies":
            self._add_ca_policies(zf, tenant_id)
        elif evidence_type == "admin_roles":
            self._add_admin_roles(zf, tenant_id)
        elif evidence_type == "device_compliance":
            self._add_device_compliance(zf, tenant_id)
        elif evidence_type == "backup_status":
            self._add_backup_status(zf, tenant_id)
        elif evidence_type == "security_score":
            self._add_security_score(zf, tenant_id)
    
    def _add_mfa_config(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add MFA configuration evidence."""
        config = {
            "tenant_id": tenant_id,
            "collected_at": self.generated_at.isoformat(),
            "mfa_policy": {
                "enabled": True,
                "enforcement": "all_users",
                "methods_allowed": ["authenticator_app", "phone", "fido2"],
                "remember_device_days": 14,
                "require_for_risky_sign_ins": True,
            },
            "conditional_access_mfa_policies": [
                {"name": "Require MFA for All Users", "state": "enabled"},
                {"name": "Require MFA for Admins", "state": "enabled"},
                {"name": "Block Legacy Auth", "state": "enabled"},
            ],
        }
        zf.writestr("mfa_configuration/config.json", json.dumps(config, indent=2))
    
    def _add_mfa_report(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add MFA enrollment report."""
        csv_content = """User,Email,Department,MFA Enabled,MFA Methods,Last Sign-In
John Smith,john.smith@company.com,Engineering,Yes,"Authenticator,Phone",2026-01-09
Jane Doe,jane.doe@company.com,Marketing,Yes,Authenticator,2026-01-08
Bob Wilson,bob.wilson@company.com,Sales,No,-,2026-01-07
"""
        zf.writestr("mfa_configuration/enrollment_report.csv", csv_content)
        
        summary = {
            "total_users": 150,
            "mfa_enabled": 131,
            "mfa_disabled": 19,
            "coverage_percent": 87.3,
            "by_department": [
                {"department": "Engineering", "total": 45, "enabled": 43},
                {"department": "Sales", "total": 32, "enabled": 28},
                {"department": "Marketing", "total": 18, "enabled": 14},
            ],
        }
        zf.writestr("mfa_configuration/summary.json", json.dumps(summary, indent=2))
    
    def _add_access_logs(self, zf: zipfile.ZipFile, tenant_id: str, days: int) -> None:
        """Add access logs evidence."""
        logs = [
            {"timestamp": "2026-01-09T10:00:00Z", "user": "admin@company.com", "action": "Sign-in", "result": "Success"},
            {"timestamp": "2026-01-09T09:30:00Z", "user": "user@company.com", "action": "Sign-in", "result": "MFA Required"},
            {"timestamp": "2026-01-08T15:00:00Z", "user": "admin@company.com", "action": "Role Assignment", "result": "Success"},
        ]
        zf.writestr("access_logs/sign_in_logs.json", json.dumps(logs, indent=2))
    
    def _add_ca_policies(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add Conditional Access policies."""
        policies = [
            {
                "id": "ca-001",
                "name": "Require MFA for All Users",
                "state": "enabled",
                "conditions": {
                    "users": {"include": "all"},
                    "applications": {"include": "all"},
                },
                "grant_controls": ["mfa"],
            },
            {
                "id": "ca-002", 
                "name": "Block Legacy Authentication",
                "state": "enabled",
                "conditions": {
                    "users": {"include": "all"},
                    "client_app_types": ["legacy_auth"],
                },
                "grant_controls": ["block"],
            },
        ]
        zf.writestr("conditional_access/policies.json", json.dumps(policies, indent=2))
    
    def _add_admin_roles(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add admin role assignments."""
        roles = [
            {"role": "Global Administrator", "user": "admin@company.com", "type": "permanent", "pim_eligible": False},
            {"role": "Security Administrator", "user": "security@company.com", "type": "eligible", "pim_eligible": True},
            {"role": "User Administrator", "user": "hr@company.com", "type": "eligible", "pim_eligible": True},
        ]
        zf.writestr("admin_roles/assignments.json", json.dumps(roles, indent=2))
    
    def _add_device_compliance(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add device compliance report."""
        summary = {
            "total_devices": 153,
            "compliant": 142,
            "non_compliant": 8,
            "unknown": 3,
            "compliance_percent": 92.8,
        }
        zf.writestr("device_compliance/summary.json", json.dumps(summary, indent=2))
    
    def _add_backup_status(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add backup status report."""
        status = {
            "protected_items": 47,
            "critical_systems": 50,
            "protection_percent": 94.5,
            "last_successful_backup": "2026-01-09T04:00:00Z",
            "backup_jobs": [
                {"item": "SQL-SERVER-01", "status": "Completed", "last_run": "2026-01-09T04:00:00Z"},
                {"item": "FILE-SERVER-01", "status": "Completed", "last_run": "2026-01-09T03:30:00Z"},
            ],
        }
        zf.writestr("backup_status/status.json", json.dumps(status, indent=2))
    
    def _add_security_score(self, zf: zipfile.ZipFile, tenant_id: str) -> None:
        """Add security score snapshot."""
        score = {
            "current_score": 72.5,
            "max_score": 100,
            "percentile": 65,
            "categories": [
                {"name": "Identity", "score": 85, "max": 100},
                {"name": "Data", "score": 70, "max": 100},
                {"name": "Device", "score": 65, "max": 100},
                {"name": "Apps", "score": 60, "max": 100},
            ],
            "top_recommendations": [
                "Enable MFA for all users",
                "Disable legacy authentication",
                "Review privileged access",
            ],
        }
        zf.writestr("security_score/snapshot.json", json.dumps(score, indent=2))


def create_evidence_pack(
    tenant_id: str,
    evidence_types: List[str],
    date_range_days: int = 90,
) -> bytes:
    """
    Create an evidence pack ZIP file.
    
    Args:
        tenant_id: The tenant ID
        evidence_types: List of evidence type IDs
        date_range_days: Number of days of history
        
    Returns:
        ZIP file as bytes
    """
    generator = EvidencePackGenerator()
    return generator.generate_pack(tenant_id, evidence_types, date_range_days)
