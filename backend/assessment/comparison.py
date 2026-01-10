"""
Comparison Engine for Assessment Deltas

Compares current assessment with a previous assessment to show
improvement, regression, and remediation progress.
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class ComparisonEngine:
    """
    Compare two assessments to generate delta reports.
    
    Shows:
    - Score changes (overall and by category)
    - Findings resolved vs. new findings
    - Compliance improvements
    - Trend analysis
    """
    
    def __init__(
        self,
        current_dir: Path,
        previous_dir: Path,
    ):
        """
        Initialize comparison engine.
        
        Args:
            current_dir: Path to current assessment
            previous_dir: Path to previous assessment
        """
        self.current_dir = Path(current_dir)
        self.previous_dir = Path(previous_dir)
        
        self.current_manifest: dict = {}
        self.previous_manifest: dict = {}
        self.current_findings: list = []
        self.previous_findings: list = []
        
        self._load_assessments()
    
    def _load_assessments(self):
        """Load assessment data from both directories."""
        # Load current assessment
        current_manifest_path = self.current_dir / "manifest.json"
        current_findings_path = self.current_dir / "analysis" / "findings.json"
        
        if current_manifest_path.exists():
            with open(current_manifest_path) as f:
                self.current_manifest = json.load(f)
        
        if current_findings_path.exists():
            with open(current_findings_path) as f:
                self.current_findings = json.load(f)
        
        # Load previous assessment
        previous_manifest_path = self.previous_dir / "manifest.json"
        previous_findings_path = self.previous_dir / "analysis" / "findings.json"
        
        if not previous_manifest_path.exists():
            raise FileNotFoundError(f"Previous assessment manifest not found: {previous_manifest_path}")
        
        with open(previous_manifest_path) as f:
            self.previous_manifest = json.load(f)
        
        if previous_findings_path.exists():
            with open(previous_findings_path) as f:
                self.previous_findings = json.load(f)
        
        logger.info(
            "assessments_loaded",
            current_date=self.current_manifest.get("assessment", {}).get("date"),
            previous_date=self.previous_manifest.get("assessment", {}).get("date"),
        )
    
    async def generate_comparison(self) -> dict:
        """
        Generate comprehensive comparison between assessments.
        
        Returns:
            Comparison data dictionary
        """
        comparison = {
            "meta": self._generate_meta(),
            "score_comparison": self._compare_scores(),
            "findings_comparison": self._compare_findings(),
            "compliance_comparison": self._compare_compliance(),
            "summary": {},
        }
        
        # Generate summary
        comparison["summary"] = self._generate_summary(comparison)
        
        # Save comparison
        self._save_comparison(comparison)
        
        return comparison
    
    def _generate_meta(self) -> dict:
        """Generate comparison metadata."""
        current_date = self.current_manifest.get("assessment", {}).get("date", "")
        previous_date = self.previous_manifest.get("assessment", {}).get("date", "")
        
        # Calculate days between assessments
        days_between = 0
        try:
            current_dt = datetime.fromisoformat(current_date.replace("Z", "+00:00"))
            previous_dt = datetime.fromisoformat(previous_date.replace("Z", "+00:00"))
            days_between = (current_dt - previous_dt).days
        except (ValueError, TypeError):
            pass
        
        return {
            "current_assessment": {
                "id": self.current_manifest.get("assessment_id"),
                "date": current_date,
                "customer": self.current_manifest.get("customer", {}).get("name"),
            },
            "previous_assessment": {
                "id": self.previous_manifest.get("assessment_id"),
                "date": previous_date,
                "customer": self.previous_manifest.get("customer", {}).get("name"),
            },
            "days_between": days_between,
            "comparison_generated": datetime.utcnow().isoformat(),
        }
    
    def _compare_scores(self) -> dict:
        """Compare scores between assessments."""
        current_scores = self.current_manifest.get("scores", {})
        previous_scores = self.previous_manifest.get("scores", {})
        
        def score_diff(current: float, previous: float) -> dict:
            change = current - previous
            change_percent = (change / previous * 100) if previous > 0 else 0
            direction = "improved" if change > 0 else "declined" if change < 0 else "unchanged"
            return {
                "current": current,
                "previous": previous,
                "change": round(change, 1),
                "change_percent": round(change_percent, 1),
                "direction": direction,
            }
        
        comparison = {
            "overall": score_diff(
                current_scores.get("overall_score", 0),
                previous_scores.get("overall_score", 0),
            ),
            "grade": {
                "current": current_scores.get("overall_grade", "?"),
                "previous": previous_scores.get("overall_grade", "?"),
            },
            "secure_score": score_diff(
                current_scores.get("secure_score", 0),
                previous_scores.get("secure_score", 0),
            ),
            "categories": {},
            "compliance": {},
        }
        
        # Category comparisons
        current_categories = current_scores.get("categories", {})
        previous_categories = previous_scores.get("categories", {})
        
        for category in set(current_categories.keys()) | set(previous_categories.keys()):
            comparison["categories"][category] = score_diff(
                current_categories.get(category, 0),
                previous_categories.get(category, 0),
            )
        
        # Compliance comparisons
        current_compliance = current_scores.get("compliance", {})
        previous_compliance = previous_scores.get("compliance", {})
        
        for framework in set(current_compliance.keys()) | set(previous_compliance.keys()):
            comparison["compliance"][framework] = score_diff(
                current_compliance.get(framework, 0),
                previous_compliance.get(framework, 0),
            )
        
        return comparison
    
    def _compare_findings(self) -> dict:
        """
        Compare findings between assessments.
        
        Identifies:
        - Resolved findings (in previous, not in current)
        - New findings (in current, not in previous)
        - Persistent findings (in both)
        """
        # Create lookup by finding "signature" (title + category)
        def finding_signature(f: dict) -> str:
            return f"{f.get('title', '')}|{f.get('category', '')}"
        
        current_sigs = {finding_signature(f): f for f in self.current_findings}
        previous_sigs = {finding_signature(f): f for f in self.previous_findings}
        
        # Resolved = in previous but not in current
        resolved = []
        for sig, finding in previous_sigs.items():
            if sig not in current_sigs:
                resolved.append({
                    "title": finding.get("title"),
                    "severity": finding.get("severity"),
                    "category": finding.get("category"),
                })
        
        # New = in current but not in previous
        new_findings = []
        for sig, finding in current_sigs.items():
            if sig not in previous_sigs:
                new_findings.append({
                    "title": finding.get("title"),
                    "severity": finding.get("severity"),
                    "category": finding.get("category"),
                    "recommendation": finding.get("recommendation"),
                })
        
        # Persistent = in both
        persistent = []
        for sig, finding in current_sigs.items():
            if sig in previous_sigs:
                persistent.append({
                    "title": finding.get("title"),
                    "severity": finding.get("severity"),
                    "category": finding.get("category"),
                    "days_open": self._calculate_days_open(previous_sigs[sig]),
                })
        
        # Count by severity
        def count_by_severity(findings: list) -> dict:
            counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for f in findings:
                sev = f.get("severity", "low")
                if sev in counts:
                    counts[sev] += 1
            return counts
        
        return {
            "summary": {
                "resolved_count": len(resolved),
                "new_count": len(new_findings),
                "persistent_count": len(persistent),
                "net_change": len(resolved) - len(new_findings),
            },
            "resolved": {
                "count": len(resolved),
                "by_severity": count_by_severity(resolved),
                "findings": resolved,
            },
            "new": {
                "count": len(new_findings),
                "by_severity": count_by_severity(new_findings),
                "findings": new_findings,
            },
            "persistent": {
                "count": len(persistent),
                "by_severity": count_by_severity(persistent),
                "findings": persistent,
            },
        }
    
    def _calculate_days_open(self, finding: dict) -> int:
        """Calculate how many days a finding has been open."""
        # In a real implementation, we'd track finding creation dates
        # For now, use days between assessments as an estimate
        try:
            current_date = self.current_manifest.get("assessment", {}).get("date", "")
            previous_date = self.previous_manifest.get("assessment", {}).get("date", "")
            current_dt = datetime.fromisoformat(current_date.replace("Z", "+00:00"))
            previous_dt = datetime.fromisoformat(previous_date.replace("Z", "+00:00"))
            return (current_dt - previous_dt).days
        except (ValueError, TypeError):
            return 0
    
    def _compare_compliance(self) -> dict:
        """Compare compliance framework scores."""
        current_scores = self.current_manifest.get("scores", {}).get("compliance", {})
        previous_scores = self.previous_manifest.get("scores", {}).get("compliance", {})
        
        comparison = {}
        for framework in set(current_scores.keys()) | set(previous_scores.keys()):
            current = current_scores.get(framework, 0)
            previous = previous_scores.get(framework, 0)
            change = current - previous
            
            comparison[framework] = {
                "current": current,
                "previous": previous,
                "change": round(change, 1),
                "direction": "improved" if change > 0 else "declined" if change < 0 else "unchanged",
            }
        
        return comparison
    
    def _generate_summary(self, comparison: dict) -> dict:
        """Generate executive summary of comparison."""
        score_comp = comparison.get("score_comparison", {})
        findings_comp = comparison.get("findings_comparison", {})
        
        overall = score_comp.get("overall", {})
        findings_summary = findings_comp.get("summary", {})
        
        # Determine overall trend
        score_change = overall.get("change", 0)
        findings_change = findings_summary.get("net_change", 0)
        
        if score_change > 5 and findings_change > 0:
            trend = "significant_improvement"
            trend_description = "Significant security improvement observed"
        elif score_change > 0 or findings_change > 0:
            trend = "improvement"
            trend_description = "Security posture has improved"
        elif score_change < -5 or findings_change < -3:
            trend = "regression"
            trend_description = "Security posture has declined"
        else:
            trend = "stable"
            trend_description = "Security posture remains stable"
        
        # Key highlights
        highlights = []
        
        # Score change
        if overall.get("change", 0) != 0:
            direction = "improved" if overall.get("change", 0) > 0 else "declined"
            highlights.append(
                f"Overall score {direction} by {abs(overall.get('change', 0)):.1f} points"
            )
        
        # Findings resolved
        if findings_summary.get("resolved_count", 0) > 0:
            highlights.append(
                f"{findings_summary.get('resolved_count')} security findings resolved"
            )
        
        # New critical findings
        new_critical = findings_comp.get("new", {}).get("by_severity", {}).get("critical", 0)
        if new_critical > 0:
            highlights.append(
                f"⚠️ {new_critical} new critical findings introduced"
            )
        
        # Grade change
        current_grade = score_comp.get("grade", {}).get("current", "?")
        previous_grade = score_comp.get("grade", {}).get("previous", "?")
        if current_grade != previous_grade:
            highlights.append(f"Grade changed from {previous_grade} to {current_grade}")
        
        return {
            "trend": trend,
            "trend_description": trend_description,
            "score_change": overall.get("change", 0),
            "findings_resolved": findings_summary.get("resolved_count", 0),
            "new_findings": findings_summary.get("new_count", 0),
            "highlights": highlights,
        }
    
    def _save_comparison(self, comparison: dict):
        """Save comparison results."""
        comparison_path = self.current_dir / "analysis" / "comparison.json"
        with open(comparison_path, "w") as f:
            json.dump(comparison, f, indent=2, default=str)
        
        logger.info("comparison_saved", path=str(comparison_path))
