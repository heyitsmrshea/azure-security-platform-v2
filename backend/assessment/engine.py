"""
Assessment Engine - Main orchestrator for point-in-time security assessments.

This module coordinates data collection, analysis, and report generation
for customer security assessments.
"""
import asyncio
import json
import shutil
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional
import structlog

from ..services.graph_client import GraphClient
from ..services.azure_client import AzureResourceClient
from ..collectors.secure_score import SecureScoreCollector
from ..collectors.identity import IdentityCollector
from ..collectors.devices import DeviceCollector
from ..collectors.backup import BackupCollector
from ..collectors.threats import ThreatCollector
from ..compliance.mapper import ComplianceMapper
from ..reports.branding import BrandingConfig
from ..reports.pdf_generator import PDFReportGenerator
from .grading import calculate_grade, calculate_overall_score, calculate_category_scores

logger = structlog.get_logger(__name__)


class AssessmentEngine:
    """
    Main assessment engine that orchestrates the entire assessment process.
    
    Workflow:
    1. Initialize with credentials and configuration
    2. Collect data from all sources (Graph API, Azure ARM)
    3. Analyze findings and map to compliance frameworks
    4. Generate reports (PDF, Word)
    5. Create assessment manifest
    """
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        tenant_id: str,
        customer_name: str,
        output_dir: Path,
        frameworks: list[str],
        brand_config: BrandingConfig,
        verbose: bool = False,
    ):
        """
        Initialize the assessment engine.
        
        Args:
            client_id: Azure AD app client ID
            client_secret: Azure AD app client secret
            tenant_id: Customer's tenant ID
            customer_name: Customer organization name
            output_dir: Directory for output files
            frameworks: List of compliance frameworks to assess
            brand_config: Branding configuration for reports
            verbose: Enable verbose logging
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.customer_name = customer_name
        self.output_dir = Path(output_dir)
        self.frameworks = frameworks
        self.brand_config = brand_config
        self.verbose = verbose
        
        # Assessment metadata
        self.assessment_id = str(uuid.uuid4())
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Collected data
        self.raw_data: dict = {}
        self.findings: list[dict] = []
        self.scores: dict = {}
        self.compliance_results: dict = {}
        
        # Initialize clients
        self._init_clients()
        
        # Create output directories
        self._setup_output_dirs()
        
        logger.info(
            "assessment_engine_initialized",
            assessment_id=self.assessment_id,
            tenant_id=tenant_id,
            customer=customer_name,
        )
    
    def _init_clients(self):
        """Initialize API clients."""
        # Graph client for Microsoft 365 data
        self.graph_client = GraphClient(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        
        # Azure client for resource manager data
        self.azure_client = AzureResourceClient(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        
        # Initialize collectors (without cache service for snapshot mode)
        self.collectors = {
            "secure_score": SecureScoreCollector(self.graph_client),
            "identity": IdentityCollector(self.graph_client),
            "devices": DeviceCollector(self.graph_client),
            "threats": ThreatCollector(self.graph_client),
            "backup": BackupCollector(self.azure_client),
        }
        
        # Compliance mapper
        self.compliance_mapper = ComplianceMapper(self.frameworks)
    
    def _setup_output_dirs(self):
        """Create output directory structure."""
        dirs = [
            self.output_dir / "raw_data",
            self.output_dir / "analysis",
            self.output_dir / "analysis" / "compliance",
            self.output_dir / "reports",
            self.output_dir / "evidence",
            self.output_dir / "evidence" / "screenshots",
            self.output_dir / "evidence" / "api_responses",
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
    
    async def collect_all(self):
        """
        Collect data from all sources.
        
        This runs all collectors and saves raw data to disk.
        """
        self.start_time = datetime.utcnow()
        
        print("  ├── Collecting Secure Score...")
        try:
            self.raw_data["secure_score"] = await self._collect_secure_score()
            print("  │   ✓ Secure Score collected")
        except Exception as e:
            logger.error("secure_score_collection_failed", error=str(e))
            print(f"  │   ✗ Secure Score failed: {e}")
            self.raw_data["secure_score"] = {"error": str(e)}
        
        print("  ├── Collecting Identity data...")
        try:
            self.raw_data["identity"] = await self._collect_identity()
            print("  │   ✓ Identity data collected")
        except Exception as e:
            logger.error("identity_collection_failed", error=str(e))
            print(f"  │   ✗ Identity collection failed: {e}")
            self.raw_data["identity"] = {"error": str(e)}
        
        print("  ├── Collecting Device data...")
        try:
            self.raw_data["devices"] = await self._collect_devices()
            print("  │   ✓ Device data collected")
        except Exception as e:
            logger.error("devices_collection_failed", error=str(e))
            print(f"  │   ✗ Device collection failed: {e}")
            self.raw_data["devices"] = {"error": str(e)}
        
        print("  ├── Collecting Threat data...")
        try:
            self.raw_data["threats"] = await self._collect_threats()
            print("  │   ✓ Threat data collected")
        except Exception as e:
            logger.error("threats_collection_failed", error=str(e))
            print(f"  │   ✗ Threat collection failed: {e}")
            self.raw_data["threats"] = {"error": str(e)}
        
        print("  └── Collecting Backup data...")
        try:
            self.raw_data["backup"] = await self._collect_backup()
            print("      ✓ Backup data collected")
        except Exception as e:
            logger.error("backup_collection_failed", error=str(e))
            print(f"      ✗ Backup collection failed: {e}")
            self.raw_data["backup"] = {"error": str(e)}
        
        # Save raw data
        self._save_raw_data()
        
        self.end_time = datetime.utcnow()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info("data_collection_complete", duration_seconds=duration)
    
    async def _collect_secure_score(self) -> dict:
        """Collect Microsoft Secure Score data."""
        collector = self.collectors["secure_score"]
        
        score = await collector.collect(force_refresh=True)
        controls = await collector.get_control_scores()
        improvements = await collector.get_improvement_actions()
        
        return {
            "score": score.model_dump() if hasattr(score, "model_dump") else score,
            "controls": controls,
            "improvement_actions": improvements[:20],  # Top 20
        }
    
    async def _collect_identity(self) -> dict:
        """Collect identity and access data."""
        collector = self.collectors["identity"]
        
        mfa = await collector.collect_mfa_coverage(force_refresh=True)
        privileged = await collector.collect_privileged_accounts(force_refresh=True)
        risky = await collector.collect_risky_users(force_refresh=True)
        ca_policies = await collector.collect_conditional_access_policies()
        
        # Detailed lists for findings
        users_without_mfa = await collector.get_users_without_mfa()
        privileged_users = await collector.get_privileged_users_detail()
        risky_users_detail = await collector.get_risky_users_detail()
        
        return {
            "mfa_coverage": mfa.model_dump() if hasattr(mfa, "model_dump") else mfa,
            "privileged_accounts": privileged.model_dump() if hasattr(privileged, "model_dump") else privileged,
            "risky_users": risky.model_dump() if hasattr(risky, "model_dump") else risky,
            "conditional_access_policies": ca_policies,
            "users_without_mfa": users_without_mfa,
            "privileged_users_detail": privileged_users,
            "risky_users_detail": risky_users_detail,
        }
    
    async def _collect_devices(self) -> dict:
        """Collect device compliance data."""
        collector = self.collectors["devices"]
        
        compliance = await collector.collect_device_compliance(force_refresh=True)
        non_compliant = await collector.get_non_compliant_devices()
        
        return {
            "compliance": compliance.model_dump() if hasattr(compliance, "model_dump") else compliance,
            "non_compliant_devices": non_compliant,
        }
    
    async def _collect_threats(self) -> dict:
        """Collect threat and alert data."""
        collector = self.collectors["threats"]
        
        alerts = await collector.collect_alert_summary(force_refresh=True)
        active_alerts = await collector.get_active_alerts()
        
        return {
            "summary": alerts.model_dump() if hasattr(alerts, "model_dump") else alerts,
            "active_alerts": active_alerts,
        }
    
    async def _collect_backup(self) -> dict:
        """Collect backup health data."""
        collector = self.collectors["backup"]
        
        try:
            health = await collector.collect_backup_health(force_refresh=True)
            recovery = await collector.collect_recovery_readiness()
            jobs = await collector.get_backup_jobs()
            
            return {
                "health": health.model_dump() if hasattr(health, "model_dump") else health,
                "recovery_readiness": recovery.model_dump() if hasattr(recovery, "model_dump") else recovery,
                "recent_jobs": jobs[:50],  # Last 50 jobs
            }
        except Exception as e:
            # Backup might not be configured
            logger.warning("backup_not_available", error=str(e))
            return {
                "health": {"status": "not_configured"},
                "recovery_readiness": {"status": "not_configured"},
                "recent_jobs": [],
            }
    
    def _save_raw_data(self):
        """Save raw collected data to disk."""
        raw_dir = self.output_dir / "raw_data"
        
        for name, data in self.raw_data.items():
            file_path = raw_dir / f"{name}.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)
        
        logger.info("raw_data_saved", directory=str(raw_dir))
    
    async def analyze(self):
        """
        Analyze collected data to generate findings and scores.
        """
        print("  ├── Generating findings...")
        self.findings = self._generate_findings()
        print(f"  │   ✓ {len(self.findings)} findings generated")
        
        print("  ├── Calculating scores...")
        self.scores = self._calculate_scores()
        print(f"  │   ✓ Overall score: {self.scores['overall_score']}")
        
        print("  └── Mapping to compliance frameworks...")
        self.compliance_results = self._map_to_frameworks()
        for fw, result in self.compliance_results.items():
            print(f"      ✓ {fw}: {result.get('score', 0):.1f}%")
        
        # Save analysis results
        self._save_analysis()
    
    def _generate_findings(self) -> list[dict]:
        """Generate findings from collected data."""
        findings = []
        
        # Identity findings
        identity_data = self.raw_data.get("identity", {})
        
        # MFA gaps
        mfa = identity_data.get("mfa_coverage", {})
        if mfa.get("admin_coverage_percent", 100) < 100:
            findings.append({
                "id": f"MFA-001-{self.assessment_id[:8]}",
                "title": "Administrators Without MFA",
                "description": f"{mfa.get('total_admins', 0) - mfa.get('admins_with_mfa', 0)} administrator accounts do not have MFA enabled",
                "severity": "critical",
                "category": "identity",
                "framework_controls": ["CIS 1.1.2", "NIST IA-2", "SOC2 CC6.1"],
                "recommendation": "Enable MFA for all administrator accounts immediately",
                "affected_resources": identity_data.get("users_without_mfa", [])[:10],
            })
        
        if mfa.get("user_coverage_percent", 100) < 95:
            severity = "critical" if mfa.get("user_coverage_percent", 100) < 80 else "high"
            findings.append({
                "id": f"MFA-002-{self.assessment_id[:8]}",
                "title": "Users Without MFA",
                "description": f"Only {mfa.get('user_coverage_percent', 0):.1f}% of users have MFA enabled",
                "severity": severity,
                "category": "identity",
                "framework_controls": ["CIS 1.1.1", "NIST IA-2", "SOC2 CC6.1"],
                "recommendation": "Enable Security Defaults or Conditional Access policies requiring MFA",
                "affected_count": mfa.get("total_users", 0) - mfa.get("users_with_mfa", 0),
            })
        
        # Privileged accounts
        priv = identity_data.get("privileged_accounts", {})
        if priv.get("global_admin_count", 0) > 5:
            findings.append({
                "id": f"PRIV-001-{self.assessment_id[:8]}",
                "title": "Excessive Global Administrators",
                "description": f"{priv.get('global_admin_count', 0)} Global Administrator accounts exist (recommended: 2-4)",
                "severity": "high",
                "category": "identity",
                "framework_controls": ["CIS 1.1.3", "NIST AC-6", "SOC2 CC6.3"],
                "recommendation": "Reduce Global Admin count and use PIM for just-in-time access",
                "affected_resources": identity_data.get("privileged_users_detail", []),
            })
        
        # Risky users
        risky = identity_data.get("risky_users", {})
        if risky.get("high_risk_count", 0) > 0:
            findings.append({
                "id": f"RISK-001-{self.assessment_id[:8]}",
                "title": "High-Risk Users Detected",
                "description": f"{risky.get('high_risk_count', 0)} users flagged as high risk by Identity Protection",
                "severity": "critical",
                "category": "identity",
                "framework_controls": ["NIST IA-5", "SOC2 CC6.1"],
                "recommendation": "Investigate and remediate high-risk user accounts immediately",
                "affected_resources": identity_data.get("risky_users_detail", []),
            })
        
        # Device findings
        device_data = self.raw_data.get("devices", {})
        compliance = device_data.get("compliance", {})
        
        if compliance.get("compliance_percent", 100) < 90:
            severity = "critical" if compliance.get("compliance_percent", 100) < 70 else "high"
            findings.append({
                "id": f"DEV-001-{self.assessment_id[:8]}",
                "title": "Non-Compliant Devices",
                "description": f"{compliance.get('non_compliant_count', 0)} devices are non-compliant with security policies",
                "severity": severity,
                "category": "devices",
                "framework_controls": ["CIS 3.1", "NIST CM-2", "SOC2 CC6.6"],
                "recommendation": "Review and remediate non-compliant devices",
                "affected_resources": device_data.get("non_compliant_devices", [])[:20],
            })
        
        # Backup findings
        backup_data = self.raw_data.get("backup", {})
        health = backup_data.get("health", {})
        
        if health.get("status") == "not_configured":
            findings.append({
                "id": f"BKP-001-{self.assessment_id[:8]}",
                "title": "Azure Backup Not Configured",
                "description": "No Azure Backup vaults detected - critical for ransomware recovery",
                "severity": "critical",
                "category": "backup",
                "framework_controls": ["NIST CP-9", "SOC2 A1.2"],
                "recommendation": "Implement Azure Backup for critical systems",
            })
        elif health.get("protected_percent", 100) < 90:
            findings.append({
                "id": f"BKP-002-{self.assessment_id[:8]}",
                "title": "Incomplete Backup Coverage",
                "description": f"Only {health.get('protected_percent', 0):.1f}% of critical systems are backed up",
                "severity": "high",
                "category": "backup",
                "framework_controls": ["NIST CP-9", "SOC2 A1.2"],
                "recommendation": "Extend backup coverage to all critical systems",
            })
        
        # Threat findings
        threat_data = self.raw_data.get("threats", {})
        summary = threat_data.get("summary", {})
        
        if summary.get("critical_count", 0) > 0:
            findings.append({
                "id": f"THR-001-{self.assessment_id[:8]}",
                "title": "Critical Security Alerts",
                "description": f"{summary.get('critical_count', 0)} critical security alerts require immediate attention",
                "severity": "critical",
                "category": "threats",
                "framework_controls": ["NIST IR-4", "SOC2 CC7.3"],
                "recommendation": "Investigate and respond to critical alerts immediately",
                "affected_resources": threat_data.get("active_alerts", [])[:10],
            })
        
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}
        findings.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 4))
        
        return findings
    
    def _calculate_scores(self) -> dict:
        """Calculate all scores."""
        # Get secure score from collected data
        secure_score_data = self.raw_data.get("secure_score", {}).get("score", {})
        secure_score = secure_score_data.get("current_score", 50)
        
        # Calculate category scores
        category_scores = calculate_category_scores(self.raw_data)
        
        # Calculate overall score
        overall_score = calculate_overall_score(
            secure_score=secure_score,
            category_scores=category_scores,
        )
        
        # Calculate grade
        overall_grade = calculate_grade(overall_score)
        
        return {
            "overall_grade": overall_grade,
            "overall_score": round(overall_score, 1),
            "secure_score": round(secure_score, 1),
            "categories": category_scores,
        }
    
    def _map_to_frameworks(self) -> dict:
        """Map findings to compliance frameworks."""
        results = {}
        
        for framework in self.frameworks:
            result = self.compliance_mapper.map_to_framework(
                framework=framework,
                findings=self.findings,
                raw_data=self.raw_data,
            )
            results[framework] = result
            self.scores.setdefault("compliance", {})[framework] = result.get("score", 0)
        
        return results
    
    def _save_analysis(self):
        """Save analysis results to disk."""
        analysis_dir = self.output_dir / "analysis"
        
        # Save findings
        findings_path = analysis_dir / "findings.json"
        with open(findings_path, "w") as f:
            json.dump(self.findings, f, indent=2, default=str)
        
        # Save scores
        scores_path = analysis_dir / "scores.json"
        with open(scores_path, "w") as f:
            json.dump(self.scores, f, indent=2)
        
        # Save compliance results
        compliance_dir = analysis_dir / "compliance"
        for framework, result in self.compliance_results.items():
            framework_path = compliance_dir / f"{framework.replace(' ', '_').lower()}.json"
            with open(framework_path, "w") as f:
                json.dump(result, f, indent=2, default=str)
        
        logger.info("analysis_saved", directory=str(analysis_dir))
    
    async def generate_reports(self):
        """Generate PDF reports."""
        reports_dir = self.output_dir / "reports"
        
        generator = PDFReportGenerator(brand_config=self.brand_config)
        
        print("  ├── Executive Summary...")
        exec_pdf = generator.generate_executive_summary(
            customer_name=self.customer_name,
            assessment_date=self.start_time,
            scores=self.scores,
            findings=self.findings,
            compliance_results=self.compliance_results,
        )
        exec_path = reports_dir / "executive_summary.pdf"
        with open(exec_path, "wb") as f:
            f.write(exec_pdf)
        print("  │   ✓ Executive Summary generated")
        
        print("  ├── Technical Findings...")
        tech_pdf = generator.generate_technical_report(
            customer_name=self.customer_name,
            assessment_date=self.start_time,
            findings=self.findings,
            raw_data=self.raw_data,
        )
        tech_path = reports_dir / "technical_findings.pdf"
        with open(tech_path, "wb") as f:
            f.write(tech_pdf)
        print("  │   ✓ Technical Findings generated")
        
        print("  └── Compliance Report...")
        compliance_pdf = generator.generate_compliance_report(
            customer_name=self.customer_name,
            assessment_date=self.start_time,
            compliance_results=self.compliance_results,
            findings=self.findings,
        )
        compliance_path = reports_dir / "compliance_report.pdf"
        with open(compliance_path, "wb") as f:
            f.write(compliance_pdf)
        print("      ✓ Compliance Report generated")
        
        logger.info("reports_generated", directory=str(reports_dir))
    
    def cleanup_raw_data(self):
        """Remove raw data files (for privacy)."""
        raw_dir = self.output_dir / "raw_data"
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
            logger.info("raw_data_deleted", directory=str(raw_dir))
    
    def get_manifest(self) -> dict:
        """Generate assessment manifest."""
        duration = 0
        if self.start_time and self.end_time:
            duration = int((self.end_time - self.start_time).total_seconds())
        
        # Count findings by severity
        finding_counts = {
            "critical": len([f for f in self.findings if f.get("severity") == "critical"]),
            "high": len([f for f in self.findings if f.get("severity") == "high"]),
            "medium": len([f for f in self.findings if f.get("severity") == "medium"]),
            "low": len([f for f in self.findings if f.get("severity") == "low"]),
            "informational": len([f for f in self.findings if f.get("severity") == "informational"]),
        }
        
        # Get primary domain from identity data
        primary_domain = f"{self.tenant_id[:8]}...onmicrosoft.com"
        
        return {
            "assessment_id": self.assessment_id,
            "version": "2.0.0",
            "customer": {
                "name": self.customer_name,
                "tenant_id": self.tenant_id,
                "primary_domain": primary_domain,
            },
            "assessment": {
                "date": self.start_time.isoformat() if self.start_time else datetime.utcnow().isoformat(),
                "duration_seconds": duration,
                "assessor": self.brand_config.company_name,
                "type": "point_in_time",
                "frameworks": self.frameworks,
            },
            "scores": self.scores,
            "findings": finding_counts,
            "branding": {
                "company": self.brand_config.company_name,
                "logo": self.brand_config.logo_path,
            },
        }
