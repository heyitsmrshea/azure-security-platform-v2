"""
Compliance Framework Mapper

Maps security findings and assessment data to compliance framework controls.
"""
import json
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)

# Framework data directory
# mapper.py -> compliance -> backend -> azure_security_platform_v2 -> data/frameworks
FRAMEWORKS_DIR = Path(__file__).parent.parent.parent / "data" / "frameworks"


class ComplianceMapper:
    """
    Maps security findings to compliance framework controls.
    
    Supported frameworks:
    - cis: CIS Microsoft Azure Foundations Benchmark v2
    - nist: NIST 800-53 Rev 5
    - soc2: SOC 2 Type II
    - iso27001: ISO 27001:2022 Annex A
    """
    
    # Control mappings from findings to framework controls
    FINDING_TO_CONTROL_MAP = {
        # MFA findings
        "MFA-001": {
            "cis": ["1.1.2"],
            "nist": ["IA-2", "IA-2(1)", "IA-2(2)"],
            "soc2": ["CC6.1"],
            "iso27001": ["A.9.4.2"],
        },
        "MFA-002": {
            "cis": ["1.1.1"],
            "nist": ["IA-2", "IA-2(1)"],
            "soc2": ["CC6.1"],
            "iso27001": ["A.9.4.2"],
        },
        # Privileged access findings
        "PRIV-001": {
            "cis": ["1.1.3", "1.1.4"],
            "nist": ["AC-6", "AC-6(1)", "AC-6(5)"],
            "soc2": ["CC6.3"],
            "iso27001": ["A.9.2.3"],
        },
        # Risky users
        "RISK-001": {
            "cis": ["1.2.6"],
            "nist": ["IA-5", "SI-4"],
            "soc2": ["CC6.1", "CC7.2"],
            "iso27001": ["A.9.4.3"],
        },
        # Device compliance
        "DEV-001": {
            "cis": ["3.1", "3.2"],
            "nist": ["CM-2", "CM-6"],
            "soc2": ["CC6.6", "CC6.7"],
            "iso27001": ["A.8.1.1", "A.12.6.1"],
        },
        # Backup
        "BKP-001": {
            "cis": ["5.1.4"],
            "nist": ["CP-9", "CP-10"],
            "soc2": ["A1.2"],
            "iso27001": ["A.12.3.1"],
        },
        "BKP-002": {
            "cis": ["5.1.4"],
            "nist": ["CP-9"],
            "soc2": ["A1.2"],
            "iso27001": ["A.12.3.1"],
        },
        # Threats
        "THR-001": {
            "cis": ["2.1.15"],
            "nist": ["IR-4", "IR-5", "IR-6"],
            "soc2": ["CC7.3", "CC7.4"],
            "iso27001": ["A.16.1.4", "A.16.1.5"],
        },
    }
    
    def __init__(self, frameworks: list[str]):
        """
        Initialize mapper with specified frameworks.
        
        Args:
            frameworks: List of framework IDs to map (cis, nist, soc2, iso27001)
        """
        self.frameworks = [f.lower() for f in frameworks]
        self.framework_data = {}
        
        # Load framework definitions
        self._load_frameworks()
    
    def _load_frameworks(self):
        """Load framework definition files."""
        framework_files = {
            "cis": "cis_azure_v2.json",
            "nist": "nist_800_53.json",
            "soc2": "soc2_criteria.json",
            "iso27001": "iso27001_annex_a.json",
        }
        
        for fw_id in self.frameworks:
            filename = framework_files.get(fw_id)
            if not filename:
                logger.warning(f"Unknown framework: {fw_id}")
                continue
            
            filepath = FRAMEWORKS_DIR / filename
            if filepath.exists():
                try:
                    with open(filepath) as f:
                        self.framework_data[fw_id] = json.load(f)
                    logger.debug(f"Loaded framework: {fw_id}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to load {filename}: {e}")
            else:
                logger.warning(f"Framework file not found: {filepath}")
                # Create stub data
                self.framework_data[fw_id] = {"framework": {"id": fw_id}, "sections": []}
    
    def map_to_framework(
        self,
        framework: str,
        findings: list[dict],
        raw_data: dict,
    ) -> dict:
        """
        Map findings to a specific compliance framework.
        
        Args:
            framework: Framework ID (cis, nist, soc2, iso27001)
            findings: List of security findings
            raw_data: Raw assessment data
            
        Returns:
            Framework compliance result
        """
        fw_id = framework.lower()
        fw_data = self.framework_data.get(fw_id, {})
        
        # Get all controls from framework
        all_controls = self._extract_all_controls(fw_data)
        total_controls = len(all_controls)
        
        # Map findings to failed controls
        failed_controls = set()
        control_findings = {}  # control_id -> list of findings
        
        for finding in findings:
            finding_id = finding.get("id", "").split("-")[0] + "-" + finding.get("id", "").split("-")[1] if "-" in finding.get("id", "") else ""
            
            # Get mapped controls for this finding
            mapped = self.FINDING_TO_CONTROL_MAP.get(finding_id, {})
            framework_controls = mapped.get(fw_id, [])
            
            # Also check finding's explicit framework_controls field
            explicit_controls = finding.get("framework_controls", [])
            for ctrl in explicit_controls:
                if ctrl.startswith(fw_id.upper()) or not any(ctrl.startswith(f) for f in ["CIS", "NIST", "SOC2", "ISO"]):
                    framework_controls.append(ctrl.split(" ")[-1])
            
            for control_id in framework_controls:
                failed_controls.add(control_id)
                if control_id not in control_findings:
                    control_findings[control_id] = []
                control_findings[control_id].append({
                    "id": finding.get("id"),
                    "title": finding.get("title"),
                    "severity": finding.get("severity"),
                })
        
        # Calculate passed controls
        passed_controls = total_controls - len(failed_controls)
        
        # Calculate score
        score = (passed_controls / total_controls * 100) if total_controls > 0 else 0
        
        # Apply penalty for critical findings
        critical_count = len([f for f in findings if f.get("severity") == "critical"])
        penalty = min(15, critical_count * 5)
        score = max(0, score - penalty)
        
        # Build control status list
        control_status = []
        for control in all_controls:
            control_id = control.get("id", "")
            is_failed = control_id in failed_controls
            
            status = {
                "id": control_id,
                "name": control.get("name", ""),
                "status": "fail" if is_failed else "pass",
                "findings": control_findings.get(control_id, []) if is_failed else [],
            }
            control_status.append(status)
        
        return {
            "framework": {
                "id": fw_id,
                "name": fw_data.get("framework", {}).get("name", fw_id),
                "version": fw_data.get("framework", {}).get("version", ""),
            },
            "score": round(score, 1),
            "controls": {
                "total": total_controls,
                "passed": passed_controls,
                "failed": len(failed_controls),
            },
            "failed_controls": list(failed_controls),
            "control_status": control_status,
            "findings_mapped": len([f for f in findings if any(
                self.FINDING_TO_CONTROL_MAP.get(f.get("id", "").rsplit("-", 1)[0], {}).get(fw_id)
                for _ in [1]
            )]),
        }
    
    def _extract_all_controls(self, fw_data: dict) -> list[dict]:
        """Extract all controls from framework data.
        
        Handles different framework JSON structures:
        - CIS: sections -> controls
        - NIST: control_families -> controls
        - SOC2: trust_service_categories -> criteria
        - ISO27001: control_categories -> controls
        """
        controls = []
        
        # CIS Azure format: sections -> controls
        for section in fw_data.get("sections", []):
            for control in section.get("controls", []):
                controls.append({
                    "id": control.get("id"),
                    "name": control.get("name"),
                    "section": section.get("name"),
                })
        
        # NIST 800-53 format: control_families -> controls
        for family in fw_data.get("control_families", []):
            for control in family.get("controls", []):
                controls.append({
                    "id": control.get("id"),
                    "name": control.get("name"),
                    "section": family.get("name"),
                })
        
        # SOC 2 format: trust_service_categories -> criteria
        for category in fw_data.get("trust_service_categories", []):
            for criterion in category.get("criteria", []):
                controls.append({
                    "id": criterion.get("id"),
                    "name": criterion.get("name"),
                    "section": category.get("name"),
                })
        
        # ISO 27001 format: control_categories -> controls
        for category in fw_data.get("control_categories", []):
            for control in category.get("controls", []):
                controls.append({
                    "id": control.get("id"),
                    "name": control.get("name"),
                    "section": category.get("name"),
                })
        
        return controls
    
    def get_framework_summary(self, framework: str) -> dict:
        """Get summary information about a framework."""
        fw_data = self.framework_data.get(framework.lower(), {})
        
        return {
            "id": framework.lower(),
            "name": fw_data.get("framework", {}).get("name", framework),
            "version": fw_data.get("framework", {}).get("version", ""),
            "total_controls": len(self._extract_all_controls(fw_data)),
            "sections": len(fw_data.get("sections", [])),
        }
