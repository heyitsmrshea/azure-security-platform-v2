"""
Accountability Collector for Azure Security Platform V2

Calculates IT accountability metrics from historical data.
"""
from datetime import datetime, timedelta
from typing import Optional
import structlog

from ..services.cosmos_service import CosmosService
from ..services.cache_service import CacheService
from ..models.schemas import (
    PatchSLACompliance,
    FindingAgeDistribution,
    MTTR,
)

logger = structlog.get_logger(__name__)


class AccountabilityCollector:
    """
    Calculates IT accountability metrics.
    
    Features:
    - Patch SLA compliance
    - Finding age distribution
    - Mean Time to Remediate (MTTR)
    - Historical trend analysis
    """
    
    # Default SLA targets (configurable per tenant)
    DEFAULT_SLA = {
        "critical": 7,   # 7 days for critical
        "high": 14,      # 14 days for high
        "medium": 30,    # 30 days for medium
        "low": 90,       # 90 days for low
    }
    
    def __init__(
        self,
        cosmos_service: CosmosService,
        cache_service: Optional[CacheService] = None,
        tenant_id: str = "",
    ):
        self._cosmos = cosmos_service
        self._cache = cache_service
        self._tenant_id = tenant_id
        
        logger.info("accountability_collector_initialized", tenant_id=tenant_id)
    
    async def collect_patch_sla_compliance(
        self,
        target_percent: float = 95.0,
        force_refresh: bool = False,
    ) -> PatchSLACompliance:
        """
        Calculate patch SLA compliance.
        
        Measures what percentage of vulnerabilities/findings
        are remediated within the SLA window.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "patch_sla")
            if cached:
                return PatchSLACompliance(**cached)
        
        # Query findings from CosmosDB
        findings = await self._get_recent_findings(days=90)
        
        in_sla = 0
        out_of_sla = 0
        
        for finding in findings:
            severity = finding.get("severity", "medium").lower()
            sla_days = self.DEFAULT_SLA.get(severity, 30)
            
            created = finding.get("created_at")
            resolved = finding.get("resolved_at")
            status = finding.get("status", "open")
            
            if status == "resolved" and resolved and created:
                try:
                    created_dt = datetime.fromisoformat(str(created).replace("Z", ""))
                    resolved_dt = datetime.fromisoformat(str(resolved).replace("Z", ""))
                    resolution_days = (resolved_dt - created_dt).days
                    
                    if resolution_days <= sla_days:
                        in_sla += 1
                    else:
                        out_of_sla += 1
                except:
                    pass
            elif status == "open" and created:
                # Check if still within SLA window
                try:
                    created_dt = datetime.fromisoformat(str(created).replace("Z", ""))
                    age_days = (datetime.utcnow() - created_dt).days
                    
                    if age_days <= sla_days:
                        in_sla += 1
                    else:
                        out_of_sla += 1
                except:
                    pass
        
        total = in_sla + out_of_sla
        compliance_percent = (in_sla / total * 100) if total > 0 else 100
        
        sla = PatchSLACompliance(
            compliance_percent=round(compliance_percent, 1),
            target_percent=target_percent,
            patches_in_sla=in_sla,
            patches_total=total,
            critical_sla_days=self.DEFAULT_SLA["critical"],
            high_sla_days=self.DEFAULT_SLA["high"],
            medium_sla_days=self.DEFAULT_SLA["medium"],
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "patch_sla", sla.model_dump())
        
        logger.info(
            "patch_sla_collected",
            tenant_id=self._tenant_id,
            compliance=compliance_percent,
            in_sla=in_sla,
            total=total,
        )
        
        return sla
    
    async def collect_finding_age_distribution(
        self,
        force_refresh: bool = False,
    ) -> FindingAgeDistribution:
        """
        Calculate open finding age distribution.
        
        Buckets: 0-7 days, 7-30 days, 30-90 days, 90+ days
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "finding_age")
            if cached:
                return FindingAgeDistribution(**cached)
        
        # Get from CosmosDB if available
        if self._cosmos:
            distribution = await self._cosmos.get_finding_age_distribution(self._tenant_id)
        else:
            # Calculate from recent findings
            findings = await self._get_open_findings()
            distribution = self._calculate_age_distribution(findings)
        
        age_dist = FindingAgeDistribution(
            age_0_7=distribution.get("age_0_7", 0),
            age_7_30=distribution.get("age_7_30", 0),
            age_30_90=distribution.get("age_30_90", 0),
            age_90_plus=distribution.get("age_90_plus", 0),
            total_open=distribution.get("total_open", 0),
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "finding_age", age_dist.model_dump())
        
        logger.info(
            "finding_age_collected",
            tenant_id=self._tenant_id,
            total_open=age_dist.total_open,
            age_90_plus=age_dist.age_90_plus,
        )
        
        return age_dist
    
    async def collect_mttr(
        self,
        days: int = 30,
        force_refresh: bool = False,
    ) -> MTTR:
        """
        Calculate Mean Time to Remediate.
        
        Calculates average days from finding creation to resolution.
        """
        # Check cache
        if not force_refresh and self._cache:
            cached = await self._cache.get(self._tenant_id, "mttr")
            if cached:
                return MTTR(**cached)
        
        # Get from CosmosDB if available
        if self._cosmos:
            mttr_data = await self._cosmos.calculate_mttr(self._tenant_id, days)
        else:
            mttr_data = await self._calculate_mttr_from_findings(days)
        
        mttr = MTTR(
            mttr_days=round(mttr_data.get("mttr_days", 0), 1),
            critical_mttr_days=round(mttr_data.get("critical_mttr_days", 0), 1),
            high_mttr_days=round(mttr_data.get("high_mttr_days", 0), 1),
            findings_resolved_count=mttr_data.get("findings_resolved_count", 0),
            period=f"{days}d",
            last_updated=datetime.utcnow(),
        )
        
        # Cache result
        if self._cache:
            await self._cache.set(self._tenant_id, "mttr", mttr.model_dump())
        
        logger.info(
            "mttr_collected",
            tenant_id=self._tenant_id,
            mttr_days=mttr.mttr_days,
            resolved_count=mttr.findings_resolved_count,
        )
        
        return mttr
    
    async def get_accountability_dashboard(self) -> dict:
        """
        Get all accountability metrics for dashboard.
        """
        patch_sla = await self.collect_patch_sla_compliance()
        finding_age = await self.collect_finding_age_distribution()
        mttr = await self.collect_mttr()
        
        # Calculate overall accountability score
        score = self._calculate_accountability_score(patch_sla, finding_age, mttr)
        
        return {
            "patch_sla": patch_sla.model_dump(),
            "finding_age": finding_age.model_dump(),
            "mttr": mttr.model_dump(),
            "accountability_score": score,
            "last_updated": datetime.utcnow().isoformat(),
        }
    
    async def get_remediation_velocity(self, days: int = 30) -> dict:
        """
        Calculate remediation velocity trends.
        
        Shows how quickly the team is resolving findings over time.
        """
        findings = await self._get_recent_findings(days)
        
        # Group by week
        weekly_resolved = {}
        weekly_created = {}
        
        for finding in findings:
            created = finding.get("created_at")
            resolved = finding.get("resolved_at")
            
            if created:
                try:
                    created_dt = datetime.fromisoformat(str(created).replace("Z", ""))
                    week_key = created_dt.strftime("%Y-W%W")
                    weekly_created[week_key] = weekly_created.get(week_key, 0) + 1
                except:
                    pass
            
            if resolved:
                try:
                    resolved_dt = datetime.fromisoformat(str(resolved).replace("Z", ""))
                    week_key = resolved_dt.strftime("%Y-W%W")
                    weekly_resolved[week_key] = weekly_resolved.get(week_key, 0) + 1
                except:
                    pass
        
        # Calculate velocity (resolved - created per week)
        all_weeks = sorted(set(weekly_created.keys()) | set(weekly_resolved.keys()))
        velocity = []
        
        for week in all_weeks:
            created = weekly_created.get(week, 0)
            resolved = weekly_resolved.get(week, 0)
            velocity.append({
                "week": week,
                "created": created,
                "resolved": resolved,
                "net": resolved - created,
            })
        
        return {
            "weekly_data": velocity,
            "total_created": sum(weekly_created.values()),
            "total_resolved": sum(weekly_resolved.values()),
            "net_change": sum(weekly_resolved.values()) - sum(weekly_created.values()),
        }
    
    async def _get_recent_findings(self, days: int) -> list[dict]:
        """Get recent findings from CosmosDB."""
        if self._cosmos:
            query = """
            SELECT * FROM c
            WHERE c.tenantId = @tenantId
            ORDER BY c.created_at DESC
            """
            return await self._cosmos.query_items(
                "findings",
                query,
                [{"name": "@tenantId", "value": self._tenant_id}],
                partition_key=self._tenant_id,
            )
        return []
    
    async def _get_open_findings(self) -> list[dict]:
        """Get open findings from CosmosDB."""
        if self._cosmos:
            return await self._cosmos.get_open_findings(self._tenant_id)
        return []
    
    def _calculate_age_distribution(self, findings: list[dict]) -> dict:
        """Calculate age distribution from findings list."""
        now = datetime.utcnow()
        distribution = {
            "age_0_7": 0,
            "age_7_30": 0,
            "age_30_90": 0,
            "age_90_plus": 0,
        }
        
        for finding in findings:
            if finding.get("status") != "open":
                continue
            
            created = finding.get("created_at")
            if not created:
                continue
            
            try:
                created_dt = datetime.fromisoformat(str(created).replace("Z", ""))
                age_days = (now - created_dt).days
                
                if age_days <= 7:
                    distribution["age_0_7"] += 1
                elif age_days <= 30:
                    distribution["age_7_30"] += 1
                elif age_days <= 90:
                    distribution["age_30_90"] += 1
                else:
                    distribution["age_90_plus"] += 1
            except:
                pass
        
        distribution["total_open"] = sum(distribution.values())
        return distribution
    
    async def _calculate_mttr_from_findings(self, days: int) -> dict:
        """Calculate MTTR from findings."""
        findings = await self._get_recent_findings(days)
        
        total_days = 0
        critical_days = 0
        high_days = 0
        total_count = 0
        critical_count = 0
        high_count = 0
        
        for finding in findings:
            if finding.get("status") != "resolved":
                continue
            
            created = finding.get("created_at")
            resolved = finding.get("resolved_at")
            
            if not created or not resolved:
                continue
            
            try:
                created_dt = datetime.fromisoformat(str(created).replace("Z", ""))
                resolved_dt = datetime.fromisoformat(str(resolved).replace("Z", ""))
                resolution_days = (resolved_dt - created_dt).days
                
                total_days += resolution_days
                total_count += 1
                
                severity = finding.get("severity", "").lower()
                if severity == "critical":
                    critical_days += resolution_days
                    critical_count += 1
                elif severity == "high":
                    high_days += resolution_days
                    high_count += 1
            except:
                pass
        
        return {
            "mttr_days": total_days / total_count if total_count else 0,
            "critical_mttr_days": critical_days / critical_count if critical_count else 0,
            "high_mttr_days": high_days / high_count if high_count else 0,
            "findings_resolved_count": total_count,
        }
    
    def _calculate_accountability_score(
        self,
        patch_sla: PatchSLACompliance,
        finding_age: FindingAgeDistribution,
        mttr: MTTR,
    ) -> dict:
        """Calculate overall accountability score."""
        score = 0
        
        # SLA compliance (40% weight)
        sla_score = min(patch_sla.compliance_percent / patch_sla.target_percent * 100, 100)
        score += sla_score * 0.4
        
        # Finding age (30% weight) - penalize old findings
        if finding_age.total_open > 0:
            old_ratio = finding_age.age_90_plus / finding_age.total_open
            age_score = (1 - old_ratio) * 100
        else:
            age_score = 100
        score += age_score * 0.3
        
        # MTTR (30% weight) - lower is better
        if mttr.mttr_days <= 7:
            mttr_score = 100
        elif mttr.mttr_days <= 14:
            mttr_score = 80
        elif mttr.mttr_days <= 30:
            mttr_score = 60
        else:
            mttr_score = max(40 - (mttr.mttr_days - 30), 0)
        score += mttr_score * 0.3
        
        if score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "score": round(score, 1),
            "grade": grade,
            "components": {
                "sla_score": round(sla_score, 1),
                "age_score": round(age_score, 1),
                "mttr_score": round(mttr_score, 1),
            },
        }
